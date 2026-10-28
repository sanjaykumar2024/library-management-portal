import base64
import json
import os
import sys
import time

# Configure Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings

from accounts.models import UserProfile, GoogleSocialAccount
from accounts.oauth_services import (
    register_mock_oauth_payload,
    clear_mock_oauth_payloads,
    verify_google_id_token,
    handle_google_user_authentication,
    revoke_user_sessions,
    decode_jwt_unverified_payload
)
from catalog.models import Book, BookCopy, Category
from circulation.models import Loan, Fine
from circulation.services import can_member_borrow
from reservations.services import can_member_reserve
from core.models import ActivityLog


def make_test_jwt(claims):
    """Creates a 3-part unencrypted JWT string for testing token claim validation."""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}).encode('utf-8')).decode('utf-8').rstrip('=')
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode('utf-8')).decode('utf-8').rstrip('=')
    signature = base64.urlsafe_b64encode(b"mock_signature_bytes_for_testing").decode('utf-8').rstrip('=')
    return f"{header}.{payload}.{signature}"


class GoogleOAuthAndAccessControlTests(TestCase):
    """
    Comprehensive verification suite for Google OAuth 2.0 / OpenID Connect,
    Admin Access Control, Granular Permissions, and Regression testing.
    """

    def setUp(self):
        clear_mock_oauth_payloads()
        self.client = Client()

        # Admin user
        self.admin_user, _ = User.objects.get_or_create(
            username='admin_test',
            defaults={'email': 'admin_test@library.org', 'is_staff': True, 'is_superuser': True}
        )
        self.admin_user.set_password('admin123')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        self.admin_profile = self.admin_user.profile
        self.admin_profile.role = 'ADMIN'
        self.admin_profile.membership_status = 'ACTIVE'
        self.admin_profile.is_approved = True
        self.admin_profile.save()

        # Librarian user
        self.librarian_user, _ = User.objects.get_or_create(
            username='librarian_test',
            defaults={'email': 'librarian_test@library.org', 'is_staff': True}
        )
        self.librarian_user.set_password('librarian123')
        self.librarian_user.is_staff = True
        self.librarian_user.save()
        self.librarian_profile = self.librarian_user.profile
        self.librarian_profile.role = 'LIBRARIAN'
        self.librarian_profile.membership_status = 'ACTIVE'
        self.librarian_profile.is_approved = True
        self.librarian_profile.save()

        # Member user
        self.member_user, _ = User.objects.get_or_create(
            username='member_test',
            defaults={'email': 'member_test@library.org'}
        )
        self.member_user.set_password('member123')
        self.member_user.save()
        self.member_profile = self.member_user.profile
        self.member_profile.role = 'MEMBER'
        self.member_profile.membership_status = 'ACTIVE'
        self.member_profile.is_approved = True
        self.member_profile.can_borrow = True
        self.member_profile.can_reserve = True
        self.member_profile.can_access_ebooks = True
        self.member_profile.save()

        # Test Category and Book
        self.category, _ = Category.objects.get_or_create(name='Computer Science')
        self.book, _ = Book.objects.get_or_create(
            isbn='9780132350884',
            defaults={'title': 'Clean Code', 'category': self.category, 'is_active': True}
        )
        self.book_copy, _ = BookCopy.objects.get_or_create(
            book=self.book,
            accession_number='ACC-TEST-001',
            defaults={'status': 'AVAILABLE'}
        )

    def tearDown(self):
        clear_mock_oauth_payloads()

    # =========================================================================
    # PART 1: Google Sign-In UI & Configuration Tests
    # =========================================================================

    def test_01_google_login_button_rendered_on_login_page(self):
        """Verify visible 'Continue with Google' button with official styling exists on login page."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Continue with Google')
        self.assertContains(response, 'btn-google-login')
        self.assertContains(response, reverse('accounts:google_login'))

    @override_settings(GOOGLE_OAUTH_CLIENT_ID='', GOOGLE_OAUTH_CLIENT_SECRET='')
    def test_02_google_login_unconfigured_redirects_with_warning(self):
        """When Google client ID/secret are unconfigured, show friendly notice and redirect safely."""
        response = self.client.get(reverse('accounts:google_login'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))

    @override_settings(GOOGLE_OAUTH_CLIENT_ID='test-client-id.apps.googleusercontent.com', GOOGLE_OAUTH_CLIENT_SECRET='test-secret')
    def test_03_google_login_generates_state_nonce_and_redirects(self):
        """When configured, initiates OAuth flow, creates cryptographically secure state & nonce in session."""
        response = self.client.get(reverse('accounts:google_login') + '?next=/catalog/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('https://accounts.google.com/o/oauth2/v2/auth'))
        self.assertIn('client_id=test-client-id.apps.googleusercontent.com', response['Location'])
        self.assertIn('scope=openid+email+profile', response['Location'])
        self.assertIn('prompt=select_account', response['Location'])

        # Verify session state and nonce
        session = self.client.session
        self.assertTrue('oauth_state' in session)
        self.assertTrue('oauth_nonce' in session)
        self.assertEqual(session.get('oauth_next'), '/catalog/')

    # =========================================================================
    # PART 2: OAuth Callback, State CSRF, and Cancellation
    # =========================================================================

    def test_04_callback_user_cancelled_handled_gracefully(self):
        """When user cancels Google consent, redirects to login page without 500 error."""
        response = self.client.get(reverse('accounts:google_callback') + '?error=access_denied&error_description=User+declined')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))

    def test_05_callback_state_mismatch_rejected_csrf_protection(self):
        """Callback with missing or mismatched state parameter is rejected (CSRF protection)."""
        session = self.client.session
        session['oauth_state'] = 'legitimate_state_token_123'
        session.save()

        # Submit mismatched state
        response = self.client.get(reverse('accounts:google_callback') + '?code=valid_code&state=forged_state_token')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))

        # User must remain unauthenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    # =========================================================================
    # PART 3: Token Claims Validation (Audience, Issuer, Expiry, Nonce, Verified Email)
    # =========================================================================

    def test_06_token_claims_validation_issuer(self):
        """Tokens with invalid issuer must be rejected."""
        claims = {
            'iss': 'https://malicious-issuer.com',
            'aud': 'test-client-id',
            'sub': '10001',
            'email': 'user@example.com',
            'email_verified': True,
            'exp': time.time() + 3600
        }
        token = make_test_jwt(claims)
        with self.assertRaises(ValueError) as ctx:
            verify_google_id_token(token, expected_client_id='test-client-id')
        self.assertIn("Invalid token issuer", str(ctx.exception))

    def test_07_token_claims_validation_audience(self):
        """Tokens with mismatched audience (client ID) must be rejected."""
        claims = {
            'iss': 'https://accounts.google.com',
            'aud': 'wrong-client-id',
            'sub': '10002',
            'email': 'user@example.com',
            'email_verified': True,
            'exp': time.time() + 3600
        }
        token = make_test_jwt(claims)
        with self.assertRaises(ValueError) as ctx:
            verify_google_id_token(token, expected_client_id='expected-client-id')
        self.assertIn("Audience mismatch", str(ctx.exception))

    def test_08_token_claims_validation_expired(self):
        """Expired tokens must be rejected."""
        claims = {
            'iss': 'https://accounts.google.com',
            'aud': 'test-client-id',
            'sub': '10003',
            'email': 'user@example.com',
            'email_verified': True,
            'exp': time.time() - 300  # Expired 5 mins ago
        }
        token = make_test_jwt(claims)
        with self.assertRaises(ValueError) as ctx:
            verify_google_id_token(token, expected_client_id='test-client-id')
        self.assertIn("Token has expired", str(ctx.exception))

    def test_09_token_claims_validation_nonce(self):
        """Tokens with mismatched nonce must be rejected (replay / CSRF protection)."""
        claims = {
            'iss': 'https://accounts.google.com',
            'aud': 'test-client-id',
            'sub': '10004',
            'email': 'user@example.com',
            'email_verified': True,
            'nonce': 'token_nonce_abc',
            'exp': time.time() + 3600
        }
        token = make_test_jwt(claims)
        with self.assertRaises(ValueError) as ctx:
            verify_google_id_token(token, expected_client_id='test-client-id', expected_nonce='session_nonce_xyz')
        self.assertIn("Token nonce mismatch", str(ctx.exception))

    def test_10_token_claims_validation_unverified_email(self):
        """Google accounts with unverified emails must be rejected."""
        claims = {
            'iss': 'https://accounts.google.com',
            'aud': 'test-client-id',
            'sub': '10005',
            'email': 'unverified@example.com',
            'email_verified': False,
            'is_mock_token': True,
            'exp': time.time() + 3600
        }
        token = make_test_jwt(claims)
        with self.assertRaises(ValueError) as ctx:
            verify_google_id_token(token, expected_client_id='test-client-id')
        self.assertIn("not verified", str(ctx.exception).lower())

    # =========================================================================
    # PART 4: User Registration, Role Assignment & Repeat Login
    # =========================================================================

    @override_settings(GOOGLE_OAUTH_CLIENT_ID='test-client-id.apps.googleusercontent.com', GOOGLE_OAUTH_CLIENT_SECRET='test-secret')
    def test_11_first_time_google_sign_in_creates_one_user_and_member_role(self):
        """First-time sign in creates exactly 1 User with GoogleSocialAccount and standard MEMBER role (never Admin)."""
        test_sub = "google_sub_first_time_98765"
        test_email = "new_google_patron@example.org"
        claims = {
            'iss': 'https://accounts.google.com',
            'aud': 'test-client-id.apps.googleusercontent.com',
            'sub': test_sub,
            'email': test_email,
            'email_verified': True,
            'given_name': 'Google',
            'family_name': 'Patron',
            'picture': 'https://lh3.googleusercontent.com/test_avatar.jpg',
            'nonce': 'secure_nonce_123',
            'is_mock_token': True,
            'exp': time.time() + 3600
        }
        mock_id_token = make_test_jwt(claims)
        register_mock_oauth_payload('code_first_time', {
            'access_token': 'mock_access_token_123',
            'id_token': mock_id_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        })

        # Set session state
        session = self.client.session
        session['oauth_state'] = 'state_first_time'
        session['oauth_nonce'] = 'secure_nonce_123'
        session.save()

        # Execute callback
        initial_user_count = User.objects.count()
        response = self.client.get(reverse('accounts:google_callback') + '?code=code_first_time&state=state_first_time')
        self.assertEqual(response.status_code, 302)

        # Verify exactly one new user created
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        created_user = User.objects.get(email=test_email)
        self.assertEqual(created_user.first_name, 'Google')
        self.assertEqual(created_user.last_name, 'Patron')
        self.assertFalse(created_user.has_usable_password())

        # Verify Profile and Strict Default Role
        profile = created_user.profile
        self.assertEqual(profile.role, 'MEMBER')
        self.assertFalse(profile.is_admin())
        self.assertFalse(profile.is_librarian())
        self.assertEqual(profile.membership_status, 'ACTIVE')
        self.assertTrue(profile.is_approved)

        # Verify GoogleSocialAccount link
        social = GoogleSocialAccount.objects.get(google_sub=test_sub)
        self.assertEqual(social.user, created_user)
        self.assertEqual(social.email, test_email)
        self.assertEqual(social.picture_url, 'https://lh3.googleusercontent.com/test_avatar.jpg')

        # Verify user is logged in
        self.assertTrue('_auth_user_id' in self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), created_user.id)

    @override_settings(GOOGLE_OAUTH_CLIENT_ID='test-client-id.apps.googleusercontent.com', GOOGLE_OAUTH_CLIENT_SECRET='test-secret')
    def test_12_repeat_google_sign_in_does_not_create_duplicates(self):
        """Repeat login retrieves existing user, updates last_login, and does not create duplicate records."""
        test_sub = "google_sub_repeat_12345"
        test_email = "repeat_patron@example.org"
        claims = {
            'iss': 'https://accounts.google.com',
            'aud': 'test-client-id.apps.googleusercontent.com',
            'sub': test_sub,
            'email': test_email,
            'email_verified': True,
            'given_name': 'Repeat',
            'family_name': 'User',
            'nonce': 'repeat_nonce_1',
            'is_mock_token': True,
            'exp': time.time() + 3600
        }
        mock_id_token = make_test_jwt(claims)
        register_mock_oauth_payload('code_repeat_1', {'id_token': mock_id_token, 'access_token': 'tok1'})

        # First sign-in
        session = self.client.session
        session['oauth_state'] = 'state_repeat_1'
        session['oauth_nonce'] = 'repeat_nonce_1'
        session.save()
        self.client.get(reverse('accounts:google_callback') + '?code=code_repeat_1&state=state_repeat_1')

        user_count_after_first = User.objects.count()

        # Second sign-in with same Google Sub
        register_mock_oauth_payload('code_repeat_2', {'id_token': mock_id_token, 'access_token': 'tok2'})
        session = self.client.session
        session['oauth_state'] = 'state_repeat_2'
        session['oauth_nonce'] = 'repeat_nonce_1'
        session.save()
        self.client.get(reverse('accounts:google_callback') + '?code=code_repeat_2&state=state_repeat_2')

        # User count must not increase
        self.assertEqual(User.objects.count(), user_count_after_first)
        self.assertEqual(GoogleSocialAccount.objects.filter(google_sub=test_sub).count(), 1)

    @override_settings(GOOGLE_OAUTH_CLIENT_ID='test-client-id.apps.googleusercontent.com', GOOGLE_OAUTH_CLIENT_SECRET='test-secret')
    def test_13_existing_account_with_matching_email_links_safely(self):
        """Existing local account with matching verified email links to Google without duplicating User."""
        local_email = "existing_member@library.org"
        local_user = User.objects.create_user(username='existing_member', email=local_email, password='password123')
        test_sub = "google_sub_link_9999"

        claims = {
            'iss': 'https://accounts.google.com',
            'aud': 'test-client-id.apps.googleusercontent.com',
            'sub': test_sub,
            'email': local_email,
            'email_verified': True,
            'given_name': 'Existing',
            'family_name': 'Member',
            'nonce': 'nonce_link',
            'is_mock_token': True,
            'exp': time.time() + 3600
        }
        mock_id_token = make_test_jwt(claims)
        register_mock_oauth_payload('code_link', {'id_token': mock_id_token, 'access_token': 'tok_link'})

        session = self.client.session
        session['oauth_state'] = 'state_link'
        session['oauth_nonce'] = 'nonce_link'
        session.save()

        initial_count = User.objects.count()
        response = self.client.get(reverse('accounts:google_callback') + '?code=code_link&state=state_link')
        self.assertEqual(response.status_code, 302)

        # Must not create a duplicate user
        self.assertEqual(User.objects.count(), initial_count)
        # GoogleSocialAccount must be linked to the existing user
        social = GoogleSocialAccount.objects.get(google_sub=test_sub)
        self.assertEqual(social.user, local_user)

    # =========================================================================
    # PART 5: Membership Approval Policy & Granular Permissions
    # =========================================================================

    @override_settings(GOOGLE_OAUTH_CLIENT_ID='test-client-id.apps.googleusercontent.com', GOOGLE_OAUTH_CLIENT_SECRET='test-secret', REQUIRE_MEMBERSHIP_APPROVAL=True)
    def test_14_require_membership_approval_sets_pending_and_blocks_borrowing(self):
        """When REQUIRE_MEMBERSHIP_APPROVAL is True, new user gets PENDING status and cannot borrow until approved."""
        test_sub = "google_sub_pending_555"
        test_email = "pending_patron@example.org"
        claims = {
            'iss': 'https://accounts.google.com',
            'aud': 'test-client-id.apps.googleusercontent.com',
            'sub': test_sub,
            'email': test_email,
            'email_verified': True,
            'nonce': 'nonce_pending',
            'is_mock_token': True,
            'exp': time.time() + 3600
        }
        mock_id_token = make_test_jwt(claims)
        register_mock_oauth_payload('code_pending', {'id_token': mock_id_token, 'access_token': 'tok_pending'})

        session = self.client.session
        session['oauth_state'] = 'state_pending'
        session['oauth_nonce'] = 'nonce_pending'
        session.save()

        self.client.get(reverse('accounts:google_callback') + '?code=code_pending&state=state_pending')

        pending_user = User.objects.get(email=test_email)
        self.assertEqual(pending_user.profile.membership_status, 'PENDING')
        self.assertFalse(pending_user.profile.is_approved)

        # Verify borrowing & reservation are blocked
        can_borrow, reason_b = can_member_borrow(pending_user.profile)
        self.assertFalse(can_borrow)
        self.assertIn("pending administrator approval", reason_b)

        can_reserve, reason_r = can_member_reserve(pending_user.profile)
        self.assertFalse(can_reserve)
        self.assertIn("pending administrator approval", reason_r)

    def test_15_admin_can_approve_pending_member(self):
        """Administrator can approve pending membership via endpoint, activating borrowing rights."""
        # Create pending user
        pending_u = User.objects.create_user(username='pending_u', email='pending_u@example.org')
        pending_u.profile.membership_status = 'PENDING'
        pending_u.profile.is_approved = False
        pending_u.profile.save()

        # Admin logs in and approves
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('accounts:approve_membership', kwargs={'user_id': pending_u.id}))
        self.assertEqual(response.status_code, 302)

        pending_u.profile.refresh_from_db()
        self.assertEqual(pending_u.profile.membership_status, 'ACTIVE')
        self.assertTrue(pending_u.profile.is_approved)

        # Now can borrow and reserve
        can_borrow, _ = can_member_borrow(pending_u.profile)
        self.assertTrue(can_borrow)
        can_reserve, _ = can_member_reserve(pending_u.profile)
        self.assertTrue(can_reserve)

    def test_16_admin_granular_permission_toggles(self):
        """Admin can toggle can_borrow, can_reserve, and can_access_ebooks, immediately enforcing access."""
        self.client.force_login(self.admin_user)

        # Revoke borrowing permission
        post_data = {
            'role': 'MEMBER',
            'status': 'ACTIVE',
            'tier': 'STUDENT',
            'is_approved': 'on',
            'can_reserve': 'on',
            'can_access_ebooks': 'on',
            # can_borrow omitted -> False
        }
        response = self.client.post(reverse('accounts:update_user_permissions', kwargs={'user_id': self.member_user.id}), post_data)
        self.assertEqual(response.status_code, 302)

        self.member_profile.refresh_from_db()
        self.assertFalse(self.member_profile.can_borrow)
        self.assertTrue(self.member_profile.can_reserve)

        can_borrow, reason = can_member_borrow(self.member_profile)
        self.assertFalse(can_borrow)
        self.assertIn("disabled", reason)

        # Revoke reservation permission
        post_data['can_borrow'] = 'on'
        del post_data['can_reserve']
        self.client.post(reverse('accounts:update_user_permissions', kwargs={'user_id': self.member_user.id}), post_data)

        self.member_profile.refresh_from_db()
        self.assertTrue(self.member_profile.can_borrow)
        self.assertFalse(self.member_profile.can_reserve)

        can_reserve, reason = can_member_reserve(self.member_profile)
        self.assertFalse(can_reserve)
        self.assertIn("disabled", reason)

    # =========================================================================
    # PART 6: Access Control & Authorization Boundaries
    # =========================================================================

    def test_17_ordinary_member_cannot_access_user_management(self):
        """Ordinary member receives HTTP 403 PermissionDenied when accessing /accounts/users/."""
        self.client.force_login(self.member_user)
        response = self.client.get(reverse('accounts:user_management'))
        self.assertEqual(response.status_code, 403)

    def test_18_ordinary_member_cannot_call_update_permissions_api(self):
        """Ordinary member receives HTTP 403 PermissionDenied when attempting to modify permissions."""
        self.client.force_login(self.member_user)
        response = self.client.post(reverse('accounts:update_user_permissions', kwargs={'user_id': self.member_user.id}), {'role': 'ADMIN'})
        self.assertEqual(response.status_code, 403)
        self.member_profile.refresh_from_db()
        self.assertEqual(self.member_profile.role, 'MEMBER')

    def test_19_admin_cannot_demote_self_lockout_protection(self):
        """Administrator cannot revoke their own admin role, preventing accidental system lockout."""
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('accounts:update_user_permissions', kwargs={'user_id': self.admin_user.id}), {'role': 'MEMBER', 'status': 'ACTIVE'})
        self.assertEqual(response.status_code, 302)

        self.admin_profile.refresh_from_db()
        self.assertEqual(self.admin_profile.role, 'ADMIN')

    def test_20_admin_can_promote_member_to_librarian(self):
        """Administrator can promote a member to librarian, granting librarian access."""
        self.client.force_login(self.admin_user)
        post_data = {
            'role': 'LIBRARIAN',
            'status': 'ACTIVE',
            'tier': 'STANDARD',
            'is_approved': 'on',
            'can_borrow': 'on',
            'can_reserve': 'on',
            'can_access_ebooks': 'on',
        }
        self.client.post(reverse('accounts:update_user_permissions', kwargs={'user_id': self.member_user.id}), post_data)

        self.member_profile.refresh_from_db()
        self.member_user.refresh_from_db()
        self.assertEqual(self.member_profile.role, 'LIBRARIAN')
        self.assertTrue(self.member_user.is_staff)
        self.assertTrue(self.member_profile.is_librarian())

    # =========================================================================
    # PART 7: Suspended User Handling & Session Revocation
    # =========================================================================

    def test_21_suspending_user_revokes_sessions_and_blocks_access(self):
        """When an admin suspends a user, active sessions are revoked and borrowing is denied."""
        # 1. Member logs in
        member_client = Client()
        member_client.force_login(self.member_user)
        self.assertTrue('_auth_user_id' in member_client.session)

        # 2. Admin suspends member
        self.client.force_login(self.admin_user)
        post_data = {
            'role': 'MEMBER',
            'status': 'SUSPENDED',
            'tier': 'STUDENT',
        }
        self.client.post(reverse('accounts:update_user_permissions', kwargs={'user_id': self.member_user.id}), post_data)

        self.member_profile.refresh_from_db()
        self.assertEqual(self.member_profile.membership_status, 'SUSPENDED')

        # 3. Check borrowing & reservations blocked
        can_b, reason_b = can_member_borrow(self.member_profile)
        self.assertFalse(can_b)
        self.assertIn("suspended", reason_b.lower())

        can_r, reason_r = can_member_reserve(self.member_profile)
        self.assertFalse(can_r)
        self.assertIn("suspended", reason_r.lower())

        # 4. Protected view access redirects to login (302)
        resp = member_client.get(reverse('accounts:profile'))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp['Location'].startswith(reverse('accounts:login')))

        # 5. Member cannot log in with password while suspended
        login_resp = member_client.post(reverse('accounts:login'), {'username': 'member_test', 'password': 'member123'})
        self.assertEqual(login_resp.status_code, 200)
        self.assertContains(login_resp, "suspended by the library administration")

    def test_22_revoke_user_sessions_endpoint(self):
        """Revoke user sessions endpoint terminates all active sessions for a user."""
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('accounts:revoke_user_sessions', kwargs={'user_id': self.member_user.id}))
        self.assertEqual(response.status_code, 302)

        # Verify audit log recorded
        last_log = ActivityLog.objects.filter(action='SESSION_REVOKED').first()
        self.assertIsNotNone(last_log)
        self.assertIn('member_test', last_log.description)

    # =========================================================================
    # PART 8: Regression Tests for Existing Features
    # =========================================================================

    def test_23_existing_password_login_works(self):
        """Standard username/password authentication continues to function without regression."""
        client = Client()
        response = client.post(reverse('accounts:login'), {'username': 'admin_test', 'password': 'admin123'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('core:dashboard'))

    def test_24_catalog_search_and_availability(self):
        """Catalog listing, search, and copy availability continue to work."""
        response = self.client.get(reverse('catalog:list') + '?q=Clean+Code')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Clean Code')

    def test_25_logout_invalidates_session(self):
        """Logging out flushes session and redirects to home."""
        self.client.force_login(self.member_user)
        self.assertTrue('_auth_user_id' in self.client.session)
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)


if __name__ == '__main__':
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=2)
    failures = runner.run_tests(['tests.test_google_oauth_and_permissions'])
    sys.exit(bool(failures))
