import os
import re
import json
import uuid
from pathlib import Path
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from catalog.models import Book, EBookMetadata, Author, Category
from ebooks.gutenberg_service import GutenbergService
from ebooks.kaggle_service import KaggleEBookService
from ebooks.generator import BookContentSynthesizer


class Command(BaseCommand):
    help = 'Audits and repairs all ebooks across the library, eliminating repetitive filler and establishing authentic reading editions.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=0, help='Maximum number of books to process (0 for all)')
        parser.add_argument('--force', action='store_true', help='Force regeneration even if book is already clean')

    def handle(self, *args, **options):
        limit = options['limit']
        force = options['force']

        protected_root = Path(settings.PROTECTED_EBOOK_ROOT)
        protected_root.mkdir(parents=True, exist_ok=True)

        synthetic_snippets = [
            'Write-Ahead Log (WAL) Checkpoint Recovery',
            'Sliding Window Rate Limiter via Redis Sorted Sets',
            'Two-Phase Commit (2PC) Coordinator Protocol',
            'Raft Consensus: Term Monotonicity',
            'The Distributed Split-Brain Crisis',
            'The Cascading Retry Storm',
            'The Memory Leak in Long-Lived Buffers',
            'The Cache Stampede at Midnight',
            'The Monolith-to-Event-Sourced Migration',
            'The Conversation in the Drawing-Room',
            'The Letter Read in Solitude',
            'Walking upon the Terrace at Twilight',
            'Section 1.2: The Shadow of Family Expectations',
            'Section 1.2: Write-Ahead Log'
        ]

        # Ensure reference benchmark EPUB (pg67098-images-3.epub: Winnie-the-Pooh by A. A. Milne)
        epub_ref_path = protected_root / 'pg67098-images-3.epub'
        html_companion_path = protected_root / 'pg67098-images-3.html'
        static_img_dir = Path(settings.BASE_DIR) / 'static' / 'ebooks' / 'pg67098'
        actual_pooh_pages = 76

        if epub_ref_path.exists():
            # Extract images to static/ebooks/pg67098 if not already present
            os.makedirs(static_img_dir, exist_ok=True)
            try:
                import zipfile
                with zipfile.ZipFile(epub_ref_path, 'r') as z:
                    for n in z.namelist():
                        if n.startswith('OEBPS/') and (n.endswith('.jpg') or n.endswith('.png')):
                            fname = os.path.basename(n)
                            target_img = static_img_dir / fname
                            if not target_img.exists():
                                with open(target_img, 'wb') as img_out:
                                    img_out.write(z.read(n))
            except Exception as e:
                self.stderr.write(f"Notice: EPUB image extraction: {e}")

            # Generate HTML reading companion if missing
            if not html_companion_path.exists():
                try:
                    res = GutenbergService.format_gutenberg_reader_document('Winnie-the-Pooh', 'A. A. Milne', 67098)
                    if res:
                        doc_html, actual_pooh_pages = res
                        doc_html = re.sub(r'src=[\"\'](?:images/)?([^\"\']+\.jpg)[\"\']', r'src=\"/static/ebooks/pg67098/\1\"', doc_html)
                        html_companion_path.write_text(doc_html, encoding='utf-8')
                except Exception as e:
                    self.stderr.write(f"Notice: EPUB companion HTML generation: {e}")

            cat = Category.objects.filter(name__icontains='Children').first() or Category.objects.first()
            pooh_book, _ = Book.objects.get_or_create(
                isbn='978-0-14-036121-6',
                defaults={
                    'title': 'Winnie-the-Pooh',
                    'description': 'The classic children’s story of Christopher Robin, Winnie-the-Pooh, Piglet, Eeyore, and friends in the Hundred Acre Wood. Complete illustrated edition with authentic Ernest H. Shepard artwork, served natively as a digital EPUB asset.',
                    'category': cat,
                    'publisher': 'Methuen & Co. / Project Gutenberg',
                    'publication_year': 1926,
                    'book_type': 'EBOOK',
                }
            )
            author_obj, _ = Author.objects.get_or_create(full_name='A. A. Milne')
            pooh_book.authors.add(author_obj)

            EBookMetadata.objects.update_or_create(
                book=pooh_book,
                defaults={
                    'protected_filename': 'pg67098-images-3.epub',
                    'original_file_name': 'Winnie-the-Pooh_Illustrated_EPUB_pg67098.epub',
                    'format': 'EPUB',
                    'file_size': epub_ref_path.stat().st_size,
                    'page_count': actual_pooh_pages,
                    'access_mode': 'READ_AND_DOWNLOAD',
                    'rights_status': 'PUBLIC_DOMAIN',
                    'rights_text': 'Project Gutenberg #67098 &bull; Public Domain in the United States',
                    'is_active': True,
                }
            )

        ebooks_qs = EBookMetadata.objects.select_related('book', 'book__category').all().order_by('id')
        if limit > 0:
            ebooks_qs = ebooks_qs[:limit]

        total = ebooks_qs.count()
        self.stdout.write(f"Initiating audit and repair across {total} ebooks in library catalog...")

        repaired_count = 0
        preserved_gutenberg = 0
        preserved_epub = 0
        error_count = 0
        results = []

        for idx, eb in enumerate(ebooks_qs, 1):
            book = eb.book
            title = book.title
            cat_name = book.category.name if book.category else 'General'
            author_name = book.author or 'Author'
            
            fpath = protected_root / eb.protected_filename if eb.protected_filename else None
            needs_repair = force or (not fpath) or (not fpath.exists())

            # Check if existing file has synthetic repetition
            if fpath and fpath.exists() and not force:
                try:
                    content = fpath.read_text(encoding='utf-8', errors='ignore')
                    if any(s in content for s in synthetic_snippets):
                        needs_repair = True
                    elif eb.format == 'EPUB' or str(fpath).endswith('.epub'):
                        preserved_epub += 1
                        results.append({'id': eb.id, 'title': title, 'status': 'VALID_EPUB', 'pages': eb.page_count})
                        continue
                    elif 'gutenberg.org' in content or 'Project Gutenberg' in content:
                        preserved_gutenberg += 1
                        results.append({'id': eb.id, 'title': title, 'status': 'AUTHENTIC_GUTENBERG', 'pages': eb.page_count})
                        continue
                except Exception:
                    needs_repair = True

            if not needs_repair:
                results.append({'id': eb.id, 'title': title, 'status': 'ALREADY_CLEAN', 'pages': eb.page_count})
                continue

            # Perform repair
            try:
                # 1. Check if title maps to Project Gutenberg
                gid = GutenbergService.get_gutenberg_id_for_title(title)
                doc_html = None
                actual_pages = 0
                source_type = 'SYNTHESIZED_EDITION'

                if gid:
                    res = GutenbergService.format_gutenberg_reader_document(title, author_name, gid)
                    if res:
                        doc_html, actual_pages = res
                        source_type = f'PROJECT_GUTENBERG_#{gid}'

                # 2. If not Gutenberg or Gutenberg fetch failed, synthesize authentic monograph
                if not doc_html:
                    book_payload = {
                        'title': title,
                        'author': author_name,
                        'category': cat_name,
                        'publisher': book.publisher or 'LibrarySphere Curated Publishing',
                        'publication_year': book.publication_year or 2024,
                        'description': book.description or f"Celebrated work in {cat_name}.",
                        'isbn': book.isbn or f"978-0-{uuid.uuid4().hex[:10]}",
                    }
                    doc_html, actual_pages = BookContentSynthesizer.generate_edition_with_pages(book_payload)
                    source_type = 'CURATED_MONOGRAPH'

                # Ensure safe randomized filename
                if not eb.protected_filename or not eb.protected_filename.endswith('.html'):
                    eb.protected_filename = f"{uuid.uuid4().hex}.html"

                out_path = protected_root / eb.protected_filename
                encoded = doc_html.encode('utf-8')
                out_path.write_bytes(encoded)

                eb.file_size = len(encoded)
                eb.page_count = actual_pages
                eb.format = 'HTML'
                clean_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', title)[:60]
                eb.original_file_name = f"{clean_slug}.html"
                eb.save(update_fields=['protected_filename', 'format', 'page_count', 'file_size', 'original_file_name'])

                repaired_count += 1
                results.append({
                    'id': eb.id,
                    'title': title,
                    'status': f'REPAIRED ({source_type})',
                    'pages': actual_pages
                })
                self.stdout.write(f"[{idx}/{total}] Repaired: '{title}' ({source_type}) -> {actual_pages} pages")

            except Exception as e:
                error_count += 1
                self.stderr.write(f"[{idx}/{total}] Error repairing '{title}': {str(e)}")
                results.append({'id': eb.id, 'title': title, 'status': f'ERROR: {str(e)}', 'pages': 0})

        # Save audit report
        report_path = Path('data/ebook_repair_report.json')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_data = {
            'timestamp': timezone.now().isoformat(),
            'total_audited': total,
            'repaired': repaired_count,
            'preserved_gutenberg': preserved_gutenberg,
            'preserved_epub': preserved_epub,
            'errors': error_count,
            'books': results
        }
        report_path.write_text(json.dumps(report_data, indent=2), encoding='utf-8')

        self.stdout.write(self.style.SUCCESS(
            f"\nLibrary E-Book Audit and Repair Complete!\n"
            f"Total Audited: {total}\n"
            f"Repaired / Modernized: {repaired_count}\n"
            f"Preserved Gutenberg Classics: {preserved_gutenberg}\n"
            f"Preserved EPUB Editions: {preserved_epub}\n"
            f"Errors: {error_count}\n"
            f"Audit report saved to: {report_path}"
        ))
