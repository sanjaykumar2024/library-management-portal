from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Author(models.Model):
    full_name = models.CharField(max_length=200)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name

class Book(models.Model):
    BOOK_TYPE_CHOICES = (
        ('PHYSICAL', 'Physical Only'),
        ('EBOOK', 'E-Book Only'),
        ('BOTH', 'Both Physical and E-Book'),
    )

    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    authors = models.ManyToManyField(Author, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    publisher = models.CharField(max_length=200, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, default='English')
    description = models.TextField()
    book_type = models.CharField(max_length=20, choices=BOOK_TYPE_CHOICES, default='PHYSICAL')
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class BookCopy(models.Model):
    STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('ISSUED', 'Issued'),
        ('RESERVED', 'Reserved'),
        ('LOST', 'Lost'),
        ('DAMAGED', 'Damaged'),
        ('MAINTENANCE', 'Maintenance'),
    )

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    accession_number = models.CharField(max_length=50, unique=True)
    shelf_location = models.CharField(max_length=100)
    condition = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')

    class Meta:
        verbose_name_plural = 'book copies'

    def __str__(self):
        return f"{self.book.title} - {self.accession_number} ({self.get_status_display()})"

from django.utils import timezone

class EBookMetadata(models.Model):
    ACCESS_MODE_CHOICES = (
        ('READ_ONLY', 'Read Only'),
        ('READ_AND_DOWNLOAD', 'Read and Download'),
    )

    RIGHTS_STATUS_CHOICES = (
        ('PUBLIC_DOMAIN', 'Public Domain'),
        ('OPEN_LICENSE', 'Open License'),
        ('LIBRARY_LICENSED', 'Library Licensed'),
        ('DEMO_ONLY', 'Demo Only'),
    )

    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='ebook_metadata')
    protected_filename = models.CharField(max_length=255, blank=True, null=True, help_text="Randomized filename in protected storage")
    original_file_name = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_ebooks')
    file_size = models.BigIntegerField(blank=True, null=True, help_text="File size in bytes")
    page_count = models.IntegerField(blank=True, null=True)
    format = models.CharField(max_length=10, default='PDF')

    
    access_mode = models.CharField(max_length=20, choices=ACCESS_MODE_CHOICES, default='READ_ONLY')
    rights_status = models.CharField(max_length=30, choices=RIGHTS_STATUS_CHOICES, default='DEMO_ONLY')
    rights_text = models.TextField(blank=True, null=True, help_text="Rights, source, or attribution text")
    max_concurrent_readers = models.IntegerField(default=5, help_text="Maximum simultaneous active readers allowed (0 for unlimited)")
    is_active = models.BooleanField(default=True)
    access_note = models.TextField(blank=True, null=True, help_text="Optional notice/note for members")

    class Meta:
        verbose_name = 'E-Book Metadata'
        verbose_name_plural = 'E-Book Metadata'

    @property
    def is_download_allowed(self):
        return self.access_mode == 'READ_AND_DOWNLOAD'

    def __str__(self):
        return f"E-Book: {self.book.title} ({self.format})"

