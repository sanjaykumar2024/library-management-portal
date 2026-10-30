import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from catalog.models import EBookMetadata


class Command(BaseCommand):
    help = 'Classifies e-book access levels (FREE vs MEMBERS_ONLY vs STAFF_ONLY) and generates an administrative audit report.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-evaluate and overwrite existing access levels for all e-books.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate classification without committing changes to database.'
        )

    def handle(self, *args, **options):
        force = options['force']
        dry_run = options['dry_run']

        ebooks_qs = EBookMetadata.objects.select_related('book', 'book__category').all()
        total = ebooks_qs.count()

        self.stdout.write(self.style.NOTICE(
            f"\n🛡️  LibrarySphere E-Book Access Classification Suite\n"
            f"   Total Digital E-Books in Catalog: {total}\n"
            f"   Mode: {'DRY RUN' if dry_run else 'LIVE CLASSIFICATION'}\n"
        ))

        classified_free = 0
        classified_members = 0
        classified_staff = 0
        unclassified_count = 0
        records = []

        for eb in ebooks_qs:
            prev_level = eb.access_level
            target_level = None

            # 1. Free Classics & Public Domain -> FREE (Accessible to Guests & Members)
            if eb.rights_status in ['PUBLIC_DOMAIN', 'OPEN_LICENSE']:
                target_level = 'FREE'
            # 2. Modern Library-Licensed Titles -> MEMBERS_ONLY (Active Membership Required)
            elif eb.rights_status == 'LIBRARY_LICENSED':
                target_level = 'MEMBERS_ONLY'
            # 3. Staff internal / demo -> STAFF_ONLY
            elif eb.rights_status == 'DEMO_ONLY':
                target_level = 'STAFF_ONLY'
            else:
                # Safe default per master prompt: MEMBERS_ONLY
                target_level = 'MEMBERS_ONLY'
                unclassified_count += 1

            needs_update = force or (prev_level != target_level)

            if needs_update and not dry_run:
                eb.access_level = target_level
                eb.save(update_fields=['access_level'])

            if target_level == 'FREE':
                classified_free += 1
            elif target_level == 'MEMBERS_ONLY':
                classified_members += 1
            elif target_level == 'STAFF_ONLY':
                classified_staff += 1

            records.append({
                'id': eb.id,
                'title': eb.book.title,
                'category': eb.book.category.name if eb.book.category else 'General',
                'rights_status': eb.rights_status,
                'access_level': target_level,
                'pages': eb.page_count,
            })

        # Save administrative audit report
        report_path = Path(settings.BASE_DIR) / 'data' / 'ebook_access_classification_report.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_data = {
            'timestamp': timezone.now().isoformat(),
            'total_ebooks': total,
            'free_access_count': classified_free,
            'members_only_count': classified_members,
            'staff_only_count': classified_staff,
            'ambiguous_defaulted_count': unclassified_count,
            'books': records,
        }
        report_path.write_text(json.dumps(report_data, indent=2), encoding='utf-8')

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 E-Book Access Classification Complete!\n"
            f"   Total E-Books Evaluated: {total}\n"
            f"   ✓ FREE Access (Guests + Members): {classified_free}\n"
            f"   🔒 MEMBERS ONLY (Active Patrons): {classified_members}\n"
            f"   🛡️  STAFF ONLY (Admins/Librarians): {classified_staff}\n"
            f"   Audit Report Saved To: {report_path}\n"
        ))
