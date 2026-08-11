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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    
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

    def is_admin(self):
        return self.role == 'ADMIN' or self.user.is_superuser

    def is_librarian(self):
        return self.role == 'LIBRARIAN' or self.is_admin()

    def is_member(self):
        return self.role == 'MEMBER'


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
