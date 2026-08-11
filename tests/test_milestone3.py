from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import datetime

from accounts.models import UserProfile
from catalog.models import Category, Author, Book, BookCopy
from circulation.models import Loan, Fine
from circulation import services as circ_services
from reservations.models import Reservation
from reservations import services as res_services
from notifications.models import Notification
from notifications import services as notif_services


class BaseTestCase(TestCase):
    """Shared test fixture for all Milestone 3 tests."""
    
    def setUp(self):
        # Create a librarian
        self.librarian_user = User.objects.create_user(
            username='librarian1', password='testpass123',
            first_name='Jane', last_name='Doe', email='jane@lib.org'
        )
        self.librarian_profile = self.librarian_user.profile
        self.librarian_profile.role = 'LIBRARIAN'
        self.librarian_profile.save()
        
        # Create a regular member
        self.member_user = User.objects.create_user(
            username='member1', password='testpass123',
            first_name='Alice', last_name='Smith', email='alice@test.com'
        )
        self.member_profile = self.member_user.profile
        self.member_profile.membership_status = 'ACTIVE'
        self.member_profile.save()
        
        # Create a second member
        self.member_user2 = User.objects.create_user(
            username='member2', password='testpass123',
            first_name='Bob', last_name='Jones', email='bob@test.com'
        )
        self.member_profile2 = self.member_user2.profile
        self.member_profile2.membership_status = 'ACTIVE'
        self.member_profile2.save()
        
        # Create catalog objects
        self.category = Category.objects.create(name='Fiction')
        self.author = Author.objects.create(full_name='Test Author')
        self.book = Book.objects.create(
            title='Test Book', isbn='978-0-123456-47-2',
            category=self.category, book_type='PHYSICAL',
            description='A test book.'
        )
        self.book.authors.add(self.author)
        
        self.copy1 = BookCopy.objects.create(
            book=self.book, accession_number='BOK-0001', status='AVAILABLE'
        )
        self.copy2 = BookCopy.objects.create(
            book=self.book, accession_number='BOK-0002', status='AVAILABLE'
        )


class CirculationServiceTests(BaseTestCase):
    """Tests for the circulation (issue / return / renew) services."""
    
    def test_issue_book_success(self):
        loan = circ_services.issue_book(self.member_profile, self.copy1, self.librarian_user)
        self.assertEqual(loan.status, 'ISSUED')
        self.copy1.refresh_from_db()
        self.assertEqual(self.copy1.status, 'ISSUED')
    
    def test_issue_book_inactive_member(self):
        self.member_profile.membership_status = 'EXPIRED'
        self.member_profile.save()
        with self.assertRaises(ValueError):
            circ_services.issue_book(self.member_profile, self.copy1, self.librarian_user)
    
    def test_issue_book_unavailable_copy(self):
        self.copy1.status = 'ISSUED'
        self.copy1.save()
        with self.assertRaises(ValueError):
            circ_services.issue_book(self.member_profile, self.copy1, self.librarian_user)
    
    def test_issue_book_exceeds_limit(self):
        # Create 3 loans (the max)
        for i in range(3):
            c = BookCopy.objects.create(
                book=self.book, accession_number=f'BOK-EXTRA-{i}', status='AVAILABLE'
            )
            circ_services.issue_book(self.member_profile, c, self.librarian_user)
        
        with self.assertRaises(ValueError):
            circ_services.issue_book(self.member_profile, self.copy2, self.librarian_user)
    
    def test_return_book_success(self):
        loan = circ_services.issue_book(self.member_profile, self.copy1, self.librarian_user)
        circ_services.return_book(loan, self.librarian_user)
        loan.refresh_from_db()
        self.assertEqual(loan.status, 'RETURNED')
        self.assertIsNotNone(loan.return_date)
        self.copy1.refresh_from_db()
        self.assertEqual(self.copy1.status, 'AVAILABLE')
    
    def test_return_book_already_returned(self):
        loan = circ_services.issue_book(self.member_profile, self.copy1, self.librarian_user)
        circ_services.return_book(loan, self.librarian_user)
        with self.assertRaises(ValueError):
            circ_services.return_book(loan, self.librarian_user)
    
    def test_return_overdue_generates_fine(self):
        loan = circ_services.issue_book(self.member_profile, self.copy1, self.librarian_user)
        # Backdate the due date to make it overdue
        loan.due_date = timezone.now().date() - datetime.timedelta(days=5)
        loan.save()
        circ_services.return_book(loan, self.librarian_user)
        loan.refresh_from_db()
        self.assertTrue(hasattr(loan, 'fine'))
        self.assertEqual(loan.fine.overdue_days, 5)
        self.assertEqual(loan.fine.amount, Decimal('25.00'))  # 5 days * $5
    
    def test_renew_book_success(self):
        loan = circ_services.issue_book(self.member_profile, self.copy1, self.librarian_user)
        old_due = loan.due_date
        circ_services.renew_book(loan)
        loan.refresh_from_db()
        self.assertEqual(loan.renewal_count, 1)
        self.assertEqual(loan.due_date, old_due + datetime.timedelta(days=14))
    
    def test_renew_book_max_renewals(self):
        loan = circ_services.issue_book(self.member_profile, self.copy1, self.librarian_user)
        circ_services.renew_book(loan)
        circ_services.renew_book(loan)
        with self.assertRaises(ValueError):
            circ_services.renew_book(loan)
    
    def test_renew_blocked_by_reservation(self):
        loan = circ_services.issue_book(self.member_profile, self.copy1, self.librarian_user)
        # Another member creates a reservation (all copies issued, so stays PENDING)
        self.copy2.status = 'ISSUED'
        self.copy2.save()
        Reservation.objects.create(
            member=self.member_profile2, book=self.book, status='PENDING'
        )
        with self.assertRaises(ValueError):
            circ_services.renew_book(loan)


class ReservationServiceTests(BaseTestCase):
    """Tests for the reservation queue services."""
    
    def test_create_reservation_pending(self):
        # Make both copies unavailable
        self.copy1.status = 'ISSUED'
        self.copy1.save()
        self.copy2.status = 'ISSUED'
        self.copy2.save()
        
        res = res_services.create_reservation(self.member_profile, self.book)
        self.assertEqual(res.status, 'PENDING')
    
    def test_create_reservation_instant_allocate(self):
        # copy1 is AVAILABLE, so reservation should be allocated immediately
        self.copy2.status = 'ISSUED'
        self.copy2.save()
        
        res = res_services.create_reservation(self.member_profile, self.book)
        res.refresh_from_db()
        # Should be ALLOCATED since copy1 is available
        self.assertEqual(res.status, 'ALLOCATED')
        self.copy1.refresh_from_db()
        self.assertEqual(self.copy1.status, 'RESERVED')
    
    def test_duplicate_reservation_blocked(self):
        self.copy1.status = 'ISSUED'
        self.copy1.save()
        self.copy2.status = 'ISSUED'
        self.copy2.save()
        res_services.create_reservation(self.member_profile, self.book)
        with self.assertRaises(ValueError):
            res_services.create_reservation(self.member_profile, self.book)
    
    def test_reservation_inactive_member(self):
        self.member_profile.membership_status = 'SUSPENDED'
        self.member_profile.save()
        with self.assertRaises(ValueError):
            res_services.create_reservation(self.member_profile, self.book)
    
    def test_cancel_reservation(self):
        self.copy1.status = 'ISSUED'
        self.copy1.save()
        self.copy2.status = 'ISSUED'
        self.copy2.save()
        res = res_services.create_reservation(self.member_profile, self.book)
        res_services.cancel_reservation(res, self.member_user)
        res.refresh_from_db()
        self.assertEqual(res.status, 'CANCELLED')
    
    def test_expire_reservations(self):
        self.copy2.status = 'ISSUED'
        self.copy2.save()
        res = res_services.create_reservation(self.member_profile, self.book)
        res.refresh_from_db()
        # Backdate expiry
        res.expiry_date = timezone.now() - datetime.timedelta(days=1)
        res.save()
        count = res_services.expire_reservations()
        self.assertEqual(count, 1)
        res.refresh_from_db()
        self.assertEqual(res.status, 'EXPIRED')
    
    def test_return_triggers_allocation(self):
        # Issue copy1 to member1
        loan = circ_services.issue_book(self.member_profile, self.copy1, self.librarian_user)
        self.copy2.status = 'ISSUED'
        self.copy2.save()
        
        # Member2 creates a reservation (all copies issued, stays PENDING)
        res = Reservation.objects.create(
            member=self.member_profile2, book=self.book, status='PENDING'
        )
        
        # Return copy1 -> should allocate to member2's reservation
        circ_services.return_book(loan, self.librarian_user)
        res.refresh_from_db()
        self.assertEqual(res.status, 'ALLOCATED')
        self.assertEqual(res.allocated_copy, self.copy1)


class NotificationServiceTests(BaseTestCase):
    """Tests for the notification service."""
    
    def test_create_notification(self):
        notif = notif_services.create_notification(
            user=self.member_user, title='Test', message='Hello', type='INFO'
        )
        self.assertFalse(notif.is_read)
        self.assertEqual(Notification.objects.filter(user=self.member_user).count(), 1)
    
    def test_mark_as_read(self):
        notif = notif_services.create_notification(
            user=self.member_user, title='Test', message='Hello'
        )
        notif_services.mark_as_read(notif.id, self.member_user)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
    
    def test_mark_all_as_read(self):
        for i in range(3):
            notif_services.create_notification(
                user=self.member_user, title=f'Test {i}', message='Hello'
            )
        notif_services.mark_all_as_read(self.member_user)
        self.assertEqual(
            Notification.objects.filter(user=self.member_user, is_read=False).count(), 0
        )
    
    def test_allocation_creates_notification(self):
        """When a returned book is allocated to a waiting member, a notification should be created."""
        loan = circ_services.issue_book(self.member_profile, self.copy1, self.librarian_user)
        self.copy2.status = 'ISSUED'
        self.copy2.save()
        
        Reservation.objects.create(
            member=self.member_profile2, book=self.book, status='PENDING'
        )
        
        circ_services.return_book(loan, self.librarian_user)
        self.assertTrue(
            Notification.objects.filter(
                user=self.member_user2, title='Reservation Available'
            ).exists()
        )


class MembershipTests(BaseTestCase):
    """Tests for membership profile auto-generation."""
    
    def test_membership_number_generated(self):
        self.assertIsNotNone(self.member_profile.membership_number)
        self.assertTrue(self.member_profile.membership_number.startswith('LIB-'))
    
    def test_membership_expiry_date_generated(self):
        self.assertIsNotNone(self.member_profile.membership_expiry_date)
    
    def test_default_status_is_active(self):
        new_user = User.objects.create_user(username='newmember', password='testpass123')
        self.assertEqual(new_user.profile.membership_status, 'ACTIVE')
