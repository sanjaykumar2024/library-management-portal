from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_number', 'role', 'membership_status', 'membership_expiry_date', 'phone_number', 'created_at')
    list_filter = ('role', 'membership_status', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'membership_number', 'phone_number')
    ordering = ('-created_at',)
