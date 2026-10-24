from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Reservation
from catalog.models import Book
from . import services
from core.decorators import librarian_required

def is_librarian(user):
    return user.is_authenticated and (user.is_superuser or (hasattr(user, 'profile') and user.profile.is_librarian()))

@login_required
def my_reservations_view(request):
    tab = request.GET.get('tab', 'active')
    
    all_reservations = Reservation.objects.filter(member=request.user.profile).select_related('book', 'allocated_copy').order_by('-reservation_date')
    
    active_reservations = [r for r in all_reservations if r.status in ['PENDING', 'ALLOCATED']]
    past_reservations = [r for r in all_reservations if r.status in ['FULFILLED', 'CANCELLED', 'EXPIRED']]
    
    # Attach queue tracking metadata to active reservations
    for res in active_reservations:
        res.queue_info = services.get_queue_info(res)

    context = {
        'active_reservations': active_reservations,
        'past_reservations': past_reservations,
        'current_tab': tab,
        'total_active': len(active_reservations),
        'total_past': len(past_reservations),
    }
    return render(request, 'reservations/my_reservations.html', context)

@login_required
def reserve_book_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        try:
            services.create_reservation(request.user.profile, book)
            messages.success(request, f"Successfully reserved '{book.title}'. We will notify you when a copy is available.")
        except ValueError as e:
            messages.error(request, str(e))
            
    return redirect('catalog:detail', book_id=book.id)


@login_required
def cancel_reservation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        try:
            services.cancel_reservation(reservation, request.user)
            messages.success(request, f"Reservation for '{reservation.book.title}' cancelled successfully.")
        except ValueError as e:
            messages.error(request, str(e))
            
    # Redirect based on role
    if request.user.profile.is_librarian():
        return redirect('reservations:manage_reservations')
    return redirect('reservations:my_reservations')


@login_required
def extend_reservation_view(request, reservation_id):
    """Extend the hold pickup window for an allocated reservation."""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Member can only extend their own reservation, librarians can extend any
    if not request.user.profile.is_librarian() and reservation.member.user != request.user:
        messages.error(request, "Permission denied.")
        return redirect('reservations:my_reservations')
        
    if request.method == 'POST':
        try:
            services.extend_reservation_hold(reservation, days=2, user=request.user)
            messages.success(request, f"Hold for '{reservation.book.title}' extended by 2 days until {reservation.expiry_date.strftime('%b %d, %Y')}.")
        except ValueError as e:
            messages.error(request, str(e))
            
    if request.user.profile.is_librarian():
        return redirect('reservations:manage_reservations')
    return redirect('reservations:my_reservations')


from django.db.models import Q

@librarian_required
def manage_reservations_view(request):
    status_filter = request.GET.get('status', 'ACTIVE')
    q = request.GET.get('q', '').strip()

    reservations = Reservation.objects.select_related('member__user', 'book', 'allocated_copy').order_by('-reservation_date')

    if status_filter == 'ACTIVE':
        reservations = reservations.filter(status__in=['PENDING', 'ALLOCATED'])
    elif status_filter and status_filter != 'ALL':
        reservations = reservations.filter(status=status_filter)

    if q:
        reservations = reservations.filter(
            Q(member__user__username__icontains=q) |
            Q(member__user__first_name__icontains=q) |
            Q(member__user__last_name__icontains=q) |
            Q(member__membership_number__icontains=q) |
            Q(book__title__icontains=q)
        )

    # Attach queue info & book availability for each reservation
    res_list = list(reservations)
    for res in res_list:
        res.queue_info = services.get_queue_info(res)
        res.book_avail = services.estimate_availability_for_book(res.book)

    context = {
        'reservations': res_list,
        'selected_status': status_filter,
        'q': q,
        'total_pending': Reservation.objects.filter(status='PENDING').count(),
        'total_allocated': Reservation.objects.filter(status='ALLOCATED').count(),
        'total_fulfilled': Reservation.objects.filter(status='FULFILLED').count(),
        'total_cancelled': Reservation.objects.filter(status='CANCELLED').count(),
        'total_expired': Reservation.objects.filter(status='EXPIRED').count(),
    }
    return render(request, 'reservations/manage_reservations.html', context)


@librarian_required
def batch_expire_reservations_view(request):
    """Run system batch expiration on all unclaimed allocated reservations."""
    if request.method == 'POST':
        expired_count = services.expire_reservations()
        if expired_count > 0:
            messages.success(request, f"Expired {expired_count} overdue holds and re-allocated copies to waiting queue.")
        else:
            messages.info(request, "No overdue holds to expire at this time.")
    return redirect('reservations:manage_reservations')


@librarian_required
def allocate_reservation_view(request, reservation_id):
    """Librarian manual action to attempt allocation of an available physical copy to a pending reservation."""
    reservation = Reservation.objects.filter(id=reservation_id).first()
    if not reservation:
        messages.error(request, "Reservation record not found.")
        return redirect('reservations:manage_reservations')
    if reservation.status != 'PENDING':
        messages.warning(request, f"Reservation is currently {reservation.get_status_display()}, not PENDING allocation.")
        return redirect('reservations:manage_reservations')

    if request.method == 'POST':
        available_copy = reservation.book.copies.filter(status='AVAILABLE').first()
        if available_copy:
            services.allocate_reservation(available_copy)
            messages.success(request, f"Allocated copy '{available_copy.accession_number}' to {reservation.member.user.username}.")
        else:
            messages.error(request, f"No physical copy of '{reservation.book.title}' is currently available on shelf.")
    return redirect('reservations:manage_reservations')


@librarian_required
def fulfill_reservation_view(request, reservation_id):
    reservation = Reservation.objects.filter(id=reservation_id).first()
    if not reservation:
        messages.error(request, "Reservation record not found.")
        return redirect('reservations:manage_reservations')
    if reservation.status != 'ALLOCATED':
        messages.warning(request, f"Reservation is currently {reservation.get_status_display()}, not ALLOCATED for checkout.")
        return redirect('reservations:manage_reservations')
    
    if request.method == 'POST':
        try:
            loan = services.fulfill_reservation(reservation, request.user)
            messages.success(request, f"Reservation fulfilled! Book issued to {reservation.member.user.username}.")
            return redirect('circulation:loan_detail', loan_id=loan.id)
        except ValueError as e:
            messages.error(request, str(e))
            
    return render(request, 'reservations/fulfill_reservation.html', {'reservation': reservation})

