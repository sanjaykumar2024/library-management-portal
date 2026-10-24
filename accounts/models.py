from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import datetime
import random
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('LIBRARIAN', 'Librarian'),
        ('MEMBER', 'Member'),
    )

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('SUSPENDED', 'Suspended'),
    )

    TIER_CHOICES = (
        ('STUDENT', 'Student Scholar (Max 3 Books)'),
        ('STANDARD', 'Standard Patron (Max 5 Books)'),
        ('PREMIUM_SCHOLAR', 'Premium Scholar (Max 10 Books & Unlimited Holds)'),
    )

    THEME_CHOICES = (
        ('light', 'Normal Mode (Light)'),
        ('dark', 'Dark Mode'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='STUDENT')
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')

    
    # Contact Info
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Membership Info
    membership_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    membership_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    joining_date = models.DateField(default=timezone.now)
    membership_expiry_date = models.DateField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True, help_text="Internal notes by librarian/admin")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def max_books_allowed(self):
        if self.tier == 'STUDENT':
            return 3
        elif self.tier == 'PREMIUM_SCHOLAR':
            return 10
        return 5

    def is_admin(self):
        return self.role == 'ADMIN' or self.user.is_superuser

    def is_librarian(self):
        return self.role == 'LIBRARIAN' or self.is_admin()

    def is_member(self):
        return self.role == 'MEMBER'


class MembershipRequest(models.Model):
    """Patron self-service request for membership renewal or tier upgrade."""
    REQUEST_TYPE_CHOICES = (
        ('RENEWAL', 'Membership Renewal (1-Year Extension)'),
        ('UPGRADE_TIER', 'Membership Tier Upgrade'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default='RENEWAL')
    requested_tier = models.CharField(max_length=20, choices=UserProfile.TIER_CHOICES, blank=True, null=True)
    reason = models.TextField(blank=True, help_text="Note from patron (student ID, justification, etc.)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_membership_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Membership Request'
        verbose_name_plural = 'Membership Requests'

    def __str__(self):
        return f"{self.get_request_type_display()} from {self.user.username} ({self.get_status_display()})"



def generate_membership_number():
    year = timezone.now().year
    while True:
        # Generate something like LIB-2026-83492
        number = f"LIB-{year}-{random.randint(10000, 99999)}"
        if not UserProfile.objects.filter(membership_number=number).exists():
            return number

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'ADMIN' if instance.is_superuser else 'MEMBER'
        mem_num = generate_membership_number()
        expiry = timezone.now().date() + datetime.timedelta(days=365)
        UserProfile.objects.create(
            user=instance, 
            role=role, 
            membership_number=mem_num,
            membership_expiry_date=expiry
        )
    else:
        if hasattr(instance, 'profile'):
            if instance.is_superuser and instance.profile.role != 'ADMIN':
                instance.profile.role = 'ADMIN'
            
            # Ensure existing users get membership numbers
            if not instance.profile.membership_number:
                instance.profile.membership_number = generate_membership_number()
            if not instance.profile.membership_expiry_date:
                instance.profile.membership_expiry_date = timezone.now().date() + datetime.timedelta(days=365)
                
            instance.profile.save()
        else:
            role = 'ADMIN' if instance.is_superuser else 'MEMBER'
            mem_num = generate_membership_number()
            expiry = timezone.now().date() + datetime.timedelta(days=365)
            UserProfile.objects.create(
                user=instance, 
                role=role,
                membership_number=mem_num,
                membership_expiry_date=expiry
            )
