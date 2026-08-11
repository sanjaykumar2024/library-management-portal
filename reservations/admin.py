from django.contrib import admin
from .models import Reservation


@admin.action(description='Expire selected reservations')
def expire_reservations(modeladmin, request, queryset):
    updated = queryset.filter(status='PENDING').update(status='EXPIRED')
    modeladmin.message_user(request, f'{updated} reservation(s) marked as expired.')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'book', 'status', 'reservation_date')
    list_filter = ('status',)
    search_fields = ('member__membership_number', 'member__user__username', 'book__title', 'allocated_copy__accession_number')
    ordering = ('-reservation_date',)
    date_hierarchy = 'reservation_date'
    actions = [expire_reservations]
