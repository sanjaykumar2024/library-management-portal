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
    """Check if member is active, approved, permitted, under loan limit, and has no unpaid pending fines."""
    if member_profile.membership_status == 'SUSPENDED':
        return False, "Your account has been suspended by the library administration."
    if member_profile.membership_status == 'PENDING' or not getattr(member_profile, 'is_approved', True):
        return False, "Your library membership is pending administrator approval."
    if member_profile.membership_status != 'ACTIVE':
        return False, "Membership is not active."
    if not getattr(member_profile, 'can_borrow', True):
        return False, "Borrowing privileges have been disabled for this account."

    # Check for pending unpaid fines
    pending_fines = Fine.objects.filter(loan__member=member_profile, status='PENDING')
    if pending_fines.exists():
        total_pending = sum(f.amount for f in pending_fines)
        return False, f"Member has unpaid pending fines totaling ${total_pending:.2f}. All fines must be paid before borrowing new books."
        
    allowed_limit = getattr(member_profile, 'max_books_allowed', MAX_LOANS_PER_MEMBER)
    active_loans_count = Loan.objects.filter(member=member_profile, status='ISSUED').count()
    if active_loans_count >= allowed_limit:
        tier_name = getattr(member_profile, 'get_tier_display', lambda: 'Standard')()
        return False, f"Member has reached the maximum limit of {allowed_limit} active loans for their {tier_name} tier."
        
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
    auth_user = librarian_user if (librarian_user and getattr(librarian_user, 'is_authenticated', False)) else None
    
    loan = Loan.objects.create(
        member=member_profile,
        book_copy=book_copy,
        issued_by=auth_user,
        due_date=due_date
    )
    
    # Update book copy status
    book_copy.status = 'ISSUED'
    book_copy.save()

    try:
        from core.models import log_activity
        log_activity('LOAN_ISSUED', f"Issued '{book_copy.book.title}' (Acc: {book_copy.accession_number}) to {member_profile.user.username}", user=auth_user or member_profile.user)
    except Exception:
        pass
    
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
        fine, created = Fine.objects.get_or_create(
            loan=loan,
            defaults={
                'amount': fine_amount,
                'overdue_days': overdue_days,
                'status': 'PENDING',
                'notes': notes
            }
        )
        if not created:
            fine.amount = fine_amount
            fine.overdue_days = overdue_days
            if notes:
                fine.notes = notes
            fine.save()

        
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

    try:
        from core.models import log_activity
        log_activity('LOAN_RETURNED', f"Returned '{loan.book_copy.book.title}' (Acc: {loan.book_copy.accession_number}) by {loan.member.user.username}", user=librarian_user)
    except Exception:
        pass
    
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

    try:
        from core.models import log_activity
        log_activity('LOAN_RENEWED', f"Renewed '{loan.book_copy.book.title}' for {loan.member.user.username}", user=loan.member.user)
    except Exception:
        pass
    
    return loan



def scan_and_notify_overdue_loans():
    """
    Scans all active loans for overdue or soon-due-date items.
    - Overdue loans: Creates notifications warning of accrued fines.
    - Due within 48 hours: Creates reminder notifications.
    Returns a dict with summary counts.
    """
    from notifications.services import create_notification
    
    today = timezone.now().date()
    warning_threshold = today + datetime.timedelta(days=2)  # 48 hours ahead
    
    active_loans = Loan.objects.filter(status='ISSUED').select_related(
        'member__user', 'book_copy__book'
    )
    
    overdue_count = 0
    reminder_count = 0
    total_estimated_fines = Decimal('0.00')
    overdue_details = []
    
    for loan in active_loans:
        book_title = loan.book_copy.book.title
        member_name = loan.member.user.get_full_name() or loan.member.user.username
        
        if loan.due_date < today:
            # OVERDUE — calculate estimated accrued fine
            overdue_days = (today - loan.due_date).days
            estimated_fine = Decimal(overdue_days) * FINE_PER_DAY
            total_estimated_fines += estimated_fine
            overdue_count += 1
            
            overdue_details.append({
                'loan': loan,
                'overdue_days': overdue_days,
                'estimated_fine': estimated_fine,
            })
            
            create_notification(
                user=loan.member.user,
                title="⚠️ Overdue Book Alert",
                message=(
                    f"'{book_title}' was due on {loan.due_date.strftime('%b %d, %Y')} "
                    f"and is now {overdue_days} day(s) overdue. "
                    f"Estimated fine: ₹{estimated_fine:.2f} (₹{FINE_PER_DAY}/day). "
                    f"Please return the book to the circulation desk promptly."
                ),
                type="WARNING",
                link="/accounts/profile/"
            )
            
        elif loan.due_date <= warning_threshold:
            # DUE SOON — send a reminder
            days_left = (loan.due_date - today).days
            reminder_count += 1
            
            create_notification(
                user=loan.member.user,
                title="📚 Due Date Reminder",
                message=(
                    f"'{book_title}' is due on {loan.due_date.strftime('%b %d, %Y')} "
                    f"({days_left} day(s) remaining). "
                    f"Please return or renew the book before the due date to avoid fines."
                ),
                type="INFO",
                link="/accounts/profile/"
            )
    
    return {
        'overdue_count': overdue_count,
        'reminder_count': reminder_count,
        'total_estimated_fines': total_estimated_fines,
        'overdue_details': overdue_details,
    }

