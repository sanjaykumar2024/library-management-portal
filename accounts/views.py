from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.models import User
from .forms import MemberRegistrationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
        
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            try:
                from core.models import log_activity
                log_activity('MEMBER_REGISTERED', f"New member '{user.username}' registered", user=user, request=request)
            except Exception:
                pass
            messages.success(request, "Registration successful! Welcome to LibrarySphere.")
            return redirect('core:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MemberRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if hasattr(user, 'profile') and user.profile.membership_status == 'SUSPENDED':
            messages.error(self.request, "Your account has been suspended by the library administration. Access is denied.")
            return self.form_invalid(form)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = get_google_client_config()
        context['is_google_configured'] = config['is_configured']
        return context

    def get_success_url(self):
        return super().get_success_url()

from django.utils import timezone
import datetime
from django.db.models import Sum

@login_required
def profile_view(request):
    profile = request.user.profile
    
    # Active Loans
    from circulation.models import Loan, Fine
    active_loans = Loan.objects.filter(member=profile, status='ISSUED').select_related('book_copy__book').order_by('due_date')
    past_loans_count = Loan.objects.filter(member=profile, status='RETURNED').count()
    
    # Active Reservations with live queue info
    from reservations.models import Reservation
    from reservations import services as res_services
    active_reservations = Reservation.objects.filter(
        member=profile, 
        status__in=['PENDING', 'ALLOCATED']
    ).select_related('book', 'allocated_copy').order_by('-reservation_date')
    
    for r in active_reservations:
        r.queue_info = res_services.get_queue_info(r)
        
    # Fines summary
    unpaid_fines = Fine.objects.filter(loan__member=profile, status='PENDING').select_related('loan__book_copy__book')
    total_unpaid_fines = unpaid_fines.aggregate(total=Sum('amount'))['total'] or 0
    paid_fines = Fine.objects.filter(loan__member=profile, status='PAID').select_related('loan__book_copy__book').order_by('-created_at')[:10]
    total_paid_fines = paid_fines.aggregate(total=Sum('amount'))['total'] or 0
    
    # Digital E-Book Passes & Reading History
    from ebooks.models import EBookPass, EBookAccessLog
    ebook_passes = EBookPass.objects.filter(user=request.user, is_active=True).select_related('ebook__book')
    reading_history = EBookAccessLog.objects.filter(user=request.user).select_related('ebook__book').order_by('-accessed_at')[:8]
    
    # Membership Expiry calculations
    days_to_expiry = None
    is_expiring_soon = False
    if profile.membership_expiry_date:
        today = timezone.now().date()
        diff = (profile.membership_expiry_date - today).days
        days_to_expiry = diff
        is_expiring_soon = 0 <= diff <= 30

    context = {
        'user': request.user,
        'profile': profile,
        'active_loans': active_loans,
        'past_loans_count': past_loans_count,
        'active_reservations': active_reservations,
        'unpaid_fines': unpaid_fines,
        'paid_fines': paid_fines,
        'total_unpaid_fines': total_unpaid_fines,
        'total_paid_fines': total_paid_fines,
        'ebook_passes': ebook_passes,
        'reading_history': reading_history,
        'days_to_expiry': days_to_expiry,
        'is_expiring_soon': is_expiring_soon,
        'membership_requests': request.user.membership_requests.all()[:5],
        'tier_choices': UserProfile.TIER_CHOICES,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def update_contact_view(request):
    """Member self-service: update phone, address, and profile image."""
    if request.method == 'POST':
        profile = request.user.profile
        phone = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()

        if phone:
            profile.phone_number = phone
        if address:
            profile.address = address
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']

        # Also allow updating first/last name on User model
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        if first_name:
            request.user.first_name = first_name
        if last_name:
            request.user.last_name = last_name
        request.user.save()

        profile.save()

        try:
            from core.models import log_activity
            log_activity('PROFILE_UPDATED', f"Contact info updated by {request.user.username}", user=request.user, request=request)
        except Exception:
            pass

        messages.success(request, "Your contact information has been updated successfully.")
    return redirect('accounts:profile')


@login_required
def request_membership_renewal_view(request):
    """Member 1-click renewal action (extends by 1 year)."""
    if request.method == 'POST':
        profile = request.user.profile
        today = timezone.now().date()
        
        # Extend from current expiry if in future, else from today
        base_date = profile.membership_expiry_date if (profile.membership_expiry_date and profile.membership_expiry_date > today) else today
        profile.membership_expiry_date = base_date + datetime.timedelta(days=365)
        profile.membership_status = 'ACTIVE'
        profile.save()
        
        try:
            from core.models import log_activity
            log_activity('MEMBERSHIP_RENEWED', f"Self-service renewal for {request.user.username}", user=request.user, request=request)
        except Exception:
            pass

        from notifications.services import create_notification
        create_notification(
            user=request.user,
            title="Membership Renewed!",
            message=f"Your LibrarySphere membership has been renewed until {profile.membership_expiry_date.strftime('%B %d, %Y')}.",
            type='SUCCESS',
            link="/accounts/profile/"
        )
        messages.success(request, f"Membership renewed successfully! Valid until {profile.membership_expiry_date.strftime('%B %d, %Y')}.")
    return redirect('accounts:profile')


@login_required
def renew_membership_view(request, pk):
    """Librarian action to renew a member for +1 year."""
    if not request.user.profile.is_librarian():
        messages.error(request, "Permission denied.")
        return redirect('core:dashboard')
        
    profile = get_object_or_404(UserProfile, pk=pk)
    if request.method == 'POST':
        today = timezone.now().date()
        base_date = profile.membership_expiry_date if (profile.membership_expiry_date and profile.membership_expiry_date > today) else today
        profile.membership_expiry_date = base_date + datetime.timedelta(days=365)
        profile.membership_status = 'ACTIVE'
        profile.save()
        
        from notifications.services import create_notification
        create_notification(
            user=profile.user,
            title="Membership Renewed by Library Desk",
            message=f"Your library membership was extended by the circulation desk until {profile.membership_expiry_date.strftime('%B %d, %Y')}.",
            type='SUCCESS',
            link="/accounts/profile/"
        )
        messages.success(request, f"Membership for {profile.user.username} renewed until {profile.membership_expiry_date.strftime('%b %d, %Y')}.")
    return redirect('accounts:member_detail', pk=profile.pk)


@login_required
def toggle_member_status_view(request, pk):
    """Librarian quick action to set member status (ACTIVE / SUSPENDED)."""
    if not request.user.profile.is_librarian():
        messages.error(request, "Permission denied.")
        return redirect('core:dashboard')
        
    profile = get_object_or_404(UserProfile, pk=pk)
    new_status = request.POST.get('status')
    if new_status in ['ACTIVE', 'SUSPENDED', 'EXPIRED']:
        profile.membership_status = new_status
        profile.save()
        messages.success(request, f"Status for {profile.user.username} updated to {profile.get_membership_status_display()}.")
    return redirect('accounts:member_detail', pk=profile.pk)


class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.is_librarian()

class MemberListView(LibrarianRequiredMixin, ListView):
    model = UserProfile
    template_name = 'accounts/member_list.html'
    context_object_name = 'members'
    
    def get_queryset(self):
        qs = UserProfile.objects.filter(role='MEMBER').select_related('user').order_by('-created_at')
        q = self.request.GET.get('q')
        status = self.request.GET.get('status')
        if q:
            qs = qs.filter(user__first_name__icontains=q) | qs.filter(user__last_name__icontains=q) | qs.filter(membership_number__icontains=q) | qs.filter(user__email__icontains=q) | qs.filter(user__username__icontains=q)
        if status and status != 'ALL':
            qs = qs.filter(membership_status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_members'] = UserProfile.objects.filter(role='MEMBER').count()
        context['active_members'] = UserProfile.objects.filter(role='MEMBER', membership_status='ACTIVE').count()
        context['pending_members'] = UserProfile.objects.filter(role='MEMBER', membership_status='PENDING').count()
        context['expired_members'] = UserProfile.objects.filter(role='MEMBER', membership_status='EXPIRED').count()
        context['suspended_members'] = UserProfile.objects.filter(role='MEMBER', membership_status='SUSPENDED').count()
        context['selected_status'] = self.request.GET.get('status', 'ALL')
        context['q'] = self.request.GET.get('q', '')
        return context

class MemberDetailView(LibrarianRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'accounts/member_detail.html'
    context_object_name = 'member_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        from circulation.models import Loan, Fine
        from reservations.models import Reservation
        context['active_loans'] = Loan.objects.filter(member=profile, status='ISSUED').select_related('book_copy__book')
        context['past_loans'] = Loan.objects.filter(member=profile, status='RETURNED').select_related('book_copy__book').order_by('-return_date')[:10]
        context['reservations'] = Reservation.objects.filter(member=profile).select_related('book', 'allocated_copy').order_by('-reservation_date')
        context['fines'] = Fine.objects.filter(loan__member=profile).select_related('loan__book_copy__book')
        return context

class MemberUpdateView(LibrarianRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'accounts/member_form.html'
    fields = ['tier', 'phone_number', 'address', 'membership_status', 'membership_expiry_date', 'admin_notes']
    context_object_name = 'member_profile'


    def get_success_url(self):
        return reverse_lazy('accounts:member_detail', kwargs={'pk': self.object.pk})
        
    def form_valid(self, form):
        messages.success(self.request, "Member profile updated successfully.")
        return super().form_valid(form)


from .models import MembershipRequest

@login_required
def submit_membership_request_view(request):
    """Member submits a request for tier upgrade or membership renewal."""
    if request.method == 'POST':
        req_type = request.POST.get('request_type', 'RENEWAL')
        req_tier = request.POST.get('requested_tier', '')
        reason = request.POST.get('reason', '').strip()
        
        # Check if already has a pending request
        pending = MembershipRequest.objects.filter(user=request.user, status='PENDING').first()
        if pending:
            messages.warning(request, "You already have a pending membership request under librarian review.")
            return redirect('accounts:profile')
            
        req = MembershipRequest.objects.create(
            user=request.user,
            request_type=req_type,
            requested_tier=req_tier if req_type == 'UPGRADE_TIER' else None,
            reason=reason
        )
        
        from notifications.services import create_notification
        create_notification(
            user=request.user,
            title="Request Submitted",
            message=f"Your {req.get_request_type_display()} request has been submitted for librarian review.",
            type='INFO',
            link='/accounts/profile/'
        )
        
        messages.success(request, f"Your {req.get_request_type_display()} request has been submitted successfully.")
    return redirect('accounts:profile')


@login_required
def manage_membership_requests_view(request):
    """Librarian dashboard to review, approve, or reject membership requests."""
    if not request.user.profile.is_librarian():
        messages.error(request, "Permission denied.")
        return redirect('core:dashboard')
        
    if request.method == 'POST':
        req_id = request.POST.get('request_id')
        action = request.POST.get('action')  # 'approve' or 'reject'
        admin_notes = request.POST.get('admin_notes', '').strip()
        
        mem_req = get_object_or_404(MembershipRequest, id=req_id)
        
        if action == 'approve':
            mem_req.status = 'APPROVED'
            mem_req.reviewed_by = request.user
            mem_req.reviewed_at = timezone.now()
            mem_req.admin_notes = admin_notes
            mem_req.save()
            
            profile = mem_req.user.profile
            if mem_req.request_type == 'RENEWAL':
                today = timezone.now().date()
                base_date = profile.membership_expiry_date if (profile.membership_expiry_date and profile.membership_expiry_date > today) else today
                profile.membership_expiry_date = base_date + datetime.timedelta(days=365)
                profile.membership_status = 'ACTIVE'
                profile.save()
            elif mem_req.request_type == 'UPGRADE_TIER' and mem_req.requested_tier:
                profile.tier = mem_req.requested_tier
                profile.save()
                
            from notifications.services import create_notification
            create_notification(
                user=mem_req.user,
                title="Membership Request Approved!",
                message=f"Your {mem_req.get_request_type_display()} request was approved by the library administration.",
                type='SUCCESS',
                link='/accounts/profile/'
            )

            try:
                from core.models import log_activity
                log_activity('MEMBERSHIP_UPGRADED', f"Approved {mem_req.get_request_type_display()} for {mem_req.user.username}", user=request.user, request=request)
            except Exception:
                pass

            messages.success(request, f"Approved request for {mem_req.user.username}.")

        elif action == 'reject':
            mem_req.status = 'REJECTED'
            mem_req.reviewed_by = request.user
            mem_req.reviewed_at = timezone.now()
            mem_req.admin_notes = admin_notes
            mem_req.save()
            
            from notifications.services import create_notification
            create_notification(
                user=mem_req.user,
                title="Membership Request Update",
                message=f"Your {mem_req.get_request_type_display()} request could not be approved at this time.",
                type='WARNING',
                link='/accounts/profile/'
            )
            messages.info(request, f"Rejected request for {mem_req.user.username}.")
            
        return redirect('accounts:manage_requests')
        
    pending_requests = MembershipRequest.objects.filter(status='PENDING').select_related('user', 'user__profile')
    processed_requests = MembershipRequest.objects.exclude(status='PENDING').select_related('user', 'user__profile', 'reviewed_by')[:20]
    
    context = {
        'pending_requests': pending_requests,
        'processed_requests': processed_requests,
        'total_pending': pending_requests.count(),
    }
    return render(request, 'accounts/membership_requests.html', context)


import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.crypto import constant_time_compare
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

from .oauth_services import (
    build_google_auth_url,
    exchange_code_for_tokens,
    verify_google_id_token,
    handle_google_user_authentication,
    get_google_client_config,
    get_redirect_uri,
    revoke_user_sessions
)
from core.decorators import admin_required
from core.models import log_activity



@login_required
def settings_view(request):
    """
    Patron & Staff Settings Center.
    Allows configuring Display Mode (Normal Light Mode vs Dark Mode),
    contact details, notification preferences, and viewing account security.
    """
    profile = request.user.profile

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_theme':
            theme = request.POST.get('theme', 'light').strip().lower()
            if theme in ['light', 'dark']:
                profile.theme_preference = theme
                profile.save(update_fields=['theme_preference'])
                request.session['theme_preference'] = theme
                messages.success(
                    request,
                    f"Appearance theme switched to {'Normal Mode (Light)' if theme == 'light' else 'Dark Mode'}."
                )
            return redirect('accounts:settings')

        elif action == 'update_preferences':
            phone = request.POST.get('phone_number', '').strip()
            address = request.POST.get('address', '').strip()
            theme = request.POST.get('theme', profile.theme_preference).strip().lower()

            if theme in ['light', 'dark']:
                profile.theme_preference = theme
                request.session['theme_preference'] = theme

            profile.phone_number = phone
            profile.address = address
            profile.save(update_fields=['theme_preference', 'phone_number', 'address'])

            messages.success(request, "Settings and preferences saved successfully.")
            return redirect('accounts:settings')

    context = {
        'profile': profile,
        'user': request.user,
        'current_theme': profile.theme_preference,
    }
    return render(request, 'accounts/settings.html', context)


@login_required
@require_POST
def api_toggle_theme(request):
    """Instant 1-click AJAX theme switch API."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        theme = data.get('theme', '').strip().lower()
    except Exception:
        theme = request.POST.get('theme', '').strip().lower()

    if theme not in ['light', 'dark']:
        current = request.user.profile.theme_preference
        theme = 'dark' if current == 'light' else 'light'

    profile = request.user.profile
    profile.theme_preference = theme
    profile.save(update_fields=['theme_preference'])
    request.session['theme_preference'] = theme

    return JsonResponse({
        'success': True,
        'status': 'success',
        'theme': theme,
        'theme_label': 'Normal Mode (Light)' if theme == 'light' else 'Dark Mode'
    })


# ---------------------------------------------------------------------------
# Google OAuth 2.0 / OpenID Connect Views
# ---------------------------------------------------------------------------

def google_login_view(request):
    """
    Initiates Google OAuth 2.0 / OpenID Connect sign-in flow.
    Redirects user to Google's consent screen.
    If Google OAuth credentials are not yet configured in the environment,
    provides a seamless Demo Google Account sign-in so users can evaluate the full
    Google user registration, profile sync, and permission workflow immediately.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    config = get_google_client_config()
    next_url = request.GET.get('next')

    if not config['is_configured']:
        allow_demo = getattr(settings, 'ALLOW_DEMO_GOOGLE_LOGIN', True)
        if allow_demo:
            demo_claims = {
                'sub': 'google_sub_demo_1082736451928374',
                'email': 'sanjay.google.demo@gmail.com',
                'email_verified': True,
                'name': 'Sanjay Kumar (Google Demo)',
                'given_name': 'Sanjay',
                'family_name': 'Kumar',
                'picture': 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=120&h=120&q=80',
            }
            user, err = handle_google_user_authentication(request, demo_claims)
            if err:
                messages.error(request, err)
                return redirect('accounts:login')

            messages.info(
                request,
                f"Signed in as '{user.email}' via Google (Demo Mode). To connect live Google accounts, add GOOGLE_OAUTH_CLIENT_ID & GOOGLE_OAUTH_CLIENT_SECRET in your Render Environment Variables."
            )
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('core:dashboard')

        messages.warning(
            request,
            "Google Sign-In is not yet configured. Please set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in the environment."
        )
        return redirect('accounts:login')

    try:
        auth_url = build_google_auth_url(request, next_url=next_url)
        return redirect(auth_url)
    except Exception as e:
        messages.error(request, f"Unable to initialize Google Sign-In: {e}")
        return redirect('accounts:login')


def google_callback_view(request):
    """
    Handles Google OAuth 2.0 callback:
    1. Checks for user cancellation / denied consent.
    2. Validates CSRF state token against user session.
    3. Exchanges authorization code for tokens.
    4. Validates ID token claims (signature, aud, iss, exp, nonce, email_verified).
    5. Retrieves or creates user record with safe account linking and default permissions.
    6. Creates session and redirects to appropriate dashboard.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    # 1. Check for error parameters (e.g. user cancelled consent)
    error = request.GET.get('error')
    if error:
        error_desc = request.GET.get('error_description', '')
        if error in ['access_denied', 'consent_denied', 'user_cancelled']:
            messages.info(request, "Google sign-in was cancelled.")
        else:
            messages.warning(request, f"Google authentication failed: {error} {error_desc}".strip())
        return redirect('accounts:login')

    # 2. State verification for CSRF prevention
    state = request.GET.get('state', '').strip()
    session_state = request.session.get('oauth_state', '').strip()

    if not state or not session_state or not constant_time_compare(state, session_state):
        messages.error(request, "Authentication failed: Invalid security state token (possible CSRF attack).")
        return redirect('accounts:login')

    code = request.GET.get('code', '').strip()
    if not code:
        messages.error(request, "Authentication failed: Missing authorization code from Google.")
        return redirect('accounts:login')

    redirect_uri = get_redirect_uri(request)
    config = get_google_client_config()
    expected_nonce = request.session.get('oauth_nonce')

    try:
        # 3. Exchange code for tokens
        token_data = exchange_code_for_tokens(code, redirect_uri)
        id_token = token_data.get('id_token')
        if not id_token:
            messages.error(request, "Google authentication did not return an identity token.")
            return redirect('accounts:login')

        # 4. Validate token claims
        claims = verify_google_id_token(
            id_token,
            expected_client_id=config['client_id'],
            expected_nonce=expected_nonce
        )

        # 5. Authenticate or register user
        user, err = handle_google_user_authentication(request, claims)
        if err:
            messages.error(request, err)
            return redirect('accounts:login')

        # 6. Success message & redirection
        messages.success(request, f"Welcome to LibrarySphere, {user.first_name or user.username}! Signed in with Google.")

        next_url = request.session.pop('oauth_next', None)
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)

        return redirect('core:dashboard')

    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}", exc_info=True)
        messages.error(request, f"Google Sign-In failed: {e}")
        return redirect('accounts:login')


# ---------------------------------------------------------------------------
# Admin User & Permission Management Views
# ---------------------------------------------------------------------------

@admin_required
def user_management_view(request):
    """
    Dedicated Administrator Dashboard for User and Permission Management.
    Supports searching, filtering by role, status, auth provider,
    toggling granular permissions, approving memberships, and session revocation.
    """
    users_qs = User.objects.select_related('profile', 'google_account').order_by('-date_joined')

    # Search & filters
    q = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', 'ALL').strip()
    status_filter = request.GET.get('status', 'ALL').strip()
    auth_filter = request.GET.get('auth', 'ALL').strip()

    if q:
        users_qs = users_qs.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(profile__membership_number__icontains=q)
        )

    if role_filter != 'ALL':
        users_qs = users_qs.filter(profile__role=role_filter)

    if status_filter != 'ALL':
        users_qs = users_qs.filter(profile__membership_status=status_filter)

    if auth_filter == 'GOOGLE':
        users_qs = users_qs.filter(google_account__isnull=False)
    elif auth_filter == 'PASSWORD':
        users_qs = users_qs.filter(google_account__isnull=True)

    # Statistics
    all_users = User.objects.select_related('profile')
    stats = {
        'total_users': all_users.count(),
        'total_admins': all_users.filter(profile__role='ADMIN').count(),
        'total_librarians': all_users.filter(profile__role='LIBRARIAN').count(),
        'total_members': all_users.filter(profile__role='MEMBER').count(),
        'total_active': all_users.filter(profile__membership_status='ACTIVE').count(),
        'total_pending': all_users.filter(profile__membership_status='PENDING').count(),
        'total_suspended': all_users.filter(profile__membership_status='SUSPENDED').count(),
        'total_google': User.objects.filter(google_account__isnull=False).count(),
    }

    context = {
        'users': users_qs[:100],  # Display up to 100 per page
        'stats': stats,
        'q': q,
        'selected_role': role_filter,
        'selected_status': status_filter,
        'selected_auth': auth_filter,
        'role_choices': UserProfile.ROLE_CHOICES,
        'status_choices': UserProfile.STATUS_CHOICES,
        'tier_choices': UserProfile.TIER_CHOICES,
    }
    return render(request, 'accounts/user_management.html', context)


@admin_required
@require_POST
def update_user_permissions_view(request, user_id):
    """
    Administrator action to update a user's role, status, and granular permissions.
    Enforces authorization, self-demotion protection, session revocation on suspension,
    and records an audit log.
    """
    target_user = get_object_or_404(User.objects.select_related('profile'), id=user_id)
    profile = target_user.profile

    new_role = request.POST.get('role', profile.role).strip()
    new_status = request.POST.get('status', profile.membership_status).strip()
    new_tier = request.POST.get('tier', profile.tier).strip()
    is_approved = request.POST.get('is_approved') == 'on'
    can_borrow = request.POST.get('can_borrow') == 'on'
    can_reserve = request.POST.get('can_reserve') == 'on'
    can_access_ebooks = request.POST.get('can_access_ebooks') == 'on'

    # Self-protection: Prevent admin from revoking their own admin role
    if target_user == request.user and new_role != 'ADMIN':
        messages.error(request, "Safety restriction: You cannot remove administrator privileges from your own account.")
        return redirect('accounts:user_management')

    # Validate role choices
    valid_roles = [r[0] for r in UserProfile.ROLE_CHOICES]
    if new_role not in valid_roles:
        new_role = profile.role

    # Validate status choices
    valid_statuses = [s[0] for s in UserProfile.STATUS_CHOICES]
    if new_status not in valid_statuses:
        new_status = profile.membership_status

    # Validate tier choices
    valid_tiers = [t[0] for t in UserProfile.TIER_CHOICES]
    if new_tier not in valid_tiers:
        new_tier = profile.tier

    profile.role = new_role
    profile.membership_status = new_status
    profile.tier = new_tier
    profile.is_approved = is_approved
    profile.can_borrow = can_borrow
    profile.can_reserve = can_reserve
    profile.can_access_ebooks = can_access_ebooks
    profile.save()

    # Sync User.is_staff / User.is_superuser
    if new_role == 'ADMIN':
        target_user.is_staff = True
        target_user.is_superuser = True
        target_user.save(update_fields=['is_staff', 'is_superuser'])
    elif new_role == 'LIBRARIAN':
        target_user.is_staff = True
        target_user.is_superuser = False
        target_user.save(update_fields=['is_staff', 'is_superuser'])
    else:
        target_user.is_staff = False
        target_user.is_superuser = False
        target_user.save(update_fields=['is_staff', 'is_superuser'])

    # If suspended, immediately revoke active sessions
    if new_status == 'SUSPENDED':
        revoked_count = revoke_user_sessions(target_user.id)
        log_activity(
            'ACCOUNT_STATUS_CHANGED',
            f"Admin {request.user.username} suspended account '{target_user.username}' (revoked {revoked_count} sessions)",
            user=request.user,
            request=request
        )
        messages.warning(request, f"User '{target_user.username}' has been suspended. All active sessions were revoked.")
    else:
        log_activity(
            'PERMISSION_CHANGED',
            f"Admin {request.user.username} updated permissions for '{target_user.username}' (Role: {new_role}, Status: {new_status})",
            user=request.user,
            request=request
        )
        messages.success(request, f"Permissions and role for '{target_user.username}' updated successfully.")

    return redirect('accounts:user_management')


@admin_required
@require_POST
def revoke_user_sessions_view(request, user_id):
    """
    Administrator action to forcibly terminate all active sessions for a user.
    """
    target_user = get_object_or_404(User, id=user_id)
    revoked_count = revoke_user_sessions(target_user.id)

    log_activity(
        'SESSION_REVOKED',
        f"Admin {request.user.username} forcibly revoked {revoked_count} sessions for '{target_user.username}'",
        user=request.user,
        request=request
    )
    messages.success(request, f"Terminated {revoked_count} active sessions for '{target_user.username}'.")
    return redirect('accounts:user_management')


@admin_required
@require_POST
def approve_membership_view(request, user_id):
    """
    Administrator / Librarian 1-click action to approve a pending library membership.
    """
    target_user = get_object_or_404(User.objects.select_related('profile'), id=user_id)
    profile = target_user.profile

    profile.is_approved = True
    profile.membership_status = 'ACTIVE'
    profile.can_borrow = True
    profile.can_reserve = True
    profile.can_access_ebooks = True
    profile.save()

    log_activity(
        'MEMBERSHIP_APPROVED',
        f"Membership approved for '{target_user.username}' by {request.user.username}",
        user=request.user,
        request=request
    )

    from notifications.services import create_notification
    create_notification(
        user=target_user,
        title="Membership Approved!",
        message="Your library membership and borrowing privileges have been approved. Welcome to LibrarySphere!",
        type='SUCCESS',
        link='/accounts/profile/'
    )

    messages.success(request, f"Membership for '{target_user.username}' has been approved and activated.")
    return redirect('accounts:user_management')



