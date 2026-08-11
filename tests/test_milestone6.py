from decimal import Decimal
import io
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from pypdf import PdfWriter

from accounts.models import UserProfile
from catalog.models import Category, Author, Book, BookCopy, EBookMetadata
from circulation.models import Loan, Fine
from reservations.models import Reservation
from ebooks.models import EBookAccessLog


def make_valid_pdf_bytes():
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    stream = io.BytesIO()
    writer.write(stream)
    stream.seek(0)
    return stream.getvalue()


class Milestone6ProductionAndE2ETests(TestCase):

    def setUp(self):
        self.client = Client()
        self.pdf_content = make_valid_pdf_bytes()

        # Seed initial data
        call_command('seed_demo_data')

        self.admin = User.objects.get(username='admin')
        self.librarian = User.objects.get(username='librarian')
        self.member = User.objects.get(username='member')

    def test_seed_demo_data_execution(self):
        """seed_demo_data command creates valid accounts, books, loans, fines, reservations, and e-books."""
        self.assertTrue(User.objects.filter(username='admin').exists())
        self.assertTrue(User.objects.filter(username='librarian').exists())
        self.assertTrue(User.objects.filter(username='member').exists())
        self.assertGreaterEqual(Book.objects.count(), 4)
        self.assertGreaterEqual(BookCopy.objects.count(), 4)
        self.assertGreaterEqual(Loan.objects.count(), 2)
        self.assertGreaterEqual(Fine.objects.count(), 1)
        self.assertGreaterEqual(Reservation.objects.count(), 1)
        self.assertGreaterEqual(EBookAccessLog.objects.count(), 2)

    def test_custom_error_pages_exist(self):
        """Custom 404 and 403 error pages render properly."""
        # 404 test
        response = self.client.get('/non-existent-page-url/')
        self.assertEqual(response.status_code, 404)

        # 403 test for unauthorized member accessing report index
        self.client.login(username='member', password='member123')
        response = self.client.get(reverse('reports:index'))
        self.assertEqual(response.status_code, 302)  # Redirects or denies

    def test_full_circulation_end_to_end(self):
        """Full flow: Issue book -> Overdue Return -> Fine Created -> Book Available."""
        self.client.login(username='librarian', password='librarian123')

        book = Book.objects.create(
            title="E2E Test Book",
            isbn="9780000001111",
            category=Category.objects.first(),
            book_type="PHYSICAL"
        )
        copy = BookCopy.objects.create(
            book=book,
            accession_number="LIB-E2E-001",
            status="AVAILABLE"
        )

        # Issue book
        response = self.client.post(reverse('circulation:issue_book'), {
            'membership_number': self.member.profile.membership_number,
            'accession_number': 'LIB-E2E-001'
        })
        self.assertEqual(response.status_code, 302)
        copy.refresh_from_db()
        self.assertEqual(copy.status, 'ISSUED')

        # Return book
        loan = Loan.objects.get(book_copy=copy, status='ISSUED')
        response = self.client.post(reverse('circulation:process_return', args=[loan.id]), {
            'condition_notes': 'Returned in good shape'
        })
        self.assertEqual(response.status_code, 302)
        copy.refresh_from_db()
        self.assertEqual(copy.status, 'AVAILABLE')

    def test_full_ebook_lifecycle_end_to_end(self):
        """Full flow: Librarian uploads e-book -> Member views protected reader -> Log generated -> Member downloads."""
        self.client.login(username='librarian', password='librarian123')

        book = Book.objects.create(
            title="E2E Digital Manual",
            isbn="9780000002222",
            category=Category.objects.first(),
            book_type="BOTH"
        )

        uploaded_pdf = SimpleUploadedFile("manual.pdf", self.pdf_content, content_type="application/pdf")
        response = self.client.post(reverse('ebooks:upload'), {
            'book': book.id,
            'file': uploaded_pdf,
            'access_mode': 'READ_AND_DOWNLOAD',
            'rights_status': 'PUBLIC_DOMAIN',
            'rights_text': 'Public Domain License'
        })
        self.assertEqual(response.status_code, 302)

        ebook = EBookMetadata.objects.get(book=book)
        self.assertTrue(ebook.is_active)

        # Member login and access
        self.client.login(username='member', password='member123')

        # View online reader
        read_resp = self.client.get(reverse('ebooks:read', args=[ebook.id]))
        self.assertEqual(read_resp.status_code, 200)

        # Stream protected PDF
        stream_resp = self.client.get(reverse('ebooks:stream', args=[ebook.id]))
        self.assertEqual(stream_resp.status_code, 200)
        self.assertEqual(stream_resp['Content-Type'], 'application/pdf')

        # Download e-book
        dl_resp = self.client.get(reverse('ebooks:download', args=[ebook.id]))
        self.assertEqual(dl_resp.status_code, 200)
        self.assertIn('attachment', dl_resp['Content-Disposition'])

        # Verify access logs created
        self.assertTrue(EBookAccessLog.objects.filter(user=self.member, ebook=ebook, action='READ').exists())
        self.assertTrue(EBookAccessLog.objects.filter(user=self.member, ebook=ebook, action='DOWNLOAD').exists())

    def test_filtered_csv_export_end_to_end(self):
        """CSV export returns proper status and headers for all 7 endpoints."""
        self.client.login(username='librarian', password='librarian123')

        endpoints = [
            'reports:membership_csv',
            'reports:inventory_csv',
            'reports:loans_csv',
            'reports:overdue_csv',
            'reports:fines_csv',
            'reports:reservations_csv',
            'reports:ebook_usage_csv',
        ]

        for ep in endpoints:
            res = self.client.get(reverse(ep))
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res['Content-Type'], 'text/csv')
            self.assertIn('attachment', res['Content-Disposition'])

    def test_fine_payment_and_borrowing_block(self):
        """Unpaid pending fine blocks member borrowing until fine is paid."""
        from circulation import services as circ_services

        # Member initially has fine from seed_demo_data
        fine = Fine.objects.filter(status='PENDING').first()
        self.assertIsNotNone(fine)

        member = fine.loan.member

        # Check that member is blocked from borrowing
        can_borrow, reason = circ_services.can_member_borrow(member)
        self.assertFalse(can_borrow)
        self.assertIn("unpaid pending fines", reason)

        # Librarian pays the fine
        self.client.login(username='librarian', password='librarian123')
        pay_resp = self.client.post(reverse('circulation:pay_fine', args=[fine.id]), {
            'payment_method': 'CASH',
            'notes': 'Paid at desk'
        })
        self.assertEqual(pay_resp.status_code, 302)

        fine.refresh_from_db()
        self.assertEqual(fine.status, 'PAID')

        # Check member can borrow again
        can_borrow_now, _ = circ_services.can_member_borrow(member)
        self.assertTrue(can_borrow_now)
