import io
from pathlib import Path
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse
from pypdf import PdfWriter

from catalog.models import Category, Author, Book, EBookMetadata
from ebooks.models import EBookAccessLog
from ebooks import services as ebook_services


def create_valid_pdf_bytes():
    """Generates a valid single-page PDF byte buffer using pypdf."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    stream = io.BytesIO()
    writer.write(stream)
    stream.seek(0)
    return stream.getvalue()


class Milestone4EBookTests(TestCase):
    def setUp(self):
        # 1. Create Users
        self.librarian_user = User.objects.create_user(
            username='lib1', password='pass123', email='lib@test.com'
        )
        self.librarian_profile = self.librarian_user.profile
        self.librarian_profile.role = 'LIBRARIAN'
        self.librarian_profile.save()

        self.active_member_user = User.objects.create_user(
            username='member_active', password='pass123', email='active@test.com'
        )
        self.active_member_profile = self.active_member_user.profile
        self.active_member_profile.role = 'MEMBER'
        self.active_member_profile.membership_status = 'ACTIVE'
        self.active_member_profile.save()

        self.expired_member_user = User.objects.create_user(
            username='member_expired', password='pass123', email='expired@test.com'
        )
        self.expired_member_profile = self.expired_member_user.profile
        self.expired_member_profile.role = 'MEMBER'
        self.expired_member_profile.membership_status = 'EXPIRED'
        self.expired_member_profile.save()

        # 2. Create Catalog Book & E-Books
        self.category = Category.objects.create(name='Technology')
        self.author = Author.objects.create(full_name='Alan Turing')
        self.book_both = Book.objects.create(
            title='Computing Machinery',
            isbn='9780123456789',
            category=self.category,
            book_type='BOTH',
            description='A foundational paper.'
        )
        self.book_both.authors.add(self.author)

        # Create physical PDF for read-only e-book
        pdf_data = create_valid_pdf_bytes()
        file_obj = SimpleUploadedFile("computing_machinery.pdf", pdf_data, content_type="application/pdf")
        
        self.readonly_ebook = ebook_services.validate_and_save_ebook(
            file_obj=file_obj,
            book=self.book_both,
            uploaded_by=self.librarian_user,
            access_mode='READ_ONLY',
            rights_status='PUBLIC_DOMAIN',
            rights_text='Public domain classic.',
            access_note='Enjoy reading online.'
        )

        # Create second downloadable e-book
        self.book_downloadable = Book.objects.create(
            title='Open Access Systems',
            isbn='9780987654321',
            category=self.category,
            book_type='EBOOK',
            description='Open access textbook.'
        )
        self.book_downloadable.authors.add(self.author)

        file_obj_2 = SimpleUploadedFile("open_access.pdf", pdf_data, content_type="application/pdf")
        self.downloadable_ebook = ebook_services.validate_and_save_ebook(
            file_obj=file_obj_2,
            book=self.book_downloadable,
            uploaded_by=self.librarian_user,
            access_mode='READ_AND_DOWNLOAD',
            rights_status='OPEN_LICENSE',
            rights_text='Licensed under CC BY 4.0.'
        )

        self.client = Client()

    def test_unauthenticated_user_denied(self):
        """Unauthenticated visitor cannot read, stream, or download e-books."""
        response = self.client.get(reverse('ebooks:read', args=[self.readonly_ebook.id]))
        self.assertRedirects(response, f"/accounts/login/?next=/ebooks/{self.readonly_ebook.id}/read/")

        response = self.client.get(reverse('ebooks:stream', args=[self.readonly_ebook.id]))
        self.assertRedirects(response, f"/accounts/login/?next=/ebooks/{self.readonly_ebook.id}/stream/")

        response = self.client.get(reverse('ebooks:download', args=[self.readonly_ebook.id]))
        self.assertRedirects(response, f"/accounts/login/?next=/ebooks/{self.readonly_ebook.id}/download/")

    def test_active_member_can_read(self):
        """Active member can view the online reader and stream the protected PDF."""
        self.client.login(username='member_active', password='pass123')
        response = self.client.get(reverse('ebooks:read', args=[self.readonly_ebook.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Computing Machinery')

        # Check inline stream view
        stream_response = self.client.get(reverse('ebooks:stream', args=[self.readonly_ebook.id]))
        self.assertEqual(stream_response.status_code, 200)
        self.assertEqual(stream_response['Content-Type'], 'application/pdf')
        self.assertTrue('inline' in stream_response['Content-Disposition'])

    def test_expired_member_denied_access(self):
        """Expired member is blocked from reading, streaming, or downloading."""
        self.client.login(username='member_expired', password='pass123')
        
        response = self.client.get(reverse('ebooks:read', args=[self.readonly_ebook.id]))
        self.assertRedirects(response, reverse('ebooks:catalog'))

        stream_response = self.client.get(reverse('ebooks:stream', args=[self.readonly_ebook.id]))
        self.assertEqual(stream_response.status_code, 403)

    def test_librarian_can_upload_valid_pdf(self):
        """Librarian can upload a valid PDF file."""
        new_book = Book.objects.create(
            title='New Tech Manual',
            isbn='9781111222233',
            category=self.category,
            book_type='EBOOK',
            description='Tech manual.'
        )
        pdf_bytes = create_valid_pdf_bytes()
        file_obj = SimpleUploadedFile("manual.pdf", pdf_bytes, content_type="application/pdf")

        ebook = ebook_services.validate_and_save_ebook(
            file_obj=file_obj,
            book=new_book,
            uploaded_by=self.librarian_user,
            access_mode='READ_ONLY',
            rights_status='DEMO_ONLY',
            rights_text='Demo manual'
        )
        self.assertIsNotNone(ebook.id)
        self.assertEqual(ebook.page_count, 1)
        self.assertTrue(ebook.protected_filename.endswith('.pdf'))

    def test_invalid_file_extension_rejected(self):
        """Uploading a non-PDF file extension (.txt) raises ValueError."""
        file_obj = SimpleUploadedFile("document.txt", b"Hello World", content_type="text/plain")
        with self.assertRaises(ValueError) as ctx:
            ebook_services.validate_and_save_ebook(
                file_obj=file_obj,
                book=self.book_both,
                uploaded_by=self.librarian_user,
                access_mode='READ_ONLY',
                rights_status='DEMO_ONLY',
                rights_text='Demo'
            )
        self.assertIn("Invalid file extension", str(ctx.exception))

    def test_invalid_pdf_signature_rejected(self):
        """A file ending in .pdf but lacking %PDF- signature is rejected."""
        fake_pdf = SimpleUploadedFile("fake.pdf", b"NOT_A_REAL_PDF_FILE", content_type="application/pdf")
        with self.assertRaises(ValueError) as ctx:
            ebook_services.validate_and_save_ebook(
                file_obj=fake_pdf,
                book=self.book_both,
                uploaded_by=self.librarian_user,
                access_mode='READ_ONLY',
                rights_status='DEMO_ONLY',
                rights_text='Demo'
            )
        self.assertIn("Invalid file format", str(ctx.exception))

    def test_oversized_pdf_rejected(self):
        """A PDF exceeding MAX_EBOOK_FILE_SIZE is rejected."""
        # Mock a file with size larger than 20MB
        large_file = SimpleUploadedFile("huge.pdf", b"%PDF-1.4 " + b"X" * 100, content_type="application/pdf")
        large_file.size = 25 * 1024 * 1024  # 25 MB
        
        with self.assertRaises(ValueError) as ctx:
            ebook_services.validate_and_save_ebook(
                file_obj=large_file,
                book=self.book_both,
                uploaded_by=self.librarian_user,
                access_mode='READ_ONLY',
                rights_status='DEMO_ONLY',
                rights_text='Demo'
            )
        self.assertIn("File size exceeds maximum allowed limit", str(ctx.exception))

    def test_readonly_ebook_cannot_be_downloaded(self):
        """A READ_ONLY e-book denies download requests."""
        self.client.login(username='member_active', password='pass123')
        response = self.client.get(reverse('ebooks:download', args=[self.readonly_ebook.id]))
        self.assertRedirects(response, reverse('ebooks:detail', args=[self.readonly_ebook.id]))

    def test_downloadable_ebook_can_be_downloaded(self):
        """A READ_AND_DOWNLOAD e-book can be downloaded by an active member."""
        self.client.login(username='member_active', password='pass123')
        response = self.client.get(reverse('ebooks:download', args=[self.downloadable_ebook.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue('attachment' in response['Content-Disposition'])

    def test_reading_creates_access_log(self):
        """Reading an e-book creates a READ access log entry."""
        self.client.login(username='member_active', password='pass123')
        initial_count = EBookAccessLog.objects.filter(user=self.active_member_user, action='READ').count()
        
        self.client.get(reverse('ebooks:read', args=[self.readonly_ebook.id]))
        
        new_count = EBookAccessLog.objects.filter(user=self.active_member_user, action='READ').count()
        self.assertEqual(new_count, initial_count + 1)

    def test_downloading_creates_access_log(self):
        """Downloading an e-book creates a DOWNLOAD access log entry."""
        self.client.login(username='member_active', password='pass123')
        initial_count = EBookAccessLog.objects.filter(user=self.active_member_user, action='DOWNLOAD').count()
        
        self.client.get(reverse('ebooks:download', args=[self.downloadable_ebook.id]))
        
        new_count = EBookAccessLog.objects.filter(user=self.active_member_user, action='DOWNLOAD').count()
        self.assertEqual(new_count, initial_count + 1)

    def test_ordinary_member_cannot_access_management_pages(self):
        """Regular members cannot access librarian management/upload/reports pages."""
        self.client.login(username='member_active', password='pass123')
        
        response = self.client.get(reverse('ebooks:manage'))
        self.assertEqual(response.status_code, 302)  # Redirected due to user_passes_test failure

        response = self.client.get(reverse('ebooks:upload'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('ebooks:reports'))
        self.assertEqual(response.status_code, 302)

    def test_protected_pdf_not_exposed_in_public_media(self):
        """Protected PDF files are not served under public MEDIA_URL (/media/...)."""
        public_url = f"/media/ebooks/{self.readonly_ebook.protected_filename}"
        response = self.client.get(public_url)
        self.assertEqual(response.status_code, 404)

    def test_html_ebook_upload_and_stream(self):
        """Librarian can upload HTML files (.html) and active members can stream HTML content."""
        html_bytes = b"<!DOCTYPE html><html><body><h1>LibrarySphere HTML E-Book</h1><p>Testing HTML content.</p></body></html>"
        html_file = SimpleUploadedFile("sample_book.html", html_bytes, content_type="text/html")
        
        ebook = ebook_services.validate_and_save_ebook(
            file_obj=html_file,
            book=self.book_both,
            uploaded_by=self.librarian_user,
            access_mode='READ_AND_DOWNLOAD',
            rights_status='PUBLIC_DOMAIN',
            rights_text='Public Domain HTML'
        )

        self.assertEqual(ebook.format, 'HTML')
        self.assertTrue(ebook.protected_filename.endswith('.html'))

        # Test streaming HTML content
        self.client.login(username='member_active', password='pass123')
        response = self.client.get(reverse('ebooks:stream', args=[ebook.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    def test_manual_title_ebook_upload(self):
        """Librarian can type a new book title manually when uploading an e-book."""
        self.client.login(username='lib1', password='pass123')
        html_bytes = b"<!DOCTYPE html><html><body><h1>Manual Title Test</h1></body></html>"
        html_file = SimpleUploadedFile("manual_test.html", html_bytes, content_type="text/html")

        response = self.client.post(
            reverse('ebooks:upload'),
            data={
                'manual_title': 'Advanced Quantum Mechanics 2026',
                'file': html_file,
                'access_mode': 'READ_ONLY',
                'rental_price': '0.00',
                'rights_status': 'PUBLIC_DOMAIN',
                'rights_text': 'Public Domain Book'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Book.objects.filter(title='Advanced Quantum Mechanics 2026').exists())


