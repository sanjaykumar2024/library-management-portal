from django.contrib import admin
from .models import Category, Author, Book, BookCopy, EBookMetadata

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    search_fields = ('full_name',)

class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 1

class EBookMetadataInline(admin.StackedInline):
    model = EBookMetadata
    can_delete = False

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'category', 'book_type', 'is_active')
    list_filter = ('book_type', 'is_active', 'category')
    search_fields = ('title', 'isbn', 'authors__full_name')
    filter_horizontal = ('authors',)
    inlines = [BookCopyInline, EBookMetadataInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'authors', 'category', 'isbn', 'description')
        }),
        ('Publication Details', {
            'fields': ('publisher', 'publication_year', 'language')
        }),
        ('Media & Status', {
            'fields': ('book_type', 'cover_image', 'is_active')
        }),
    )

@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('accession_number', 'book', 'status', 'shelf_location')
    list_filter = ('status',)
    search_fields = ('accession_number', 'book__title')

@admin.register(EBookMetadata)
class EBookMetadataAdmin(admin.ModelAdmin):
    list_display = ('book', 'access_level', 'format', 'access_mode', 'rights_status', 'is_active', 'page_count')
    list_filter = ('access_level', 'access_mode', 'rights_status', 'is_active')
    search_fields = ('book__title', 'original_file_name')
    actions = ['mark_as_free', 'mark_as_members_only', 'mark_as_staff_only']

    @admin.action(description="Set Access Level to FREE (Available to Everyone)")
    def mark_as_free(self, request, queryset):
        updated = queryset.update(access_level='FREE')
        self.message_user(request, f"Successfully classified {updated} e-book(s) as FREE.")

    @admin.action(description="Set Access Level to MEMBERS ONLY (Active Membership Required)")
    def mark_as_members_only(self, request, queryset):
        updated = queryset.update(access_level='MEMBERS_ONLY')
        self.message_user(request, f"Successfully classified {updated} e-book(s) as MEMBERS ONLY.")

    @admin.action(description="Set Access Level to STAFF ONLY (Internal Staff / Librarians)")
    def mark_as_staff_only(self, request, queryset):
        updated = queryset.update(access_level='STAFF_ONLY')
        self.message_user(request, f"Successfully classified {updated} e-book(s) as STAFF ONLY.")

