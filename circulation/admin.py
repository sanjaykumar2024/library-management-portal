from django.contrib import admin
from .models import Loan, Fine


@admin.action(description='Mark selected loans as returned')
def mark_as_returned(modeladmin, request, queryset):
    from django.utils import timezone
    updated = queryset.filter(status='ACTIVE').update(status='RETURNED', return_date=timezone.now().date())
    modeladmin.message_user(request, f'{updated} loan(s) marked as returned.')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'book_copy', 'issue_date', 'due_date', 'return_date', 'status')
    list_filter = ('status', 'issue_date')
    search_fields = ('member__membership_number', 'member__user__username', 'book_copy__accession_number', 'book_copy__book__title')
    ordering = ('-issue_date',)
    date_hierarchy = 'issue_date'
    raw_id_fields = ('member', 'book_copy')
    actions = [mark_as_returned]


@admin.action(description='Mark selected fines as paid')
def mark_fines_as_paid(modeladmin, request, queryset):
    updated = queryset.filter(status='PENDING').update(status='PAID')
    modeladmin.message_user(request, f'{updated} fine(s) marked as paid.')

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_member_name', 'get_book_title', 'amount', 'status', 'overdue_days')
    list_filter = ('status',)
    search_fields = ('loan__member__membership_number', 'loan__member__user__username', 'loan__book_copy__book__title')
    ordering = ('-created_at',)
    actions = [mark_fines_as_paid]

    @admin.display(description='Member')
    def get_member_name(self, obj):
        return obj.loan.member.user.get_full_name() or obj.loan.member.user.username

    @admin.display(description='Book Title')
    def get_book_title(self, obj):
        return obj.loan.book_copy.book.title if obj.loan else 'N/A'
