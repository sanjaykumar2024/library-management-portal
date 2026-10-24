from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'user', 'action', 'description', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('description', 'user__username', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action', 'description', 'ip_address')
    date_hierarchy = 'timestamp'
