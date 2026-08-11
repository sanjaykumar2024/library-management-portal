from django.contrib import admin
from .models import EBookAccessLog


@admin.register(EBookAccessLog)
class EBookAccessLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ebook', 'action', 'accessed_at', 'ip_address')
    list_filter = ('action',)
    search_fields = ('user__username', 'ebook__book__title', 'ip_address')
    ordering = ('-accessed_at',)
    date_hierarchy = 'accessed_at'
