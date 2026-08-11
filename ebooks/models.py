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
