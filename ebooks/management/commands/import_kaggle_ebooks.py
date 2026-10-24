import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from ebooks.kaggle_service import KaggleEBookService


class Command(BaseCommand):
    help = 'Imports curated or user-provided Kaggle book datasets into the LibrarySphere catalog.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='',
            help='Path to Kaggle CSV file (defaults to data/kaggle_books.csv)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Maximum number of books to import (0 for all, default: 0)'
        )
        parser.add_argument(
            '--mode',
            type=str,
            default='READ_AND_DOWNLOAD',
            choices=['READ_ONLY', 'READ_AND_DOWNLOAD'],
            help='Digital access mode (default: READ_AND_DOWNLOAD)'
        )
        parser.add_argument(
            '--rights',
            type=str,
            default='LIBRARY_LICENSED',
            choices=['PUBLIC_DOMAIN', 'OPEN_LICENSE', 'LIBRARY_LICENSED', 'DEMO_ONLY'],
            help='Rights status classification (default: LIBRARY_LICENSED)'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing book records if matching ISBN exists'
        )

    def handle(self, *args, **options):
        csv_file_path = options['file']
        if not csv_file_path:
            default_csv = Path(settings.BASE_DIR) / 'data' / 'kaggle_books.csv'
            if not default_csv.exists():
                raise CommandError(f"Default Kaggle dataset not found at {default_csv}. Specify a path via --file.")
            csv_file_path = str(default_csv)
        else:
            if not os.path.exists(csv_file_path):
                raise CommandError(f"Specified CSV file not found: {csv_file_path}")

        limit = options['limit'] or None
        mode = options['mode']
        rights = options['rights']
        overwrite = options['overwrite']

        self.stdout.write(self.style.NOTICE(
            f"\n🚀 Initiating Kaggle E-Book Ingestion\n"
            f"   Source File: {csv_file_path}\n"
            f"   Limit:       {limit or 'All rows'}\n"
            f"   Access Mode: {mode}\n"
            f"   Rights:      {rights}\n"
            f"   Overwrite:   {overwrite}\n"
        ))

        admin_user = (
            User.objects.filter(is_superuser=True).first()
            or User.objects.filter(is_staff=True).first()
            or User.objects.first()
        )

        stats = KaggleEBookService.import_from_csv(
            file_or_path=csv_file_path,
            limit=limit,
            access_mode=mode,
            rights_status=rights,
            uploaded_by=admin_user,
            overwrite=overwrite
        )

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Kaggle E-Book Ingestion Completed Successfully!\n"
            f"   -----------------------------------------\n"
            f"   Total Rows Processed:  {stats['total_rows']}\n"
            f"   Successfully Imported: {stats['imported']}\n"
            f"   Skipped / Unchanged:   {stats['skipped']}\n"
            f"   Errors:                {stats['errors']}\n"
        ))

        if stats['books']:
            self.stdout.write(self.style.MIGRATE_HEADING("Sample Imported Books:"))
            for book in stats['books'][:10]:
                authors = ", ".join(a.full_name for a in book.authors.all())
                self.stdout.write(f"  • {book.title} (ISBN: {book.isbn}) by {authors} [{book.category.name if book.category else 'N/A'}]")
            if len(stats['books']) > 10:
                self.stdout.write(f"  ... and {len(stats['books']) - 10} more books!")
