from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ebooks.open_source import OpenSourceEBookService


class Command(BaseCommand):
    help = 'Imports curated open-source public domain e-books into the LibrarySphere catalog.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of curated classics to import (default: 10)'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(self.style.NOTICE(f"Initiating Open-Source E-Book ingestion (target: {count} books)..."))

        # Find or use an admin/librarian user as uploader
        admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(is_staff=True).first()

        classics = OpenSourceEBookService.get_curated_classics()[:count]
        imported_count = 0
        skipped_count = 0

        for book_data in classics:
            title = book_data.get('title')
            self.stdout.write(f"Processing '{title}'...")
            book, was_created = OpenSourceEBookService.import_book_to_catalog(book_data, uploaded_by=admin_user)

            if was_created:
                imported_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ Successfully imported '{book.title}' into catalog."))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"  - '{book.title}' is already in catalog."))

        self.stdout.write(self.style.SUCCESS(
            f"\nOpen-Source ingestion finished! {imported_count} imported, {skipped_count} already existed."
        ))
