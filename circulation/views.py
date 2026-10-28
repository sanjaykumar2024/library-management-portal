from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Loan, Fine
from .forms import IssueBookForm
from . import services
from core.decorators import librarian_required

def is_librarian(user):
    return user.is_authenticated and (user.is_superuser or (hasattr(user, 'profile') and user.profile.is_librarian()))

from django.db import models
from django.db.models import Sum, Q
from decimal import Decimal
from accounts.models import UserProfile
from catalog.models import BookCopy

@librarian_required
def dashboard_view(request):
    today = timezone.now().date()
    active_loans_qs = list(Loan.objects.filter(status='ISSUED').select_related('member__user', 'book_copy__book').order_by('due_date'))
    overdue_loans = []
    total_accrued_overdue_fines = Decimal('0.00')

    for loan in active_loans_qs:
        if loan.due_date < today:
            days = (today - loan.due_date).days
            est = Decimal(days) * services.FINE_PER_DAY
            loan.overdue_days = days
            loan.estimated_fine = est
            total_accrued_overdue_fines += est
            overdue_loans.append(loan)
        else:
            loan.overdue_days = 0
            loan.estimated_fine = Decimal('0.00')

    recent_returns = Loan.objects.filter(status='RETURNED').select_related('member__user', 'book_copy__book', 'fine').order_by('-return_date')[:6]
    
    total_pending_fines = Fine.objects.filter(status='PENDING').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_paid_fines = Fine.objects.filter(status='PAID').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    context = {
        'today': today,
        'active_loans': active_loans_qs[:10],
        'active_loans_count': len(active_loans_qs),
        'overdue_loans_count': len(overdue_loans),
        'total_accrued_overdue_fines': total_accrued_overdue_fines,
        'recent_returns': recent_returns,
        'total_pending_fines': total_pending_fines,
        'total_paid_fines': total_paid_fines,
    }
    return render(request, 'circulation/dashboard.html', context)


@librarian_required
def issue_book_view(request):
    preset_copy = request.GET.get('copy', '').strip()
    preset_member = request.GET.get('member', '').strip()

    if request.method == 'POST':
        form = IssueBookForm(request.POST)
        if form.is_valid():
            member_profile = form.cleaned_data['membership_number']
            book_copy = form.cleaned_data['accession_number']
            
            try:
                loan = services.issue_book(member_profile, book_copy, request.user)
                messages.success(request, f"Successfully issued '{book_copy.book.title}' to {member_profile.user.get_full_name() or member_profile.user.username}. Due on {loan.due_date.strftime('%b %d, %Y')}.")
                return redirect('circulation:loan_detail', loan_id=loan.id)
            except ValueError as e:
                messages.error(request, str(e))
    else:
        initial_data = {}
        if preset_copy:
            initial_data['accession_number'] = preset_copy
        if preset_member:
            initial_data['membership_number'] = preset_member
        form = IssueBookForm(initial=initial_data)
        
    available_copies = BookCopy.objects.filter(status='AVAILABLE').select_related('book').order_by('book__title')[:12]
    active_members = UserProfile.objects.filter(role='MEMBER', membership_status='ACTIVE').select_related('user').order_by('user__first_name', 'user__username')[:12]

    context = {
        'form': form,
        'available_copies': available_copies,
        'active_members': active_members,
        'preset_copy': preset_copy,
        'preset_member': preset_member,
    }
    return render(request, 'circulation/issue_book.html', context)


@librarian_required
def return_book_list_view(request):
    q = request.GET.get('q', '')
    active_loans = Loan.objects.filter(status='ISSUED').select_related('member__user', 'book_copy__book').order_by('due_date')
    
    if q:
        active_loans = active_loans.filter(
            book_copy__accession_number__icontains=q
        ) | active_loans.filter(
            member__membership_number__icontains=q
        )
        
    return render(request, 'circulation/return_list.html', {'active_loans': active_loans, 'q': q})

@librarian_required
def process_return_view(request, loan_id):
    loan = get_object_or_404(Loan.objects.select_related('member__user', 'book_copy__book'), id=loan_id, status='ISSUED')
    
    if request.method == 'POST':
        copy_status = request.POST.get('copy_status', 'AVAILABLE')
        notes = request.POST.get('condition_notes', '')
        try:
            services.return_book(loan, request.user, copy_status=copy_status, notes=notes)
            messages.success(request, f"Successfully processed return for '{loan.book_copy.book.title}' (Copy status: {copy_status}).")
            if hasattr(loan, 'fine') and loan.fine:
                messages.warning(request, f"Fine of ${loan.fine.amount} has been generated.")
            return redirect('circulation:return_list')
        except ValueError as e:
            messages.error(request, str(e))
            
    return render(request, 'circulation/process_return.html', {'loan': loan})

@login_required
def loan_detail_view(request, loan_id):
    loan = get_object_or_404(Loan.objects.select_related('member__user', 'book_copy__book').prefetch_related('fine'), id=loan_id)
    
    # Check permissions
    if not request.user.profile.is_librarian() and loan.member.user != request.user:
        messages.error(request, "You do not have permission to view this loan.")
        return redirect('core:dashboard')
        
    return render(request, 'circulation/loan_detail.html', {'loan': loan})

@login_required
def renew_book_view(request, loan_id):
    loan = get_object_or_404(Loan.objects.select_related('member__user', 'book_copy__book'), id=loan_id, status='ISSUED')
    
    if not request.user.profile.is_librarian() and loan.member.user != request.user:
        messages.error(request, "You do not have permission to renew this loan.")
        return redirect('core:dashboard')
        
    if request.method == 'POST':
        try:
            services.renew_book(loan)
            messages.success(request, f"Successfully renewed '{loan.book_copy.book.title}'. New due date: {loan.due_date}.")
        except ValueError as e:
            messages.error(request, str(e))
            
    return redirect('circulation:loan_detail', loan_id=loan.id)


@librarian_required
def fine_list_view(request):
    """View all pending and paid fines at the circulation desk."""
    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '')

    fines = Fine.objects.select_related('loan__member__user', 'loan__book_copy__book').order_by('-created_at')

    if status_filter:
        fines = fines.filter(status=status_filter)
    if q:
        fines = fines.filter(
            loan__member__membership_number__icontains=q
        ) | fines.filter(
            loan__member__user__username__icontains=q
        ) | fines.filter(
            loan__book_copy__book__title__icontains=q
        )

    context = {
        'fines': fines,
        'selected_status': status_filter,
        'q': q,
    }
    return render(request, 'circulation/fine_list.html', context)


@login_required
def pay_fine_view(request, fine_id):
    """Record payment for an overdue fine (Staff collection at desk or Patron self-pay)."""
    fine = get_object_or_404(Fine.objects.select_related('loan__member__user', 'loan__book_copy__book'), id=fine_id)

    # Permission check: must be a librarian/admin or the patron who owns the fine
    is_lib = request.user.profile.is_librarian() if hasattr(request.user, 'profile') else False
    if not is_lib and fine.loan.member.user != request.user:
        messages.error(request, "Access denied. You can only view and pay your own fines.")
        return redirect('core:dashboard')

    if fine.status == 'PAID':
        messages.info(request, "This fine has already been paid.")
        if is_lib:
            return redirect(request.META.get('HTTP_REFERER', 'circulation:fine_list'))
        return redirect('accounts:profile')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'CASH' if is_lib else 'UPI')
        notes = request.POST.get('notes', '')

        fine.status = 'PAID'
        fine.notes = f"Paid via {payment_method}. {notes}".strip()
        fine.save()

        member_name = fine.loan.member.user.get_full_name() or fine.loan.member.user.username
        messages.success(request, f"Payment of ₹{fine.amount} for '{fine.loan.book_copy.book.title}' recorded successfully.")

        try:
            from core.models import log_activity
            log_activity('FINE_PAID', f"Fine payment of ₹{fine.amount} for '{fine.loan.book_copy.book.title}' recorded ({member_name})", user=request.user, request=request)
        except Exception:
            pass

        # Notify member of fine settlement
        from notifications.services import create_notification

        create_notification(
            user=fine.loan.member.user,
            title="Fine Payment Received",
            message=f"Your fine payment of ₹{fine.amount} for '{fine.loan.book_copy.book.title}' has been processed.",
            type="SUCCESS",
            link="/accounts/profile/"
        )

        if not is_lib:
            return redirect('accounts:profile')
        return redirect(request.META.get('HTTP_REFERER', 'circulation:fine_list'))

    return render(request, 'circulation/pay_fine.html', {'fine': fine, 'is_librarian': is_lib})


@login_required
def loan_receipt_view(request, loan_id):
    """Printable issue/loan transaction slip."""
    loan = get_object_or_404(Loan.objects.select_related('member__user', 'book_copy__book', 'fine'), id=loan_id)
    if not request.user.profile.is_librarian() and loan.member.user != request.user:
        messages.error(request, "Access denied.")
        return redirect('core:dashboard')
    return render(request, 'circulation/receipt_loan.html', {'loan': loan})


@login_required
def fine_receipt_view(request, fine_id):
    """Printable fine payment receipt."""
    fine = get_object_or_404(Fine.objects.select_related('loan__member__user', 'loan__book_copy__book'), id=fine_id)
    if not request.user.profile.is_librarian() and fine.loan.member.user != request.user:
        messages.error(request, "Access denied.")
        return redirect('core:dashboard')
    return render(request, 'circulation/receipt_fine.html', {'fine': fine})


@librarian_required
def trigger_overdue_check_view(request):
    """Librarian action to trigger batch overdue scan and notification dispatch."""
    if request.method == 'POST':
        result = services.scan_and_notify_overdue_loans()
        messages.success(
            request,
            f"Overdue scan completed: {result['overdue_count']} overdue alert(s) sent, "
            f"{result['reminder_count']} due-soon reminder(s) sent. "
            f"Estimated accrued fines: ₹{result['total_estimated_fines']:.2f}."
        )
    return redirect('circulation:dashboard')


@librarian_required
def send_overdue_notice_view(request, loan_id):
    """Sends an immediate targeted reminder notice to a specific loan's member."""
    loan = get_object_or_404(Loan.objects.select_related('member__user', 'book_copy__book'), id=loan_id, status='ISSUED')
    today = timezone.now().date()
    from notifications.services import create_notification
    
    if loan.due_date < today:
        days = (today - loan.due_date).days
        fine = Decimal(days) * services.FINE_PER_DAY
        create_notification(
            user=loan.member.user,
            title="⚠️ Urgent: Overdue Book Notice",
            message=f"Official Notice from Circulation Desk: '{loan.book_copy.book.title}' is {days} day(s) overdue. Current accrued fine: ₹{fine:.2f}. Please return this copy immediately to avoid suspension.",
            type="WARNING",
            link="/accounts/profile/"
        )
        messages.success(request, f"Overdue notice sent to {loan.member.user.get_full_name() or loan.member.user.username}.")
    else:
        days_left = (loan.due_date - today).days
        create_notification(
            user=loan.member.user,
            title="📚 Library Loan Reminder",
            message=f"Friendly Reminder: '{loan.book_copy.book.title}' is due in {days_left} day(s) on {loan.due_date.strftime('%b %d, %Y')}.",
            type="INFO",
            link="/accounts/profile/"
        )
        messages.success(request, f"Reminder notice sent to {loan.member.user.get_full_name() or loan.member.user.username}.")
        
    return redirect('circulation:dashboard')


# ── Pillar 2: Self-Service Kiosk & Barcode APIs ───────────────────────────────

from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction


def kiosk_view(request):
    """Self-Service Touchscreen Checkout Kiosk with Camera Barcode/QR Scanner."""
    current_profile = None
    if request.user.is_authenticated:
        current_profile = getattr(request.user, 'profile', None)

    # Provide sample members and sample available copies for quick testing/demo
    sample_members = UserProfile.objects.filter(
        membership_status='ACTIVE'
    ).select_related('user')[:3]

    sample_copies = BookCopy.objects.filter(
        status='AVAILABLE'
    ).select_related('book')[:4]

    return render(request, 'circulation/kiosk.html', {
        'today': timezone.now().date(),
        'default_due_date': timezone.now().date() + timezone.timedelta(days=14),
        'current_user_profile': current_profile,
        'sample_members': sample_members,
        'sample_copies': sample_copies,
    })


def api_kiosk_lookup_member(request):
    """Lookup member profile by digital card QR / membership number / username."""
    query = (request.GET.get('q') or request.GET.get('query') or request.GET.get('membership_number') or '').strip()
    if not query:
        return JsonResponse({'success': False, 'error': 'Membership number is required.'}, status=400)

    profile = UserProfile.objects.filter(
        models.Q(membership_number__iexact=query) | models.Q(user__username__iexact=query)
    ).select_related('user').first()

    if not profile:
        return JsonResponse({'success': False, 'error': f"No member found with ID '{query}'."}, status=404)

    can_borrow, reason = services.can_member_borrow(profile)
    active_loans_count = Loan.objects.filter(member=profile, status='ISSUED').count()
    pending_fines = Fine.objects.filter(loan__member=profile, status='PENDING').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    return JsonResponse({
        'success': True,
        'member': {
            'id': profile.id,
            'name': profile.user.get_full_name() or profile.user.username,
            'username': profile.user.username,
            'membership_number': profile.membership_number,
            'status': profile.membership_status,
            'tier': profile.get_tier_display(),
            'active_loans_count': active_loans_count,
            'max_books_allowed': profile.max_books_allowed,
            'remaining_quota': max(0, profile.max_books_allowed - active_loans_count),
            'pending_fines': float(pending_fines),
            'can_borrow': can_borrow,
            'block_reason': reason if not can_borrow else None,
            'avatar': profile.profile_image.url if profile.profile_image else None,
        }
    })


def api_kiosk_lookup_book(request):
    """Lookup physical book copy by barcode / accession number / ISBN / Title."""
    query = (request.GET.get('barcode') or request.GET.get('q') or request.GET.get('query') or request.GET.get('accession_number') or '').strip()
    if not query:
        return JsonResponse({'success': False, 'error': 'Accession barcode or ISBN is required.'}, status=400)

    # 1. Exact accession number match
    copy = BookCopy.objects.filter(
        accession_number__iexact=query
    ).select_related('book', 'book__category').prefetch_related('book__authors').first()

    # 2. ISBN match (prefer available copy)
    if not copy:
        copy = BookCopy.objects.filter(
            book__isbn__iexact=query,
            status='AVAILABLE'
        ).select_related('book', 'book__category').prefetch_related('book__authors').first()
        if not copy:
            copy = BookCopy.objects.filter(
                book__isbn__iexact=query
            ).select_related('book', 'book__category').prefetch_related('book__authors').first()

    # 3. Title match (prefer available copy)
    if not copy:
        copy = BookCopy.objects.filter(
            book__title__icontains=query,
            status='AVAILABLE'
        ).select_related('book', 'book__category').prefetch_related('book__authors').first()
        if not copy:
            copy = BookCopy.objects.filter(
                book__title__icontains=query
            ).select_related('book', 'book__category').prefetch_related('book__authors').first()

    if not copy:
        return JsonResponse({'success': False, 'error': f"No book copy found with barcode or title '{query}'."}, status=404)

    authors = ", ".join(a.full_name for a in copy.book.authors.all()) or "Unknown Author"
    cover_url = copy.book.cover_image.url if copy.book.cover_image else None

    return JsonResponse({
        'success': True,
        'copy': {
            'id': copy.id,
            'accession_number': copy.accession_number,
            'status': copy.status,
            'is_available': copy.status == 'AVAILABLE',
            'title': copy.book.title,
            'author': authors,
            'isbn': copy.book.isbn,
            'category': copy.book.category.name if copy.book.category else 'General',
            'shelf_location': copy.shelf_location,
            'cover_url': cover_url,
        }
    })


@require_POST
def api_kiosk_checkout(request):
    """Process atomic batch checkout for a member at the kiosk."""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON body.'}, status=400)

    membership_input = str(data.get('membership_number') or data.get('member_id') or '').strip()
    copy_accessions = data.get('accession_numbers', [])

    if not membership_input:
        return JsonResponse({'success': False, 'error': 'Membership number is required.'}, status=400)

    if not copy_accessions or not isinstance(copy_accessions, list):
        return JsonResponse({'success': False, 'error': 'Please scan at least one book copy to checkout.'}, status=400)

    profile = None
    if membership_input.isdigit():
        profile = UserProfile.objects.filter(id=int(membership_input)).first()
    if not profile:
        profile = UserProfile.objects.filter(
            models.Q(membership_number__iexact=membership_input) | models.Q(user__username__iexact=membership_input)
        ).first()

    if not profile:
        return JsonResponse({'success': False, 'error': 'Invalid member identification.'}, status=404)

    # Permission check: If logged in, staff can checkout for anyone; normal member for themselves.
    # If not logged in, kiosk mode checkout operates using verified membership card.
    if request.user.is_authenticated:
        user_prof = getattr(request.user, 'profile', None)
        is_staff = user_prof and (user_prof.is_librarian() or user_prof.is_admin())
        if not is_staff and profile.user != request.user:
            return JsonResponse({'success': False, 'error': 'You can only check out books for your own account.'}, status=403)

    can_borrow, reason = services.can_member_borrow(profile)
    if not can_borrow:
        return JsonResponse({'success': False, 'error': reason}, status=400)

    active_count = Loan.objects.filter(member=profile, status='ISSUED').count()
    if active_count + len(copy_accessions) > profile.max_books_allowed:
        return JsonResponse({
            'success': False,
            'error': f"Quota exceeded. You can only borrow {profile.max_books_allowed - active_count} more book(s)."
        }, status=400)

    loans_created = []
    issued_by_user = request.user if request.user.is_authenticated else None

    try:
        with transaction.atomic():
            for acc in copy_accessions:
                copy = BookCopy.objects.select_for_update().filter(accession_number__iexact=acc).first()
                if not copy:
                    raise ValueError(f"Book copy '{acc}' was not found.")
                if copy.status != 'AVAILABLE':
                    raise ValueError(f"Copy '{copy.accession_number}' ({copy.book.title}) is not available (Status: {copy.get_status_display()}).")

                loan = services.issue_book(profile, copy, issued_by_user)
                loans_created.append({
                    'id': loan.id,
                    'title': copy.book.title,
                    'accession_number': copy.accession_number,
                    'issue_date': loan.issue_date.strftime('%Y-%m-%d'),
                    'due_date': loan.due_date.strftime('%B %d, %Y'),
                    'receipt_url': f"/circulation/loan/{loan.id}/receipt/",
                })
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Checkout transaction failed: {str(e)}'}, status=500)

    try:
        from core.models import log_activity
        titles = ", ".join(f"'{l['title']}'" for l in loans_created)
        log_activity('LOAN_ISSUED', f"Kiosk checkout: {len(loans_created)} book(s) issued to {profile.user.username} ({titles})", user=request.user if request.user.is_authenticated else profile.user, request=request)
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'message': f"Successfully checked out {len(loans_created)} book(s)!",
        'loans': loans_created,
        'member_name': profile.user.get_full_name() or profile.user.username,
    })


