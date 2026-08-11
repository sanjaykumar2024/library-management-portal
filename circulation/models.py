from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from accounts.models import UserProfile
from catalog.models import BookCopy
from django.utils import timezone

class Loan(models.Model):
    STATUS_CHOICES = (
        ('ISSUED', 'Issued'),
        ('RETURNED', 'Returned'),
    )

    member = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='loans')
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='loans')
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_loans')
    returned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_loans')
    
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ISSUED')
    renewal_count = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.due_date and self.issue_date and self.due_date < self.issue_date:
            raise ValidationError({'due_date': 'Due date cannot be before the issue date.'})
        if self.return_date and self.issue_date and self.return_date < self.issue_date:
            raise ValidationError({'return_date': 'Return date cannot be before the issue date.'})

    def __str__(self):
        return f"Loan: {self.book_copy.book.title} to {self.member.user.username}"


class Fine(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('WAIVED', 'Waived'),
    )

    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name='fine')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    overdue_days = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({'amount': 'Fine amount must be greater than zero.'})
        if self.overdue_days is not None and self.overdue_days <= 0:
            raise ValidationError({'overdue_days': 'Overdue days must be greater than zero.'})

    def __str__(self):
        return f"Fine: ${self.amount} for {self.loan.member.user.username}"
