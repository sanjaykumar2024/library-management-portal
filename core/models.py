from django.db import models
from django.contrib.auth.models import User


class ActivityLog(models.Model):
    """
    Centralized event audit trail recording key lifecycle actions
    across circulation, catalog, e-books, and membership.
    """
    ACTION_CHOICES = [
        ('LOAN_ISSUED', 'Loan Issued'),
        ('LOAN_RETURNED', 'Loan Returned'),
        ('LOAN_RENEWED', 'Loan Renewed'),
        ('FINE_PAID', 'Fine Paid'),
        ('RESERVATION_PLACED', 'Reservation Placed'),
        ('RESERVATION_ALLOCATED', 'Reservation Allocated'),
        ('EBOOK_READ', 'E-Book Read'),
        ('EBOOK_IMPORTED', 'E-Book Imported'),
        ('MEMBER_REGISTERED', 'Member Registered'),
        ('REVIEW_POSTED', 'Review Posted'),
        ('MEMBERSHIP_UPGRADED', 'Membership Upgraded'),
        ('OAUTH_LOGIN', 'OAuth Google Sign-In'),
        ('USER_ROLE_CHANGED', 'User Role Changed'),
        ('PERMISSION_CHANGED', 'Permission Changed'),
        ('ACCOUNT_STATUS_CHANGED', 'Account Status Changed'),
        ('SESSION_REVOKED', 'User Session Revoked'),
        ('MEMBERSHIP_APPROVED', 'Membership Approved'),
        ('MEMBERSHIP_DENIED', 'Membership Denied'),
        ('OTHER', 'Other Activity'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    description = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {user_str} - {self.get_action_display()}: {self.description}"


def log_activity(action, description, user=None, request=None):
    """
    Convenience helper to record a platform activity event.
    Extracts IP address from request if supplied.
    """
    ip = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        if not user and request.user.is_authenticated:
            user = request.user

    return ActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip
    )
