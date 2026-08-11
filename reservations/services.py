from django.conf import settings
from django.utils import timezone
import datetime
from .models import Reservation
from catalog.models import BookCopy
from circulation.services import issue_book

MAX_RESERVATIONS_PER_MEMBER = getattr(settings, 'MAX_RESERVATIONS_PER_MEMBER', 2)
RESERVATION_EXPIRY_DAYS = getattr(settings, 'RESERVATION_EXPIRY_DAYS', 2)

def can_member_reserve(member_profile):
    """Check if member is active and under reservation limit."""
    if member_profile.membership_status != 'ACTIVE':
        return False, "Membership is not active."
        
    active_reservations = Reservation.objects.filter(
        member=member_profile, 
        status__in=['PENDING', 'ALLOCATED']
    ).count()
    
    if active_reservations >= MAX_RESERVATIONS_PER_MEMBER:
        return False, f"Member has reached the maximum limit of {MAX_RESERVATIONS_PER_MEMBER} active reservations."
        
    return True, ""


def create_reservation(member_profile, book):
    """
    Creates a new reservation for a book.
    If an available copy exists, allocates it immediately.
    """
    is_eligible, reason = can_member_reserve(member_profile)
    if not is_eligible:
        raise ValueError(reason)

    # Check if member already has a pending/allocated reservation for this book
    existing = Reservation.objects.filter(
        member=member_profile, 
        book=book, 
        status__in=['PENDING', 'ALLOCATED']
    ).exists()
    
    if existing:
        raise ValueError("You already have an active reservation for this book.")
        
    # Check if member currently has a copy of this book issued
    from circulation.models import Loan
    has_loan = Loan.objects.filter(
        member=member_profile,
        book_copy__book=book,
        status='ISSUED'
    ).exists()
    
    if has_loan:
        raise ValueError("You currently have a copy of this book issued to you.")

    reservation = Reservation.objects.create(
        member=member_profile,
        book=book,
        status='PENDING'
    )
    
    # Try to allocate immediately if an available copy exists
    available_copy = BookCopy.objects.filter(book=book, status='AVAILABLE').first()
    if available_copy:
        allocate_reservation(available_copy)
        
    return reservation


def allocate_reservation(book_copy):
    """
    Called when a book copy becomes available (e.g. returned or newly added).
    Finds the oldest pending reservation and allocates this copy to it.
    """
    if book_copy.status != 'AVAILABLE':
        return False
        
    pending_res = Reservation.objects.filter(
        book=book_copy.book, 
        status='PENDING'
    ).order_by('reservation_date').first()
    
    if pending_res:
        pending_res.status = 'ALLOCATED'
        pending_res.allocated_copy = book_copy
        pending_res.expiry_date = timezone.now() + datetime.timedelta(days=RESERVATION_EXPIRY_DAYS)
        pending_res.save()
        
        book_copy.status = 'RESERVED'
        book_copy.save()
        
        # NOTE: Notification should be triggered here
        from notifications.services import create_notification
        create_notification(
            user=pending_res.member.user,
            title="Reservation Available",
            message=f"A copy of '{book_copy.book.title}' is now available for you to pick up. Please collect it by {pending_res.expiry_date.strftime('%B %d, %Y')}.",
            type='INFO',
            link=f"/catalog/book/{book_copy.book.id}/"
        )
        return True
        
    return False


def fulfill_reservation(reservation, librarian_user):
    """
    Librarian hands the allocated book to the member.
    Converts the reservation to FULFILLED and issues the book via Circulation.
    """
    if reservation.status != 'ALLOCATED':
        raise ValueError("Only ALLOCATED reservations can be fulfilled.")
        
    if not reservation.allocated_copy:
        raise ValueError("No copy is allocated to this reservation.")
        
    # To issue it, we must first mark the copy as AVAILABLE temporarily 
    # so circulation services doesn't block it.
    copy = reservation.allocated_copy
    copy.status = 'AVAILABLE'
    copy.save()
    
    # Issue the book
    try:
        loan = issue_book(reservation.member, copy, librarian_user)
        reservation.status = 'FULFILLED'
        reservation.save()
        return loan
    except ValueError as e:
        # Revert copy status if issue fails
        copy.status = 'RESERVED'
        copy.save()
        raise e


def cancel_reservation(reservation, user):
    """
    Member or Librarian cancels the reservation.
    """
    if reservation.status not in ['PENDING', 'ALLOCATED']:
        raise ValueError("Cannot cancel this reservation. It is not active.")
        
    # If a member is canceling, ensure they own it
    if not user.profile.is_librarian() and reservation.member.user != user:
        raise ValueError("You do not have permission to cancel this reservation.")
        
    was_allocated = (reservation.status == 'ALLOCATED')
    allocated_copy = reservation.allocated_copy
    
    reservation.status = 'CANCELLED'
    reservation.save()
    
    # If a copy was tied up, release it and allocate to the next person in line
    if was_allocated and allocated_copy:
        allocated_copy.status = 'AVAILABLE'
        allocated_copy.save()
        allocate_reservation(allocated_copy)
        
    return True


def expire_reservations():
    """
    Background task to expire ALLOCATED reservations that have passed their expiry_date.
    """
    now = timezone.now()
    expired_reservations = Reservation.objects.filter(
        status='ALLOCATED',
        expiry_date__lt=now
    )
    
    count = 0
    for res in expired_reservations:
        copy = res.allocated_copy
        res.status = 'EXPIRED'
        res.save()
        count += 1
        
        # Release the copy
        if copy:
            copy.status = 'AVAILABLE'
            copy.save()
            allocate_reservation(copy)  # Pass to next person
            
    return count
