from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login

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


