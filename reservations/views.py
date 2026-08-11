from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Reservation
from catalog.models import Book
from . import services

def is_librarian(user):
    return user.is_authenticated and user.profile.is_librarian()

@login_required
def my_reservations_view(request):
    reservations = Reservation.objects.filter(member=request.user.profile).exclude(status='FULFILLED').select_related('book').order_by('-reservation_date')
    return render(request, 'reservations/my_reservations.html', {'reservations': reservations})

@login_required
def reserve_book_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        try:
            services.create_reservation(request.user.profile, book)
            messages.success(request, f"Successfully reserved '{book.title}'. We will notify you when a copy is available.")
        except ValueError as e:
            messages.error(request, str(e))
            
    return redirect('catalog:detail', pk=book.id)

@login_required
def cancel_reservation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        try:
            services.cancel_reservation(reservation, request.user)
            messages.success(request, "Reservation cancelled successfully.")
        except ValueError as e:
            messages.error(request, str(e))
            
    # Redirect based on role
    if request.user.profile.is_librarian():
        return redirect('reservations:manage_reservations')
    return redirect('reservations:my_reservations')

@login_required
@user_passes_test(is_librarian)
def manage_reservations_view(request):
    active_reservations = Reservation.objects.filter(status__in=['PENDING', 'ALLOCATED']).select_related('member__user', 'book', 'allocated_copy').order_by('reservation_date')
    return render(request, 'reservations/manage_reservations.html', {'active_reservations': active_reservations})

@login_required
@user_passes_test(is_librarian)
def fulfill_reservation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, status='ALLOCATED')
    
    if request.method == 'POST':
        try:
            loan = services.fulfill_reservation(reservation, request.user)
            messages.success(request, f"Reservation fulfilled! Book issued to {reservation.member.user.username}.")
            return redirect('circulation:loan_detail', loan_id=loan.id)
        except ValueError as e:
            messages.error(request, str(e))
            
    return render(request, 'reservations/fulfill_reservation.html', {'reservation': reservation})
