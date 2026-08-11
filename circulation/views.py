from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Loan, Fine
from .forms import IssueBookForm
from . import services

def is_librarian(user):
    return user.is_authenticated and user.profile.is_librarian()

@login_required
@user_passes_test(is_librarian)
def dashboard_view(request):
    active_loans = Loan.objects.filter(status='ISSUED').select_related('member__user', 'book_copy__book').order_by('due_date')
    today = timezone.now().date()
    overdue_loans = [loan for loan in active_loans if loan.due_date < today]
    recent_returns = Loan.objects.filter(status='RETURNED').select_related('member__user', 'book_copy__book').order_by('-return_date')[:5]
    
    context = {
        'active_loans_count': active_loans.count(),
        'overdue_loans_count': len(overdue_loans),
        'recent_returns': recent_returns,
    }
    return render(request, 'circulation/dashboard.html', context)

@login_required
@user_passes_test(is_librarian)
def issue_book_view(request):
    if request.method == 'POST':
        form = IssueBookForm(request.POST)
        if form.is_valid():
            member_profile = form.cleaned_data['membership_number']
            book_copy = form.cleaned_data['accession_number']
            
            try:
                loan = services.issue_book(member_profile, book_copy, request.user)
                messages.success(request, f"Successfully issued '{book_copy.book.title}' to {member_profile.user.get_full_name()}. Due on {loan.due_date}.")
                return redirect('circulation:loan_detail', loan_id=loan.id)
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = IssueBookForm()
        
    return render(request, 'circulation/issue_book.html', {'form': form})

@login_required
@user_passes_test(is_librarian)
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

@login_required
@user_passes_test(is_librarian)
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


@login_required
@user_passes_test(is_librarian)
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
@user_passes_test(is_librarian)
def pay_fine_view(request, fine_id):
    """Record payment for an overdue fine."""
    fine = get_object_or_404(Fine.objects.select_related('loan__member__user', 'loan__book_copy__book'), id=fine_id)

    if fine.status == 'PAID':
        messages.info(request, "This fine has already been paid.")
        return redirect(request.META.get('HTTP_REFERER', 'circulation:fine_list'))

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'CASH')
        notes = request.POST.get('notes', '')

        fine.status = 'PAID'
        fine.notes = f"Paid via {payment_method}. {notes}".strip()
        fine.save()

        member_name = fine.loan.member.user.get_full_name() or fine.loan.member.user.username
        messages.success(request, f"Payment of ${fine.amount} for {member_name} recorded successfully.")

        # Notify member of fine settlement
        from notifications.services import create_notification
        create_notification(
            user=fine.loan.member.user,
            title="Fine Payment Received",
            message=f"Your fine payment of ${fine.amount} for '{fine.loan.book_copy.book.title}' has been processed.",
            type="SUCCESS",
            link="/accounts/profile/"
        )

        return redirect(request.META.get('HTTP_REFERER', 'circulation:fine_list'))

    return render(request, 'circulation/pay_fine.html', {'fine': fine})


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

