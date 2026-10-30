import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from catalog.models import Book, EBookMetadata
from ebooks.models import EBookAccessLog, EBookPass, EBookAnnotation


class Command(BaseCommand):
    help = 'Removes e-books with fewer than 25 pages from the digital catalog, ensuring only substantial reading editions remain.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-pages',
            type=int,
            default=25,
            help='Minimum page count threshold (default: 25). Ebooks with fewer pages are removed.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate removal without modifying the database or disk files.'
        )

    def handle(self, *args, **options):
        min_pages = options['min_pages']
        dry_run = options['dry_run']

        protected_root = Path(getattr(settings, 'PROTECTED_EBOOK_ROOT', settings.BASE_DIR / 'protected_ebooks'))

        short_ebooks = EBookMetadata.objects.filter(page_count__lt=min_pages).select_related('book')
        total_count = short_ebooks.count()

        self.stdout.write(self.style.NOTICE(
            f"\n📚 LibrarySphere E-Book Pruning Suite\n"
            f"   Criteria: Page count strictly less than {min_pages}\n"
            f"   Found: {total_count} matching e-book record(s)\n"
            f"   Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE REMOVAL'}\n"
        ))

        if total_count == 0:
            self.stdout.write(self.style.SUCCESS("✅ No e-books found with page count below threshold."))
            return

        removed_count = 0
        files_deleted = 0
        books_converted = 0

        for eb in short_ebooks:
            book = eb.book
            title = book.title
            pages = eb.page_count
            fname = eb.protected_filename

            # Check if file exists on disk
            fpath = protected_root / fname if fname else None

            if dry_run:
                self.stdout.write(f"  [DRY RUN] Would remove: '{title}' (ID: {eb.id}, Pages: {pages}, File: {fname})")
                continue

            # 1. Clean up associated file if not shared
            if fpath and fpath.exists():
                # Check if other records reference this filename
                other_refs = EBookMetadata.objects.filter(protected_filename=fname).exclude(id=eb.id).exists()
                if not other_refs:
                    try:
                        os.remove(fpath)
                        files_deleted += 1
                    except OSError as e:
                        self.stderr.write(f"  Notice: Could not delete file {fpath}: {e}")

            # 2. Delete related access logs, passes, and annotations
            EBookAccessLog.objects.filter(ebook=eb).delete()
            EBookPass.objects.filter(ebook=eb).delete()
            EBookAnnotation.objects.filter(ebook=eb).delete()

            # 3. Update parent Book object
            if book.copies.exists():
                book.book_type = 'PHYSICAL'
                book.save(update_fields=['book_type'])
                books_converted += 1

            # 4. Delete the EBookMetadata record
            eb.delete()
            removed_count += 1
            self.stdout.write(f"  ✓ Removed: '{title}' ({pages} pages) | Book '{book.title}' set to PHYSICAL")

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 E-Book Pruning Completed Successfully!\n"
            f"   E-Book Records Removed: {removed_count}\n"
            f"   Physical Books Retained: {books_converted}\n"
            f"   Files Cleared from Vault: {files_deleted}\n"
            f"   Remaining E-Books in Catalog: {EBookMetadata.objects.count()} (All >= {min_pages} pages)\n"
        ))
