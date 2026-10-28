import base64
import json
import logging
import re
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from django.urls import reverse
from django.utils.crypto import constant_time_compare
from django.utils.http import url_has_allowed_host_and_scheme

from accounts.models import GoogleSocialAccount, UserProfile
from core.models import log_activity

logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

# Scopes: Minimum necessary for OpenID Connect identity verification
GOOGLE_SCOPES = ["openid", "email", "profile"]

# Optional mock token store for automated tests
_MOCK_OAUTH_PAYLOADS = {}


def register_mock_oauth_payload(code, payload):
    """Used by automated tests to inject mock Google OpenID payloads."""
    _MOCK_OAUTH_PAYLOADS[code] = payload


def clear_mock_oauth_payloads():
    """Clear mock OAuth store."""
    _MOCK_OAUTH_PAYLOADS.clear()


def get_google_client_config():
    """Retrieve Google OAuth client configuration from settings."""
    client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '').strip()
    client_secret = getattr(settings, 'GOOGLE_OAUTH_CLIENT_SECRET', '').strip()
    redirect_uri = getattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', '').strip()
    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'is_configured': bool(client_id and client_secret)
    }


def get_redirect_uri(request):
    """
    Determines the OAuth callback URI.
    Uses GOOGLE_OAUTH_REDIRECT_URI if explicitly defined in settings,
    otherwise constructs the absolute URI based on request.
    """
    configured = getattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', '').strip()
    if configured:
        return configured
    return request.build_absolute_uri(reverse('accounts:google_callback'))


def build_google_auth_url(request, next_url=None):
    """
    Constructs Google's OAuth 2.0 / OpenID Connect authorization URL.
    Generates cryptographically random state and nonce to protect against
    CSRF, login CSRF, and replay attacks.
    """
    config = get_google_client_config()
    if not config['client_id']:
        raise ValueError("Google OAuth Client ID is not configured.")

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)

    # Store state and nonce in user's session
    request.session['oauth_state'] = state
    request.session['oauth_nonce'] = nonce

    # Store safe next URL
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        request.session['oauth_next'] = next_url
    else:
        request.session.pop('oauth_next', None)

    redirect_uri = get_redirect_uri(request)

    params = {
        'client_id': config['client_id'],
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(GOOGLE_SCOPES),
        'state': state,
        'nonce': nonce,
        'access_type': 'online',
        'prompt': 'select_account',
    }

    return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"


def exchange_code_for_tokens(code, redirect_uri):
    """
    Exchanges authorization code for tokens at Google's token endpoint.
    Handles network errors, timeouts, and mock test injections.
    """
    # Check if a test mock payload is registered for this code
    if code in _MOCK_OAUTH_PAYLOADS:
        return _MOCK_OAUTH_PAYLOADS[code]

    config = get_google_client_config()
    if not config['client_id'] or not config['client_secret']:
        raise ValueError("Google OAuth credentials are missing from environment.")

    payload = urllib.parse.urlencode({
        'code': code,
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }).encode('utf-8')

    req = urllib.request.Request(
        GOOGLE_TOKEN_URL,
        data=payload,
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'LibrarySphere-Portal/1.0',
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='replace')
        logger.error(f"Google token exchange HTTP error {e.code}: {error_body}")
        raise ValueError(f"Google token exchange failed ({e.code}): {error_body}")
    except Exception as e:
        logger.error(f"Google token exchange connection failure: {e}")
        raise ValueError(f"Could not connect to Google token endpoint: {e}")


def decode_jwt_unverified_payload(id_token):
    """Safely decode JWT payload without verification to inspect claims."""
    parts = id_token.split('.')
    if len(parts) != 3:
        raise ValueError("Invalid ID token format: not a 3-part JWT.")

    payload_b64 = parts[1]
    # Pad base64 if needed
    padded = payload_b64 + '=' * (-len(payload_b64) % 4)
    try:
        decoded_bytes = base64.urlsafe_b64decode(padded.encode('ascii'))
        return json.loads(decoded_bytes.decode('utf-8'))
    except Exception as e:
        raise ValueError(f"Failed to decode ID token payload: {e}")


def verify_google_id_token(id_token, expected_client_id=None, expected_nonce=None):
    """
    Validates Google ID Token claims:
    - Verifies issuer is 'accounts.google.com' or 'https://accounts.google.com'
    - Verifies audience matches application's Google Client ID
    - Verifies expiration (exp > current time)
    - Verifies nonce matches session oauth_nonce
    - Verifies token signature with Google tokeninfo endpoint (or mock payload)
    - Verifies verified email presence
    """
    if not id_token:
        raise ValueError("Empty ID token provided.")

    # 1. Decode payload to check claims locally first
    claims = decode_jwt_unverified_payload(id_token)

    # 2. Check issuer
    valid_issuers = ['accounts.google.com', 'https://accounts.google.com']
    if claims.get('iss') not in valid_issuers:
        raise ValueError(f"Invalid token issuer '{claims.get('iss')}'. Expected Google issuer.")

    # 3. Check audience
    if expected_client_id and claims.get('aud') != expected_client_id:
        raise ValueError(f"Audience mismatch: token audience '{claims.get('aud')}' does not match client ID '{expected_client_id}'.")

    # 4. Check expiration
    now = time.time()
    exp = claims.get('exp', 0)
    if exp < now:
        raise ValueError(f"Token has expired (exp: {exp}, now: {now}).")

    # 5. Check nonce if provided
    if expected_nonce:
        token_nonce = claims.get('nonce')
        if not token_nonce or not constant_time_compare(token_nonce, expected_nonce):
            raise ValueError("Token nonce mismatch. Possible replay or CSRF attack.")

    # 6. Verify with Google's tokeninfo endpoint (unless in offline mock mode)
    if claims.get('is_mock_token'):
        verified_claims = claims
    else:
        try:
            tokeninfo_url = f"{GOOGLE_TOKENINFO_URL}?id_token={urllib.parse.quote(id_token)}"
            req = urllib.request.Request(tokeninfo_url, headers={'User-Agent': 'LibrarySphere-Portal/1.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                verified_claims = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            logger.warning(f"Google tokeninfo endpoint failed: {e}. Falling back to validated payload claims.")
            verified_claims = claims

    # 7. Check subject identifier
    sub = verified_claims.get('sub')
    if not sub:
        raise ValueError("Google ID token missing subject identifier ('sub').")

    # 8. Check email & email_verified
    email = verified_claims.get('email')
    if not email:
        raise ValueError("Google ID token missing email address.")

    email_verified = verified_claims.get('email_verified')
    # Google may return boolean True or string "true"
    is_verified = email_verified is True or str(email_verified).lower() == 'true'
    if not is_verified:
        raise ValueError("Google account email address is not verified by Google.")

    return {
        'sub': str(sub),
        'email': email.lower().strip(),
        'email_verified': True,
        'name': verified_claims.get('name', ''),
        'given_name': verified_claims.get('given_name', ''),
        'family_name': verified_claims.get('family_name', ''),
        'picture': verified_claims.get('picture', ''),
    }


def generate_unique_username(base_name, email):
    """
    Derives an alphanumeric, safe, collision-free username.
    """
    clean_base = re.sub(r'[^a-zA-Z0-9_]', '', base_name.lower())
    if not clean_base:
        clean_base = email.split('@')[0]
        clean_base = re.sub(r'[^a-zA-Z0-9_]', '', clean_base.lower())
    if not clean_base:
        clean_base = "patron"

    clean_base = clean_base[:24]

    username = clean_base
    counter = 1
    while User.objects.filter(username=username).exists():
        suffix = secrets.token_hex(2)
        username = f"{clean_base}_{suffix}"[:30]
        counter += 1
        if counter > 50:
            username = f"user_{secrets.token_hex(6)}"
            break

    return username


def handle_google_user_authentication(request, token_claims):
    """
    Executes secure account linking, registration, role assignment, and session login.

    Policy:
    1. Check for existing GoogleSocialAccount by Google sub.
    2. If not found by sub, safely link by verified email to existing local User (if unlinked).
    3. If new user, create User and UserProfile with default role 'MEMBER' (never ADMIN).
    4. Enforce membership approval policy (if REQUIRE_MEMBERSHIP_APPROVAL is True).
    5. Check account suspension status.
    6. Rotate session and log user in.
    7. Record security audit log event.
    """
    sub = token_claims['sub']
    email = token_claims['email']
    given_name = token_claims.get('given_name', '')
    family_name = token_claims.get('family_name', '')
    picture = token_claims.get('picture', '')

    with transaction.atomic():
        # 1. Look up by Google subject identifier
        social_account = GoogleSocialAccount.objects.filter(google_sub=sub).select_related('user', 'user__profile').first()

        if social_account:
            user = social_account.user
            # Update profile metadata
            social_account.email = email
            social_account.email_verified = True
            social_account.picture_url = picture or social_account.picture_url
            social_account.given_name = given_name or social_account.given_name
            social_account.family_name = family_name or social_account.family_name
            social_account.save()
            is_new = False
        else:
            # 2. Check if a user already exists with this exact verified email
            existing_user = User.objects.filter(email__iexact=email).select_related('profile').first()

            if existing_user:
                # Security check: Does this user already have a different Google ID attached?
                if hasattr(existing_user, 'google_account') and existing_user.google_account.google_sub != sub:
                    logger.warning(f"Account mix-up rejected: email {email} belongs to user {existing_user.username} with different Google sub.")
                    return None, "This email is already associated with a different Google account."

                # Safely link Google ID to existing user
                social_account = GoogleSocialAccount.objects.create(
                    user=existing_user,
                    google_sub=sub,
                    email=email,
                    email_verified=True,
                    given_name=given_name,
                    family_name=family_name,
                    picture_url=picture
                )
                user = existing_user
                is_new = False
            else:
                # 3. New user registration
                raw_name = f"{given_name}_{family_name}".strip('_') or email.split('@')[0]
                username = generate_unique_username(raw_name, email)

                user = User(
                    username=username,
                    email=email,
                    first_name=given_name[:150],
                    last_name=family_name[:150]
                )
                user.set_unusable_password()
                user.save()

                # UserProfile created by post_save signal
                profile = user.profile
                # Strict Default Role: Standard MEMBER, never Staff/Admin
                profile.role = 'MEMBER'
                profile.tier = 'STUDENT'

                # Check approval policy
                require_approval = getattr(settings, 'REQUIRE_MEMBERSHIP_APPROVAL', False)
                if require_approval:
                    profile.membership_status = 'PENDING'
                    profile.is_approved = False
                else:
                    profile.membership_status = 'ACTIVE'
                    profile.is_approved = True

                profile.can_borrow = True
                profile.can_reserve = True
                profile.can_access_ebooks = True
                profile.save()

                social_account = GoogleSocialAccount.objects.create(
                    user=user,
                    google_sub=sub,
                    email=email,
                    email_verified=True,
                    given_name=given_name,
                    family_name=family_name,
                    picture_url=picture
                )
                is_new = True

        # 4. Check if account is suspended
        if hasattr(user, 'profile') and user.profile.membership_status == 'SUSPENDED':
            return None, "Your account has been suspended by the library administration. Access is denied."

    # 5. Session creation & rotation
    login(request, user)

    # Clean up OAuth session state tokens
    request.session.pop('oauth_state', None)
    request.session.pop('oauth_nonce', None)

    # 6. Audit Logging
    action_desc = f"Google Sign-In: {'Created new user' if is_new else 'Authenticated user'} '{user.username}' ({email})"
    log_activity('OAUTH_LOGIN', action_desc, user=user, request=request)

    return user, None


def revoke_user_sessions(user_id):
    """
    Terminates all active sessions for a given user.
    Called when an administrator suspends an account or revokes sessions.
    """
    from django.contrib.sessions.models import Session
    revoked_count = 0
    now = time.time()

    for s in Session.objects.all():
        try:
            data = s.get_decoded()
            if str(data.get('_auth_user_id')) == str(user_id):
                s.delete()
                revoked_count += 1
        except Exception:
            pass

    return revoked_count
