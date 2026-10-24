import json
from decimal import Decimal
from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.management import call_command

from accounts.models import UserProfile, MembershipRequest
from catalog.models import Book, BookCopy, Category, Author, BookReview, UserBookList
from circulation.models import Loan, Fine
from circulation.services import issue_book, scan_and_notify_overdue_loans
from core.models import ActivityLog, log_activity
from ebooks.models import EBookMetadata
from ebooks.open_source import OpenSourceEBookService
from notifications.models import Notification


class AdvancedFeaturesIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Admin
        self.admin_user = User.objects.create_superuser(
            username='admin_test', password='password123', email='admin@test.com'
        )
        self.admin_profile = self.admin_user.profile
        self.admin_profile.role = 'ADMIN'
        self.admin_profile.save()

        # Create Librarian
        self.librarian_user = User.objects.create_user(
            username='librarian_test', password='password123', email='lib@test.com'
        )
        self.librarian_profile = self.librarian_user.profile
        self.librarian_profile.role = 'LIBRARIAN'
        self.librarian_profile.save()

        # Create Member
        self.member_user = User.objects.create_user(
            username='member_test', password='password123', email='member@test.com'
        )
        self.member_profile = self.member_user.profile
        self.member_profile.role = 'MEMBER'
        self.member_profile.membership_status = 'ACTIVE'
        self.member_profile.tier = 'STUDENT'
        self.member_profile.save()

        # Create Catalog basics
        self.category = Category.objects.create(name='Science Fiction')
        self.author = Author.objects.create(full_name='Mary Shelley')
        self.book = Book.objects.create(
            title='Frankenstein Physical',
            isbn='978-0-123456-99-9',
            category=self.category,
            book_type='PHYSICAL'
        )
        self.book.authors.add(self.author)
        self.copy = BookCopy.objects.create(
            book=self.book, accession_number='CPY-ADV-001', status='AVAILABLE'
        )

    # -------------------------------------------------------------
    # 1. Open Source E-Book Ecosystem & Ingestion Tests
    # -------------------------------------------------------------
    def test_curated_classics_catalog(self):
        """Curated offline repository should contain at least 10 world-renowned classics."""
        service = OpenSourceEBookService()
        classics = service.get_curated_classics()
        self.assertGreaterEqual(len(classics), 10)
        titles = [c['title'] for c in classics]
        self.assertIn('Pride and Prejudice', titles)
        self.assertIn('Frankenstein; or, The Modern Prometheus', titles)


    def test_import_opensource_book(self):
        """Importing a curated classic creates Book, Author, Category, EBookMetadata, and saves file."""
        service = OpenSourceEBookService()
        classics = service.get_curated_classics()
        frankenstein = [c for c in classics if 'Frankenstein' in c['title']][0]
        
        imported_book, created = service.import_book_to_catalog(frankenstein, uploaded_by=self.librarian_user)
        self.assertIsNotNone(imported_book)
        self.assertEqual(imported_book.book_type, 'EBOOK')
        self.assertTrue(imported_book.has_ebook)
        
        metadata = imported_book.ebook_metadata
        self.assertEqual(metadata.format, 'HTML')
        self.assertEqual(metadata.rights_status, 'PUBLIC_DOMAIN')
        self.assertEqual(metadata.rental_price, Decimal('0.00'))
        self.assertEqual(metadata.access_mode, 'READ_AND_DOWNLOAD')
        self.assertTrue(metadata.is_active)

    def test_commons_page_loads(self):
        """Open-access digital commons catalog view should load cleanly."""
        response = self.client.get('/ebooks/commons/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Free Classic Books')

    def test_import_management_command(self):
        """Management command 'import_opensource_ebooks' runs cleanly."""
        call_command('import_opensource_ebooks', count=2)
        ebook_count = EBookMetadata.objects.filter(rights_status='PUBLIC_DOMAIN').count()
        self.assertGreaterEqual(ebook_count, 2)

    # -------------------------------------------------------------
    # 2. Community Reviews & Bookshelf Tests
    # -------------------------------------------------------------
    def test_submit_book_review_and_rating_aggregation(self):
        """Patrons can submit star reviews; average rating updates on the Book model."""
        self.client.login(username='member_test', password='password123')
        
        # Post review
        response = self.client.post(f'/catalog/book/{self.book.id}/review/', {
            'rating': '5',
            'headline': 'Masterpiece of gothic fiction',
            'review_text': 'One of the greatest books ever written.'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify BookReview object
        review = BookReview.objects.get(book=self.book, user=self.member_user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.headline, 'Masterpiece of gothic fiction')
        
        # Verify Book aggregation properties
        self.book.refresh_from_db()
        self.assertEqual(self.book.average_rating, 5.0)
        self.assertEqual(self.book.review_count, 1)

    def test_toggle_bookshelf_api(self):
        """Toggle bookshelf endpoint adds/removes books from patron's shelf."""
        self.client.login(username='member_test', password='password123')
        
        # Add to WANT_TO_READ
        response = self.client.post(
            '/catalog/api/bookshelf/toggle/',
            data=json.dumps({'book_id': self.book.id, 'shelf_type': 'WANT_TO_READ'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'added')
        self.assertTrue(UserBookList.objects.filter(user=self.member_user, book=self.book, shelf_type='WANT_TO_READ').exists())
        
        # Check personal bookshelf page
        shelf_res = self.client.get('/catalog/my-bookshelf/')
        self.assertEqual(shelf_res.status_code, 200)
        self.assertContains(shelf_res, self.book.title)

    # -------------------------------------------------------------
    # 3. Membership Tiers & Self-Service Renewal Tests
    # -------------------------------------------------------------
    def test_membership_tier_limits(self):
        """Student tier allows 3 books; Premium Scholar allows 10 books."""
        self.assertEqual(self.member_profile.max_books_allowed, 3)
        self.member_profile.tier = 'STANDARD'
        self.member_profile.save()
        self.assertEqual(self.member_profile.max_books_allowed, 5)
        self.member_profile.tier = 'PREMIUM_SCHOLAR'
        self.member_profile.save()
        self.assertEqual(self.member_profile.max_books_allowed, 10)

    def test_submit_and_approve_membership_request(self):
        """Member submits upgrade request; Librarian approves it at review desk."""
        self.client.login(username='member_test', password='password123')
        
        # Submit upgrade request
        response = self.client.post('/accounts/profile/submit-request/', {
            'request_type': 'UPGRADE_TIER',
            'requested_tier': 'PREMIUM_SCHOLAR',
            'reason': 'I am conducting comprehensive thesis research.'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        
        req = MembershipRequest.objects.get(user=self.member_user, request_type='UPGRADE_TIER')
        self.assertEqual(req.status, 'PENDING')
        self.assertEqual(req.requested_tier, 'PREMIUM_SCHOLAR')
        
        # Librarian approves request
        self.client.login(username='librarian_test', password='password123')
        approve_res = self.client.post('/accounts/members/requests/', {
            'request_id': req.id,
            'action': 'approve',
            'admin_notes': 'Granted for doctoral research'
        }, follow=True)
        self.assertEqual(approve_res.status_code, 200)
        
        req.refresh_from_db()
        self.assertEqual(req.status, 'APPROVED')
        self.member_profile.refresh_from_db()
        self.assertEqual(self.member_profile.tier, 'PREMIUM_SCHOLAR')
        self.assertEqual(self.member_profile.max_books_allowed, 10)

    # -------------------------------------------------------------
    # 4. Proactive Overdue Detection & Automated Reminders Tests
    # -------------------------------------------------------------
    def test_overdue_scanner_and_notification(self):
        """Overdue scanner flags overdue loan, calculates estimated fine, and creates alert notification."""
        # Create an overdue loan (due 5 days ago)
        loan = issue_book(self.member_profile, self.copy, self.librarian_user)
        loan.due_date = timezone.now().date() - timedelta(days=5)
        loan.save()
        
        # Run proactive scanner
        result = scan_and_notify_overdue_loans()
        self.assertGreaterEqual(result['overdue_count'], 1)
        self.assertEqual(result['total_estimated_fines'], Decimal('25.00')) # 5 days * 5.00
        
        # Verify in-app notification delivered
        notif = Notification.objects.filter(user=self.member_user, type='WARNING').first()
        self.assertIsNotNone(notif)
        self.assertIn('Overdue Book Alert', notif.title)
        self.assertIn('25.00', notif.message)

    def test_overdue_management_command(self):
        """Management command 'check_overdue_loans' executes cleanly."""
        call_command('check_overdue_loans')

    # -------------------------------------------------------------
    # 5. Activity Stream & Audit Log Tests
    # -------------------------------------------------------------
    def test_activity_logging_and_admin_feed(self):
        """System events are recorded in ActivityLog and render on the admin command center."""
        log_activity('LOAN_ISSUED', 'Test loan issued for Mary Shelley classic', user=self.librarian_user)
        log_activity('EBOOK_IMPORTED', 'Test open-source ingest', user=self.admin_user)
        
        self.assertEqual(ActivityLog.objects.count(), 2)
        
        # Admin dashboard renders activity feed
        self.client.login(username='admin_test', password='password123')
        dash_res = self.client.get('/dashboard/admin/')
        self.assertEqual(dash_res.status_code, 200)
        self.assertContains(dash_res, 'System Activity Stream & Audit Trail')
        self.assertContains(dash_res, 'Test loan issued for Mary Shelley classic')
