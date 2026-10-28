from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    @classmethod
    def resolve(cls, value):
        """
        Safely resolve a category from an integer ID, digit string, or name string.
        Returns a Category instance or None.
        """
        if not value:
            return None
        val_str = str(value).strip()
        if not val_str:
            return None
        if val_str.isdigit():
            return cls.objects.filter(id=int(val_str)).first()

        aliases = {
            'sci-fi': 'Science Fiction',
            'scifi': 'Science Fiction',
            'tech': 'Technology',
            'tech & ai': 'Technology',
            'tech and ai': 'Technology',
            'programming': 'Technology',
            'classics': 'Literature',
            'free classics': 'Literature',
        }
        lookup = aliases.get(val_str.lower(), val_str)
        return (
            cls.objects.filter(name__iexact=lookup).first() or
            cls.objects.filter(name__icontains=lookup).first()
        )

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
    isbn = models.CharField(max_length=32, unique=True, verbose_name="ISBN")
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

    @property
    def author(self):
        authors = self.authors.all()
        if authors.exists():
            return ", ".join(a.full_name for a in authors)
        return "Unknown Author"

    @property
    def average_rating(self):
        res = self.reviews.filter(is_approved=True).aggregate(avg=models.Avg('rating'))['avg']
        return round(res, 1) if res else None

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

    @property
    def has_ebook(self):
        return hasattr(self, 'ebook_metadata') and self.ebook_metadata is not None



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

    
    rental_price = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'), help_text="Affordable reading pass fee in INR (₹)")
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


class BookReview(models.Model):
    """Patron rating and review for a library catalog book."""
    RATING_CHOICES = (
        (5, '★★★★★ (5/5) - Excellent'),
        (4, '★★★★☆ (4/5) - Very Good'),
        (3, '★★★☆☆ (3/5) - Good'),
        (2, '★★☆☆☆ (2/5) - Fair'),
        (1, '★☆☆☆☆ (1/5) - Poor'),
    )

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    headline = models.CharField(max_length=150, blank=True)
    review_text = models.TextField()
    is_approved = models.BooleanField(default=True, help_text="Moderation status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('book', 'user')
        verbose_name = 'Book Review'
        verbose_name_plural = 'Book Reviews'

    def __str__(self):
        return f"{self.user.username}'s {self.rating}★ review on '{self.book.title}'"


class UserBookList(models.Model):
    """Personal Bookshelf / Reading Lists for library patrons."""
    SHELF_CHOICES = (
        ('WANT_TO_READ', 'Want to Read'),
        ('CURRENTLY_READING', 'Currently Reading'),
        ('COMPLETED', 'Finished Reading'),
        ('FAVORITES', 'Favorites'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookshelf')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='bookshelf_entries')
    shelf_type = models.CharField(max_length=30, choices=SHELF_CHOICES, default='WANT_TO_READ')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']
        unique_together = ('user', 'book', 'shelf_type')
        verbose_name = 'Bookshelf Entry'
        verbose_name_plural = 'Bookshelf Entries'

    def __str__(self):
        return f"{self.user.username} - {self.get_shelf_type_display()}: {self.book.title}"


# ── Pillar 5: Gamification, Reading Challenges & Badges ────────────────────────

class ReadingChallenge(models.Model):
    """Annual reading goal set by a patron (e.g., 15 books in 2026)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_challenges')
    year = models.IntegerField(default=2026)
    target_books = models.PositiveIntegerField(default=12)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'year')
        verbose_name = 'Reading Challenge'
        verbose_name_plural = 'Reading Challenges'

    @property
    def completed_count(self):
        return UserBookList.objects.filter(
            user=self.user, shelf_type='COMPLETED', added_at__year=self.year
        ).values('book').distinct().count()

    @property
    def progress_pct(self):
        if self.target_books == 0:
            return 100
        return min(100, round((self.completed_count / self.target_books) * 100))

    def __str__(self):
        return f"{self.user.username}'s {self.year} Goal: {self.completed_count}/{self.target_books} Books"


class PatronBadge(models.Model):
    """Gamification achievement badges earned by library patrons."""
    BADGE_INFO = {
        'FIRST_BORROW': ('First Checkout', 'Checked out your first library book', 'bi-book-half', '#6366F1'),
        'BOOKWORM': ('Avid Bookworm', 'Completed 5 books in your reading shelf', 'bi-trophy-fill', '#F59E0B'),
        'CLASSIC_EXPLORER': ('Classic Explorer', 'Read an open access world classic', 'bi-compass-fill', '#10B981'),
        'COMMUNITY_VOICE': ('Community Voice', 'Contributed a thoughtful star review', 'bi-chat-heart-fill', '#EC4899'),
        'NIGHT_OWL': ('Night Owl Scholar', 'Engaged with library portal in evening hours', 'bi-moon-stars-fill', '#8B5CF6'),
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge_type = models.CharField(max_length=30, choices=[(k, v[0]) for k, v in BADGE_INFO.items()])
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge_type')
        ordering = ['-awarded_at']
        verbose_name = 'Patron Badge'
        verbose_name_plural = 'Patron Badges'

    @property
    def title(self):
        return self.BADGE_INFO.get(self.badge_type, (self.badge_type, ''))[0]

    @property
    def description(self):
        return self.BADGE_INFO.get(self.badge_type, ('', 'Achievement unlocked'))[1]

    @property
    def icon(self):
        return self.BADGE_INFO.get(self.badge_type, ('', '', 'bi-award'))[2]

    @property
    def color(self):
        return self.BADGE_INFO.get(self.badge_type, ('', '', '', '#6366F1'))[3]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


def award_badge(user, badge_type):
    """Helper to safely award an achievement badge with notification and audit logging."""
    badge, created = PatronBadge.objects.get_or_create(user=user, badge_type=badge_type)
    if created:
        try:
            from notifications.services import create_notification
            create_notification(
                user=user,
                title="🏆 Achievement Badge Unlocked!",
                message=f"Congratulations! You've unlocked the '{badge.title}' badge: {badge.description}.",
                type='SUCCESS',
                link='/accounts/profile/'
            )
        except Exception:
            pass
        try:
            from core.models import log_activity
            log_activity('BADGE_UNLOCKED', f"Unlocked badge '{badge.title}' for {user.username}", user=user)
        except Exception:
            pass
    return badge, created


