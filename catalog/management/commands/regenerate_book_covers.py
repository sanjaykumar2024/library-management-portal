import os
from django.core.management.base import BaseCommand
from catalog.models import Book
from catalog.cover_generator import BookCoverGenerator


class Command(BaseCommand):
    help = 'Regenerates high-resolution, publisher-grade simulated hardcover book covers for all catalog books.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of covers for all books, overwriting existing ones.'
        )
        parser.add_argument(
            '--missing-only',
            action='store_true',
            help='Only generate covers for books that have no cover_image.'
        )

    def handle(self, *args, **options):
        force = options['force']
        missing_only = options['missing_only']

        books = Book.objects.all().select_related('category').prefetch_related('authors')
        total = books.count()
        self.stdout.write(self.style.NOTICE(f"\n🎨 Initiating Book Cover Art Regeneration (Total: {total} books)...\n"))

        updated_count = 0
        skipped_count = 0

        for book in books:
            has_cover = bool(book.cover_image and hasattr(book.cover_image, 'name') and book.cover_image.name)

            if missing_only and has_cover:
                skipped_count += 1
                continue

            authors = ", ".join(a.full_name for a in book.authors.all())
            category_name = book.category.name if book.category else "General"

            try:
                cover_file = BookCoverGenerator.generate_cover(
                    title=book.title,
                    author=authors,
                    category=category_name,
                    isbn=book.isbn
                )
                # Save the new cover file
                book.cover_image.save(cover_file.name, cover_file, save=True)
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ [{book.id}] Generated cover for '{book.title}' ({category_name})"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ [{book.id}] Failed for '{book.title}': {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Finished Cover Regeneration!\n"
            f"   Total Updated: {updated_count}\n"
            f"   Total Skipped: {skipped_count}\n"
        ))
