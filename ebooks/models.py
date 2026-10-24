from django.db import models
from django.contrib.auth.models import User
from catalog.models import EBookMetadata

class EBookAccessLog(models.Model):
    ACTION_CHOICES = (
        ('READ', 'Read Online'),
        ('DOWNLOAD', 'Download'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ebook_access_logs')
    ebook = models.ForeignKey(EBookMetadata, on_delete=models.CASCADE, related_name='access_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-accessed_at']
        verbose_name = 'E-Book Access Log'
        verbose_name_plural = 'E-Book Access Logs'

    def __str__(self):
        return f"{self.user.username} {self.get_action_display()} '{self.ebook.book.title}' on {self.accessed_at.strftime('%Y-%m-%d %H:%M')}"


class EBookPass(models.Model):
    """
    Model representing an unlocked, affordable digital reading pass paid by a member.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ebook_passes')
    ebook = models.ForeignKey(EBookMetadata, on_delete=models.CASCADE, related_name='unlocked_passes')
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2, default=5.00)
    payment_method = models.CharField(max_length=50, default='UPI / Wallet Pass')
    transaction_id = models.CharField(max_length=100, unique=True)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-unlocked_at']
        verbose_name = 'E-Book Digital Pass'
        verbose_name_plural = 'E-Book Digital Passes'

    def __str__(self):
        return f"Pass #{self.transaction_id[:8]} for {self.user.username} on '{self.ebook.book.title}' (₹{self.amount_paid})"


class EBookAnnotation(models.Model):
    """
    Patron highlight and marginalia note inside an e-book.
    """
    COLOR_CHOICES = (
        ('yellow', 'Amber Gold'),
        ('green', 'Emerald Green'),
        ('pink', 'Rose Pink'),
        ('blue', 'Cyan Blue'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ebook_annotations')
    ebook = models.ForeignKey(EBookMetadata, on_delete=models.CASCADE, related_name='annotations')
    selected_text = models.TextField(help_text="Highlighted passage text")
    note = models.TextField(blank=True, help_text="Patron note or reflection")
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='yellow')
    chapter_title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'E-Book Annotation'
        verbose_name_plural = 'E-Book Annotations'

    def __str__(self):
        snippet = self.selected_text[:40] + "..." if len(self.selected_text) > 40 else self.selected_text
        return f"{self.user.username} - '{snippet}' on {self.ebook.book.title}"

