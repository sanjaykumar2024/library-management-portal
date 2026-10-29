import os
import io
from pathlib import Path
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.management import call_command
from django.conf import settings

from accounts.models import UserProfile
from catalog.models import Book, Author, Category, EBookMetadata, BookReview
from ebooks.kaggle_service import KaggleEBookService


class KaggleEBookImportTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='kaggle_admin',
            email='admin@library.org',
            password='adminpassword123'
        )
        self.admin.profile.role = 'ADMIN'
        self.admin.profile.save()

        self.librarian = User.objects.create_user(
            username='kaggle_lib',
            email='lib@library.org',
            password='libpassword123'
        )
        self.librarian.profile.role = 'LIBRARIAN'
        self.librarian.profile.save()

        self.member = User.objects.create_user(
            username='kaggle_member',
            email='member@example.com',
            password='memberpassword123'
        )
        self.member.profile.role = 'MEMBER'
        self.member.profile.membership_status = 'ACTIVE'
        self.member.profile.save()

    def test_import_single_book(self):
        row = {
            'title': 'Designing Data-Intensive Applications',
            'subtitle': 'The Big Ideas Behind Systems',
            'authors': 'Martin Kleppmann',
            'categories': 'Computer Science',
            'description': 'A landmark book on reliable distributed computing systems.',
            'published_year': '2017',
            'average_rating': '4.8',
            'num_pages': '616',
            'publisher': "O'Reilly Media",
            'isbn13': '9781449373320',
        }

        book, created, msg = KaggleEBookService.import_single_book(
            row=row,
            uploaded_by=self.librarian,
            access_mode='READ_AND_DOWNLOAD',
            rights_status='LIBRARY_LICENSED'
        )

        self.assertTrue(created)
        self.assertIsNotNone(book)
        self.assertEqual(book.title, 'Designing Data-Intensive Applications')
        self.assertEqual(book.isbn, '9781449373320')
        self.assertEqual(book.category.name, 'Computer Science')
        self.assertTrue(book.authors.filter(full_name='Martin Kleppmann').exists())
        self.assertEqual(book.book_type, 'BOTH')

        # Check EBookMetadata
        self.assertTrue(hasattr(book, 'ebook_metadata'))
        ebook = book.ebook_metadata
        self.assertEqual(ebook.format, 'HTML')
        self.assertEqual(ebook.page_count, 616)
        self.assertEqual(ebook.access_mode, 'READ_AND_DOWNLOAD')
        self.assertTrue(ebook.is_active)

        # Check file exists in protected storage
        protected_root = Path(getattr(settings, 'PROTECTED_EBOOK_ROOT', settings.BASE_DIR / 'protected_ebooks'))
        file_path = protected_root / ebook.protected_filename
        self.assertTrue(file_path.exists())
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('Designing Data-Intensive Applications', content)
        self.assertIn('Martin Kleppmann', content)
        self.assertIn('Executive Synopsis', content)

    def test_import_from_csv_stream(self):
        csv_data = """isbn13,title,subtitle,authors,categories,thumbnail,description,published_year,average_rating,num_pages,ratings_count,publisher
9780132350884,"Clean Code","A Handbook of Agile Craftsmanship","Robert C. Martin","Computer Science","","Even bad code can function.","2008","4.4","464","32000","Prentice Hall"
9780441172719,"Dune","The Epic Sci-Fi Masterpiece","Frank Herbert","Science Fiction","","Set on desert planet Arrakis.","1965","4.7","688","950000","Ace Books"
"""
        stats = KaggleEBookService.import_from_csv(
            file_or_path=io.StringIO(csv_data),
            uploaded_by=self.librarian,
            overwrite=True
        )

        self.assertEqual(stats['total_rows'], 2)
        self.assertEqual(stats['imported'], 2)
        self.assertEqual(stats['errors'], 0)
        self.assertEqual(Book.objects.filter(isbn='9780132350884').count(), 1)
        self.assertEqual(Book.objects.filter(isbn='9780441172719').count(), 1)

    def test_import_kaggle_management_command(self):
        call_command('import_kaggle_ebooks', limit=3, overwrite=True)
        # Should have imported at least 3 books
        self.assertGreaterEqual(Book.objects.filter(ebook_metadata__rights_text__icontains='Kaggle').count(), 3)

    def test_kaggle_import_view_librarian_access(self):
        client = Client()
        client.force_login(self.librarian)

        # GET
        resp = client.get('/ebooks/kaggle-import/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Add Kaggle Books')

        # POST 1-click curated
        post_resp = client.post('/ebooks/kaggle-import/', {'action': 'import_curated'})
        self.assertEqual(post_resp.status_code, 302)

    def test_member_streaming_reader_access(self):
        # Create a book via Kaggle service
        row = {
            'title': 'Test Kaggle Stream Book',
            'authors': 'Alice Wonder',
            'categories': 'Technology',
            'description': 'Exploring the wonders of digital libraries.',
            'isbn13': '9789998887771',
        }
        book, _, _ = KaggleEBookService.import_single_book(row, uploaded_by=self.librarian)

        client = Client()
        client.force_login(self.member)

        # Reader view
        read_resp = client.get(f'/ebooks/{book.ebook_metadata.id}/read/')
        self.assertEqual(read_resp.status_code, 200)
        self.assertContains(read_resp, 'Test Kaggle Stream Book')
        self.assertContains(read_resp, 'reader-fullscreen-bar')
        self.assertContains(read_resp, 'reader-card-container')
        self.assertContains(read_resp, 'reader-fullscreen-btn')
        self.assertContains(read_resp, 'reader-audio-btn')
        self.assertContains(read_resp, 'reader-notes-btn')
        self.assertContains(read_resp, 'reader-zoom-btn-group')
        self.assertContains(read_resp, 'Exit Fullscreen')

        # Stream view
        stream_resp = client.get(f'/ebooks/{book.ebook_metadata.id}/stream/')
        self.assertEqual(stream_resp.status_code, 200)
        self.assertEqual(stream_resp.headers.get('Content-Type'), 'text/html; charset=utf-8')
        content = b''.join(stream_resp.streaming_content).decode('utf-8')
        self.assertIn('Test Kaggle Stream Book', content)

    def test_full_page_extent_synthesis(self):
        """Verifies that BookContentSynthesizer produces exact page counts across small and large books."""
        from ebooks.generator import BookContentSynthesizer

        for target in [120, 480, 616, 1000]:
            html_doc = BookContentSynthesizer.generate_full_edition({
                'title': f'Synthesis Test Volume {target}',
                'author': 'Dr. Verification',
                'category': 'Computer Science',
                'pages': target,
            })
            page_count = html_doc.count('class="book-page"')
            self.assertEqual(page_count, target, f"Expected {target} pages, got {page_count}")
            self.assertIn('id="page-1"', html_doc)
            self.assertIn(f'id="page-{target}"', html_doc)
            self.assertNotIn(f'id="page-{target + 1}"', html_doc)

    def test_reader_ui_has_pagination_and_scrubber(self):
        """Verifies that the reader template renders complete pagination, jump controls, and scrubber."""
        row = {
            'title': 'High Scale Data Systems',
            'authors': 'Dr. System',
            'categories': 'Computer Science',
            'description': 'A comprehensive exploration of high-scale data systems.',
            'num_pages': '550',
            'isbn13': '9780123456789',
        }
        book, _, _ = KaggleEBookService.import_single_book(row, uploaded_by=self.librarian)

        client = Client()
        client.force_login(self.member)

        resp = client.get(f'/ebooks/{book.ebook_metadata.id}/read/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'id="readerPageInput"')
        self.assertContains(resp, 'id="readerPageScrubber"')
        self.assertContains(resp, 'id="btnPrevPage"')
        self.assertContains(resp, 'id="btnNextPage"')
        self.assertContains(resp, 'id="tocDrawer"')
        self.assertContains(resp, 'id="viewModeToggleBtn"')
        self.assertContains(resp, 'reader-edge-prev')
        self.assertContains(resp, 'reader-edge-next')
        self.assertContains(resp, '550')

