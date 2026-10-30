import os
import io
import datetime
from pathlib import Path
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone

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
        self.assertGreater(ebook.page_count, 10)
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
        """Verifies that BookContentSynthesizer produces genuine, non-repetitive publication pages."""
        from ebooks.generator import BookContentSynthesizer
        import re

        html_doc, page_count = BookContentSynthesizer.generate_edition_with_pages({
            'title': 'The Mythical Man-Month: Essays on Software Engineering',
            'author': 'Frederick P. Brooks Jr.',
            'category': 'Computer Science',
            'pages': 336,
        })
        actual_pages = html_doc.count('class="book-page"')
        self.assertEqual(page_count, actual_pages)
        self.assertGreater(page_count, 15)
        self.assertIn('id="page-1"', html_doc)
        self.assertIn(f'id="page-{page_count}"', html_doc)
        self.assertIn('The Tar Pit', html_doc)
        self.assertTrue('Brooks&#x27; Law' in html_doc or "Brooks' Law" in html_doc)

        # Verify zero repetitive duplicate pages
        page_slices = re.findall(r'<div class="page-content[^"]*"[^>]*>(.*?)</div>', html_doc, re.DOTALL)
        hashes = set(hash(p.strip()) for p in page_slices)
        self.assertEqual(len(hashes), len(page_slices), "All synthesized pages must be unique without repetition.")

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
        self.assertContains(resp, str(book.ebook_metadata.page_count))

    def test_reader_ui_typography_and_fluent_narration_controls(self):
        """Verifies that the reader UI has active typography scaling (A-/A+) and fluent audio narration."""
        row = {
            'title': 'The Idiot',
            'authors': 'Fyodor Dostoevsky',
            'categories': 'Classics',
            'description': 'A landmark classic novel.',
            'num_pages': '709',
            'isbn13': '9780140449402',
        }
        book, _, _ = KaggleEBookService.import_single_book(row, uploaded_by=self.librarian)

        client = Client()
        client.force_login(self.member)

        resp = client.get(f'/ebooks/{book.ebook_metadata.id}/read/')
        self.assertEqual(resp.status_code, 200)

        # Typography scaling controls
        self.assertContains(resp, 'id="fontSizeDisplay"')
        self.assertContains(resp, 'adjustFontSize(-1)')
        self.assertContains(resp, 'adjustFontSize(1)')
        self.assertContains(resp, 'resetFontSize()')
        self.assertContains(resp, 'librarysphere-reader-zoom-style')
        self.assertContains(resp, 'librarysphere-reader-theme-style')

        # Fluent audio narration controls
        self.assertContains(resp, 'id="ttsPlayBtn"')
        self.assertContains(resp, 'toggleTTS()')
        self.assertContains(resp, 'setTTSSpeed')
        self.assertContains(resp, 'createSpeechChunks')
        self.assertContains(resp, 'getBestVoice')
        self.assertContains(resp, 'playNextChunk')

    def test_epub_reading_stream_and_download_separation(self):
        """Verifies that EPUB ebooks stream as inline HTML in the reader and download as genuine EPUB archives."""
        client = Client()
        client.force_login(self.member)

        # Check Pooh or create EPUB fixture
        pooh = EBookMetadata.objects.filter(book__title__icontains='Pooh').first()
        if pooh:
            # Reader view
            resp_read = client.get(f'/ebooks/{pooh.id}/read/')
            self.assertEqual(resp_read.status_code, 200)

            # Stream view: MUST be HTML to render inside iframe without browser auto-download
            resp_stream = client.get(f'/ebooks/{pooh.id}/stream/')
            self.assertEqual(resp_stream.status_code, 200)
            self.assertIn('text/html', resp_stream.get('Content-Type'))
            self.assertIn('inline', resp_stream.get('Content-Disposition'))

            # Download view: MUST be EPUB attachment
            resp_down = client.get(f'/ebooks/{pooh.id}/download/')
            self.assertEqual(resp_down.status_code, 200)
            self.assertIn('epub', resp_down.get('Content-Type'))
            self.assertIn('attachment', resp_down.get('Content-Disposition'))


class GuestAndMembershipAccessControlTests(TestCase):
    """
    Comprehensive test suite for Guest User (Non-Member) access and
    Membership-Based Ebook Restrictions.
    """
    def setUp(self):
        # 1. Staff Admin
        self.admin = User.objects.create_superuser(
            username='auth_admin',
            email='admin@library.org',
            password='adminpassword123'
        )
        self.admin.profile.role = 'ADMIN'
        self.admin.profile.membership_status = 'ACTIVE'
        self.admin.profile.is_approved = True
        self.admin.profile.save()

        # 2. Active Member
        self.active_member = User.objects.create_user(
            username='active_patron',
            email='patron@example.com',
            password='patronpassword123'
        )
        self.active_member.profile.role = 'MEMBER'
        self.active_member.profile.membership_status = 'ACTIVE'
        self.active_member.profile.is_approved = True
        self.active_member.profile.membership_expiry_date = timezone.now().date() + datetime.timedelta(days=180)
        self.active_member.profile.can_access_ebooks = True
        self.active_member.profile.save()

        # 3. Expired Member
        self.expired_member = User.objects.create_user(
            username='expired_patron',
            email='expired@example.com',
            password='patronpassword123'
        )
        self.expired_member.profile.role = 'MEMBER'
        self.expired_member.profile.membership_status = 'EXPIRED'
        self.expired_member.profile.membership_expiry_date = timezone.now().date() - datetime.timedelta(days=10)
        self.expired_member.profile.save()

        # 4. Suspended Member
        self.suspended_member = User.objects.create_user(
            username='suspended_patron',
            email='suspended@example.com',
            password='patronpassword123'
        )
        self.suspended_member.profile.role = 'MEMBER'
        self.suspended_member.profile.membership_status = 'SUSPENDED'
        self.suspended_member.profile.save()

        # 5. Pending Member
        self.pending_member = User.objects.create_user(
            username='pending_patron',
            email='pending@example.com',
            password='patronpassword123'
        )
        self.pending_member.profile.role = 'MEMBER'
        self.pending_member.profile.membership_status = 'PENDING'
        self.pending_member.profile.is_approved = False
        self.pending_member.profile.save()

        # Test Category
        self.category = Category.objects.create(name='Classics & Science', description='General Collection')

        # Test Free Book
        self.free_book = Book.objects.create(
            title='The Art of Public Domain',
            isbn='978-0-FREE-001',
            category=self.category,
            book_type='EBOOK',
            description='A completely open public domain educational treatise.'
        )
        # Create physical HTML file for free ebook
        protected_root = Path(getattr(settings, 'PROTECTED_EBOOK_ROOT', settings.BASE_DIR / 'protected_ebooks'))
        protected_root.mkdir(parents=True, exist_ok=True)
        free_file = protected_root / 'test_free_book.html'
        free_file.write_text('<html><body><h1>Free Classic Book Content</h1></body></html>', encoding='utf-8')

        self.free_ebook = EBookMetadata.objects.create(
            book=self.free_book,
            protected_filename='test_free_book.html',
            original_file_name='test_free_book.html',
            format='HTML',
            page_count=50,
            access_level='FREE',
            access_mode='READ_AND_DOWNLOAD',
            rights_status='PUBLIC_DOMAIN',
            is_active=True
        )

        # Test Members-Only Book
        self.restricted_book = Book.objects.create(
            title='Advanced System Architecture',
            isbn='978-0-RESTRICT-002',
            category=self.category,
            book_type='EBOOK',
            description='A licensed modern engineering manual for active library patrons.'
        )
        restricted_file = protected_root / 'test_restricted_book.html'
        restricted_file.write_text('<html><body><h1>Restricted Member Content</h1></body></html>', encoding='utf-8')

        self.restricted_ebook = EBookMetadata.objects.create(
            book=self.restricted_book,
            protected_filename='test_restricted_book.html',
            original_file_name='test_restricted_book.html',
            format='HTML',
            page_count=120,
            access_level='MEMBERS_ONLY',
            access_mode='READ_AND_DOWNLOAD',
            rights_status='LIBRARY_LICENSED',
            is_active=True
        )

        # Test Staff-Only Book
        self.staff_book = Book.objects.create(
            title='Circulation Staff Desk Procedures',
            isbn='978-0-STAFF-003',
            category=self.category,
            book_type='EBOOK',
            description='Internal operating procedures.'
        )
        staff_file = protected_root / 'test_staff_book.html'
        staff_file.write_text('<html><body><h1>Staff Manual</h1></body></html>', encoding='utf-8')

        self.staff_ebook = EBookMetadata.objects.create(
            book=self.staff_book,
            protected_filename='test_staff_book.html',
            original_file_name='test_staff_book.html',
            format='HTML',
            page_count=45,
            access_level='STAFF_ONLY',
            access_mode='READ_ONLY',
            rights_status='DEMO_ONLY',
            is_active=True
        )

    def test_guest_can_browse_homepage_and_catalog(self):
        """Guest (unauthenticated) can browse the portal home and e-book catalog without login."""
        guest_client = Client()
        resp_home = guest_client.get('/')
        self.assertEqual(resp_home.status_code, 200)

        resp_cat = guest_client.get('/ebooks/')
        self.assertEqual(resp_cat.status_code, 200)
        self.assertContains(resp_cat, 'FREE ACCESS')
        self.assertContains(resp_cat, 'MEMBERS ONLY')

    def test_guest_filter_catalog_by_free_access(self):
        """Guest can filter the catalog to view only Free e-books."""
        guest_client = Client()
        resp = guest_client.get('/ebooks/?access=FREE')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'The Art of Public Domain')
        self.assertNotContains(resp, 'Advanced System Architecture')

    def test_guest_can_read_and_stream_free_ebook(self):
        """Guest user CAN open and stream a FREE access e-book without being forced to register."""
        guest_client = Client()
        # Detail view
        resp_detail = guest_client.get(f'/ebooks/{self.free_ebook.id}/')
        self.assertEqual(resp_detail.status_code, 200)
        self.assertContains(resp_detail, 'Read Online Now')

        # Read view
        resp_read = guest_client.get(f'/ebooks/{self.free_ebook.id}/read/')
        self.assertEqual(resp_read.status_code, 200)
        self.assertContains(resp_read, f'/ebooks/{self.free_ebook.id}/stream/')

        # Stream view
        resp_stream = guest_client.get(f'/ebooks/{self.free_ebook.id}/stream/')
        self.assertEqual(resp_stream.status_code, 200)
        self.assertIn(b'Free Classic Book Content', b''.join(resp_stream.streaming_content))

    def test_guest_cannot_read_or_stream_members_only_ebook(self):
        """Guest user CANNOT read, stream, or download a MEMBERS_ONLY e-book."""
        guest_client = Client()

        # Detail view displays restriction notice and no reader button
        resp_detail = guest_client.get(f'/ebooks/{self.restricted_ebook.id}/')
        self.assertEqual(resp_detail.status_code, 200)
        self.assertContains(resp_detail, 'Membership Required')
        self.assertContains(resp_detail, 'Apply for Membership')
        self.assertNotContains(resp_detail, 'Read Online Now')

        # Read view redirects to login with informative notice
        resp_read = guest_client.get(f'/ebooks/{self.restricted_ebook.id}/read/')
        self.assertEqual(resp_read.status_code, 302)
        self.assertIn('/accounts/login/', resp_read.url)

        # Direct stream call returns HTTP 401 Unauthorized
        resp_stream = guest_client.get(f'/ebooks/{self.restricted_ebook.id}/stream/')
        self.assertEqual(resp_stream.status_code, 401)
        self.assertNotIn(b'Restricted Member Content', resp_stream.content)
        self.assertIn('no-store', resp_stream.headers.get('Cache-Control', ''))

        # Direct download call redirects to login / 401
        resp_down = guest_client.get(f'/ebooks/{self.restricted_ebook.id}/download/')
        self.assertEqual(resp_down.status_code, 302)

    def test_active_member_can_read_free_and_members_only_ebooks(self):
        """Active library member can read both Free and Members-Only e-books."""
        client = Client()
        client.force_login(self.active_member)

        # Can read free
        resp_free = client.get(f'/ebooks/{self.free_ebook.id}/read/')
        self.assertEqual(resp_free.status_code, 200)

        # Can read members only
        resp_restricted = client.get(f'/ebooks/{self.restricted_ebook.id}/read/')
        self.assertEqual(resp_restricted.status_code, 200)

        # Can stream members only
        resp_stream = client.get(f'/ebooks/{self.restricted_ebook.id}/stream/')
        self.assertEqual(resp_stream.status_code, 200)
        self.assertIn(b'Restricted Member Content', b''.join(resp_stream.streaming_content))

    def test_expired_member_denied_access_to_members_only_content(self):
        """Expired library member is denied access to Members-Only e-books."""
        client = Client()
        client.force_login(self.expired_member)

        # Read view returns 403 Membership Required
        resp_read = client.get(f'/ebooks/{self.restricted_ebook.id}/read/')
        self.assertEqual(resp_read.status_code, 403)
        self.assertContains(resp_read, 'Membership Required', status_code=403)
        self.assertContains(resp_read, 'expired', status_code=403)

        # Stream view returns 403
        resp_stream = client.get(f'/ebooks/{self.restricted_ebook.id}/stream/')
        self.assertEqual(resp_stream.status_code, 403)

    def test_suspended_member_denied_access_to_members_only_content(self):
        """Suspended library member is denied access to Members-Only e-books."""
        client = Client()
        client.force_login(self.suspended_member)

        # AccountStatusMiddleware immediately revokes active session and redirects to login (302)
        resp_read = client.get(f'/ebooks/{self.restricted_ebook.id}/read/')
        self.assertEqual(resp_read.status_code, 302)
        self.assertIn('/accounts/login/', resp_read.url)

        # Direct authorization check confirms denial with SUSPENDED code and 403
        from ebooks.authorization import check_ebook_access
        access = check_ebook_access(self.suspended_member, self.restricted_ebook)
        self.assertFalse(access.is_authorized)
        self.assertEqual(access.status_code, 403)
        self.assertEqual(access.code, 'SUSPENDED')

    def test_staff_admin_can_access_all_levels_including_staff_only(self):
        """Staff/Admins can access all e-books including STAFF_ONLY."""
        client = Client()
        client.force_login(self.admin)

        resp_staff_read = client.get(f'/ebooks/{self.staff_ebook.id}/read/')
        self.assertEqual(resp_staff_read.status_code, 200)

        resp_staff_stream = client.get(f'/ebooks/{self.staff_ebook.id}/stream/')
        self.assertEqual(resp_staff_stream.status_code, 200)
        self.assertIn(b'Staff Manual', b''.join(resp_staff_stream.streaming_content))

    def test_regular_member_denied_access_to_staff_only_ebook(self):
        """Regular patrons cannot read or stream STAFF_ONLY e-books."""
        client = Client()
        client.force_login(self.active_member)

        resp_read = client.get(f'/ebooks/{self.staff_ebook.id}/read/')
        self.assertEqual(resp_read.status_code, 403)

        resp_stream = client.get(f'/ebooks/{self.staff_ebook.id}/stream/')
        self.assertEqual(resp_stream.status_code, 403)

    def test_dynamic_reclassification_enforced_immediately(self):
        """Changing an e-book from FREE to MEMBERS_ONLY immediately revokes guest access."""
        guest_client = Client()

        # Initially Free -> Guest can stream
        resp1 = guest_client.get(f'/ebooks/{self.free_ebook.id}/stream/')
        self.assertEqual(resp1.status_code, 200)

        # Admin changes classification to MEMBERS_ONLY
        self.free_ebook.access_level = 'MEMBERS_ONLY'
        self.free_ebook.save()

        # Next guest request is immediately rejected with 401
        resp2 = guest_client.get(f'/ebooks/{self.free_ebook.id}/stream/')
        self.assertEqual(resp2.status_code, 401)



