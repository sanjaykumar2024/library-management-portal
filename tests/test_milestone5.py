from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from catalog.models import Category, Author, Book, BookCopy, EBookMetadata
from circulation.models import Loan, Fine
from reservations.models import Reservation
from ebooks.models import EBookAccessLog


class Milestone5DashboardAndReportTests(TestCase):
    def setUp(self):
        # 1. Create Admin User
        self.admin_user = User.objects.create_user(
            username='admin_test', password='password123', email='admin@test.com'
        )
        self.admin_profile = self.admin_user.profile
        self.admin_profile.role = 'ADMIN'
        self.admin_profile.save()

        # 2. Create Librarian User
        self.librarian_user = User.objects.create_user(
            username='lib_test', password='password123', email='lib@test.com'
        )
        self.librarian_profile = self.librarian_user.profile
        self.librarian_profile.role = 'LIBRARIAN'
        self.librarian_profile.save()

        # 3. Create Member Users
        self.member1_user = User.objects.create_user(
            username='member1_test', password='password123', email='member1@test.com'
        )
        self.member1_profile = self.member1_user.profile
        self.member1_profile.role = 'MEMBER'
        self.member1_profile.membership_status = 'ACTIVE'
        self.member1_profile.phone_number = '555-0101'
        self.member1_profile.save()

        self.member2_user = User.objects.create_user(
            username='member2_test', password='password123', email='member2@test.com'
        )
        self.member2_profile = self.member2_user.profile
        self.member2_profile.role = 'MEMBER'
        self.member2_profile.membership_status = 'EXPIRED'
        self.member2_profile.save()

        # 4. Create Catalogue & Copies
        self.category = Category.objects.create(name='Science')
        self.author = Author.objects.create(full_name='Carl Sagan')
        self.book = Book.objects.create(
            title='Cosmos', isbn='9780394502946', category=self.category, book_type='BOTH'
        )
        self.book.authors.add(self.author)

        self.copy1 = BookCopy.objects.create(
            book=self.book, accession_number='ACC-M5-001', status='ISSUED'
        )
        self.copy2 = BookCopy.objects.create(
            book=self.book, accession_number='ACC-M5-002', status='AVAILABLE'
        )

        self.ebook = EBookMetadata.objects.create(
            book=self.book, format='PDF', access_mode='READ_ONLY', rights_status='PUBLIC_DOMAIN', is_active=True
        )

        # 5. Create Loan, Fine, Reservation, EBookAccessLog
        self.today = timezone.now().date()
        self.loan = Loan.objects.create(
            member=self.member1_profile,
            book_copy=self.copy1,
            issue_date=self.today,
            due_date=self.today - timezone.timedelta(days=3),
            status='ISSUED'
        )

        self.fine = Fine.objects.create(
            loan=self.loan,
            amount=Decimal('15.00'),
            overdue_days=3,
            status='PENDING'
        )

        self.reservation = Reservation.objects.create(
            member=self.member1_profile,
            book=self.book,
            status='PENDING'
        )

        self.access_log = EBookAccessLog.objects.create(
            user=self.member1_user,
            ebook=self.ebook,
            action='READ'
        )

        self.client = Client()

    def test_dashboard_counts_admin(self):
        """Admin dashboard displays accurate real database metrics."""
        self.client.login(username='admin_test', password='password123')
        response = self.client.get(reverse('core:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_members'], 2)
        self.assertEqual(response.context['total_librarians'], 1)
        self.assertEqual(response.context['total_titles'], 1)
        self.assertEqual(response.context['total_physical_copies'], 2)
        self.assertEqual(response.context['total_ebooks'], 1)
        self.assertEqual(response.context['overdue_loans'], 1)

    def test_dashboard_counts_librarian(self):
        """Librarian dashboard displays accurate circulation numbers."""
        self.client.login(username='lib_test', password='password123')
        response = self.client.get(reverse('core:librarian_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['issued_today_count'], 1)
        self.assertEqual(response.context['active_loans_count'], 1)
        self.assertEqual(response.context['overdue_loans_count'], 1)
        self.assertEqual(response.context['available_copies'], 1)

    def test_dashboard_member_isolation(self):
        """Member dashboard shows personal activity only."""
        self.client.login(username='member1_test', password='password123')
        response = self.client.get(reverse('core:member_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_overdue'])
        self.assertEqual(len(response.context['my_active_loans']), 1)
        self.assertEqual(len(response.context['my_active_reservations']), 1)

    def test_report_access_restriction(self):
        """Ordinary member cannot access report pages or CSV downloads."""
        self.client.login(username='member1_test', password='password123')

        # Index report page
        response = self.client.get(reverse('reports:index'))
        self.assertEqual(response.status_code, 302)

        # Membership CSV export
        response = self.client.get(reverse('reports:membership_csv'))
        self.assertEqual(response.status_code, 302)

        # Overdue CSV export
        response = self.client.get(reverse('reports:overdue_csv'))
        self.assertEqual(response.status_code, 302)

    def test_librarian_can_access_reports_and_csv(self):
        """Librarian user can view reports and download CSV files."""
        self.client.login(username='lib_test', password='password123')

        # View report index
        response = self.client.get(reverse('reports:index'))
        self.assertEqual(response.status_code, 200)

        # View membership report
        response = self.client.get(reverse('reports:membership'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'member1_test')

        # Download membership CSV
        csv_response = self.client.get(reverse('reports:membership_csv'))
        self.assertEqual(csv_response.status_code, 200)
        self.assertEqual(csv_response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="membership_report.csv"', csv_response['Content-Disposition'])
        content = csv_response.content.decode('utf-8')
        self.assertIn('member1_test', content)
        self.assertIn('555-0101', content)

    def test_report_filtering_and_csv(self):
        """Report filtering works correctly and CSV export respects current filters."""
        self.client.login(username='admin_test', password='password123')

        # Filter membership by active status
        response = self.client.get(reverse('reports:membership'), {'status': 'ACTIVE'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'member1_test')
        self.assertNotContains(response, 'member2_test')

        # CSV export with filter
        csv_response = self.client.get(reverse('reports:membership_csv'), {'status': 'ACTIVE'})
        self.assertEqual(csv_response.status_code, 200)
        content = csv_response.content.decode('utf-8')
        self.assertIn('member1_test', content)
        self.assertNotIn('member2_test', content)

    def test_csv_exports_all_types(self):
        """Verify all CSV export endpoints function properly for librarians."""
        self.client.login(username='lib_test', password='password123')

        csv_endpoints = [
            'reports:membership_csv',
            'reports:inventory_csv',
            'reports:loans_csv',
            'reports:overdue_csv',
            'reports:fines_csv',
            'reports:reservations_csv',
            'reports:ebook_usage_csv',
        ]

        for ep in csv_endpoints:
            response = self.client.get(reverse(ep))
            self.assertEqual(response.status_code, 200, f"Failed on endpoint: {ep}")
            self.assertEqual(response['Content-Type'], 'text/csv')
            self.assertTrue('attachment;' in response['Content-Disposition'])
