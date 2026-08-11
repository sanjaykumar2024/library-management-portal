from django.conf import settings
from django.utils import timezone
from .models import Loan, Fine
from decimal import Decimal
import datetime

# Fetch settings with fallbacks
MAX_LOANS_PER_MEMBER = getattr(settings, 'MAX_LOANS_PER_MEMBER', 3)
LOAN_PERIOD_DAYS = getattr(settings, 'LOAN_PERIOD_DAYS', 14)
MAX_RENEWALS = getattr(settings, 'MAX_RENEWALS', 2)
FINE_PER_DAY = Decimal(getattr(settings, 'FINE_PER_DAY', '5.00'))

def can_member_borrow(member_profile):
    """Check if member is active, under loan limit, and has no unpaid pending fines."""
    if member_profile.membership_status != 'ACTIVE':
        return False, "Membership is not active."

    # Check for pending unpaid fines
    pending_fines = Fine.objects.filter(loan__member=member_profile, status='PENDING')
    if pending_fines.exists():
        total_pending = sum(f.amount for f in pending_fines)
        return False, f"Member has unpaid pending fines totaling ${total_pending:.2f}. All fines must be paid before borrowing new books."
        
    active_loans_count = Loan.objects.filter(member=member_profile, status='ISSUED').count()
    if active_loans_count >= MAX_LOANS_PER_MEMBER:
        return False, f"Member has reached the maximum limit of {MAX_LOANS_PER_MEMBER} active loans."
        
    return True, ""


def issue_book(member_profile, book_copy, librarian_user):
    """
    Issues a physical book to a member.
    Validates membership, loan count, and book copy availability.
    """
    is_eligible, reason = can_member_borrow(member_profile)
    if not is_eligible:
        raise ValueError(reason)

    if book_copy.status != 'AVAILABLE':
        raise ValueError(f"Book copy is currently {book_copy.get_status_display()}.")

    # Create the loan
    due_date = timezone.now().date() + datetime.timedelta(days=LOAN_PERIOD_DAYS)
    
    loan = Loan.objects.create(
        member=member_profile,
        book_copy=book_copy,
        issued_by=librarian_user,
        due_date=due_date
    )
    
    # Update book copy status
    book_copy.status = 'ISSUED'
    book_copy.save()
    
    return loan


def return_book(loan, librarian_user, copy_status='AVAILABLE', notes=''):
    """
    Marks a loan as returned, calculates fines, and updates book copy status.
    Supports marking copies as LOST, DAMAGED, or MAINTENANCE.
    """
    if loan.status == 'RETURNED':
        raise ValueError("This loan has already been returned.")
        
    today = timezone.now().date()
    loan.status = 'RETURNED'
    loan.return_date = today
    loan.returned_to = librarian_user
    loan.save()
    
    # Calculate overdue fine
    fine_amount = Decimal('0.00')
    overdue_days = 0
    if today > loan.due_date:
        overdue_days = (today - loan.due_date).days
        fine_amount = Decimal(overdue_days) * FINE_PER_DAY

    # Add lost book fee if marked lost
    if copy_status == 'LOST':
        fine_amount += Decimal('25.00')  # $25 replacement fee
        notes = f"Book marked LOST. Includes $25.00 replacement fee. {notes}".strip()

    if fine_amount > Decimal('0.00'):
        Fine.objects.create(
            loan=loan,
            amount=fine_amount,
            overdue_days=overdue_days,
            status='PENDING',
            notes=notes
        )
        
    # Update book copy status
    book_copy = loan.book_copy
    book_copy.status = copy_status
    if notes:
        book_copy.condition = notes
    book_copy.save()
    
    # Check reservation queue — allocate to next waiting member if copy is available
    if copy_status == 'AVAILABLE':
        from reservations.services import allocate_reservation
        allocate_reservation(book_copy)
    
    return loan


def renew_book(loan):
    """
    Renews a loan if constraints are met.
    """
    if loan.status == 'RETURNED':
        raise ValueError("Cannot renew a returned loan.")
        
    if loan.renewal_count >= MAX_RENEWALS:
        raise ValueError(f"Maximum of {MAX_RENEWALS} renewals reached.")
        
    # Block renewal if someone is waiting for this book
    from reservations.models import Reservation
    has_pending = Reservation.objects.filter(
        book=loan.book_copy.book,
        status='PENDING'
    ).exists()
    if has_pending:
        raise ValueError("Cannot renew — another member has a pending reservation for this book.")
    
    loan.due_date = loan.due_date + datetime.timedelta(days=LOAN_PERIOD_DAYS)
    loan.renewal_count += 1
    loan.save()
    
    return loan
