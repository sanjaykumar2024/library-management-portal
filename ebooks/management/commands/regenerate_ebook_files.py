import os
import re
import uuid
from pathlib import Path
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from catalog.models import EBookMetadata
from ebooks.kaggle_service import KaggleEBookService


CLASSIC_PAGES_MAP = {
    'pride and prejudice': 480,
    'frankenstein': 280,
    'the adventures of sherlock holmes': 320,
    'dracula': 448,
    'alice': 200,
    'the great gatsby': 180,
    'the time machine': 128,
    'the metamorphosis': 104,
    'a tale of two cities': 448,
    'moby-dick': 624,
    'the quantum horizon': 360,
    'algorithms of tomorrow': 420,
}


class Command(BaseCommand):
    help = 'Ensures all catalog e-books have valid protected HTML reader documents on disk.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of all e-book files, overwriting existing ones.'
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        protected_root = Path(getattr(settings, 'PROTECTED_EBOOK_ROOT', settings.BASE_DIR / 'protected_ebooks'))
        os.makedirs(protected_root, exist_ok=True)

        ebooks = EBookMetadata.objects.all().select_related('book', 'book__category').prefetch_related('book__authors')
        total = ebooks.count()
        self.stdout.write(self.style.NOTICE(f"\n📖 Initiating E-Book Reader Document Sync (Total: {total} e-books)...\n"))

        generated_count = 0
        skipped_count = 0

        for ebook in ebooks:
            book = ebook.book
            title_lower = book.title.lower()
            target_pages = ebook.page_count or 350
            if target_pages < 100:
                for k, p in CLASSIC_PAGES_MAP.items():
                    if k in title_lower:
                        target_pages = p
                        break
                if target_pages < 100:
                    target_pages = 350

            if not ebook.protected_filename or not ebook.protected_filename.endswith('.html'):
                ebook.protected_filename = f"{uuid.uuid4().hex}.html"
                ebook.format = 'HTML'
                ebook.save(update_fields=['protected_filename', 'format'])

            file_path = protected_root / ebook.protected_filename

            if file_path.exists() and not force and ebook.page_count and ebook.page_count >= 100:
                skipped_count += 1
                continue

            first_author = book.authors.first() if hasattr(book, 'authors') else None
            first_author_name = first_author.full_name if first_author else 'Unknown Author'
            category_name = book.category.name if book.category else 'General'

            book_info = {
                'title': book.title,
                'subtitle': getattr(book, 'subtitle', '') or '',
                'author': first_author_name,
                'category': category_name,
                'publisher': book.publisher or 'Public Library Digital Collection',
                'publication_year': book.publication_year or 2024,
                'description': book.description or f"Complete digital edition of {book.title}.",
                'isbn': book.isbn or '',
                'pages': target_pages,
                'average_rating': 4.5,
            }

            try:
                doc_html = KaggleEBookService._generate_reader_document(book_info)
                encoded = doc_html.encode('utf-8')
                with open(file_path, 'wb') as f:
                    f.write(encoded)
                ebook.file_size = len(encoded)
                ebook.format = 'HTML'
                ebook.page_count = target_pages
                ebook.save(update_fields=['file_size', 'format', 'page_count'])
                generated_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ [{ebook.id}] Synced {target_pages}-page edition for '{book.title}'"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ [{ebook.id}] Failed for '{book.title}': {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Finished E-Book Document Sync!\n"
            f"   Total Generated/Synced: {generated_count}\n"
            f"   Total Already Present:  {skipped_count}\n"
        ))
