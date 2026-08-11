from django.core.exceptions import ValidationError
from django.db import models
from accounts.models import UserProfile
from catalog.models import Book, BookCopy

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),        # Waiting for a copy to become available
        ('ALLOCATED', 'Allocated'),    # Copy is available and held for the member
        ('FULFILLED', 'Fulfilled'),    # Member picked up the book
        ('CANCELLED', 'Cancelled'),    # Member cancelled the reservation
        ('EXPIRED', 'Expired'),        # Member didn't pick up the book in time
    )

    member = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    allocated_copy = models.ForeignKey(BookCopy, on_delete=models.SET_NULL, null=True, blank=True, related_name='allocations')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)

    def clean(self):
        super().clean()
        if self.status == 'PENDING' and self.pk is None:
            existing = Reservation.objects.filter(
                member=self.member, book=self.book, status='PENDING'
            ).exists()
            if existing:
                raise ValidationError('You already have a pending reservation for this book.')

    class Meta:
        ordering = ['reservation_date']

    def __str__(self):
        return f"Reservation: {self.book.title} for {self.member.user.username}"
