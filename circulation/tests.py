import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounts.models import UserProfile
from catalog.models import Book, BookCopy, Category
from circulation.models import Loan


class KioskSelfCheckoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Technology')
        self.user = User.objects.create_user(username='member_test', password='password123')
        self.profile = self.user.profile
        self.profile.membership_number = 'LIB-TEST-001'
        self.profile.membership_status = 'ACTIVE'
        self.profile.is_approved = True
        self.profile.tier = 'STUDENT'
        self.profile.save()
        self.book = Book.objects.create(
            title='The Phoenix Project',
            isbn='9780988262591',
            category=self.category,
            book_type='PHYSICAL'
        )
        self.copy = BookCopy.objects.create(
            book=self.book,
            accession_number='LIB-1006',
            status='AVAILABLE',
            condition='GOOD'
        )

    def test_kiosk_page_renders_cleanly(self):
        resp = self.client.get('/circulation/kiosk/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Quick Self-Checkout Station')
        self.assertContains(resp, 'id="scannedCartCard"')
        self.assertContains(resp, 'id="receiptSummaryCard"')
        self.assertContains(resp, 'id="btnCheckout"')

    def test_kiosk_lookup_member(self):
        resp = self.client.get('/circulation/api/kiosk/lookup-member/?q=LIB-TEST-001')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['member']['username'], 'member_test')
        self.assertEqual(data['member']['membership_number'], 'LIB-TEST-001')

    def test_kiosk_lookup_book(self):
        resp = self.client.get('/circulation/api/kiosk/lookup-book/?barcode=LIB-1006')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['copy']['accession_number'], 'LIB-1006')
        self.assertTrue(data['copy']['is_available'])

    def test_kiosk_checkout_success(self):
        self.client.force_login(self.user)
        payload = {
            'membership_number': 'LIB-TEST-001',
            'accession_numbers': ['LIB-1006']
        }
        resp = self.client.post(
            '/circulation/api/kiosk/checkout/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['loans']), 1)
        self.assertEqual(data['loans'][0]['accession_number'], 'LIB-1006')

        # Verify database state
        self.copy.refresh_from_db()
        self.assertEqual(self.copy.status, 'ISSUED')
        self.assertTrue(Loan.objects.filter(member=self.profile, book_copy=self.copy, status='ISSUED').exists())

    def test_kiosk_checkout_cross_user_station_mode(self):
        """Kiosk station allows checkout for verified scanned card even if browser session differs."""
        other_user = User.objects.create_user(username='other_patron', password='password123')
        self.client.force_login(other_user)

        copy2 = BookCopy.objects.create(
            book=self.book,
            accession_number='LIB-1007',
            status='AVAILABLE',
            condition='GOOD'
        )
        payload = {
            'membership_number': 'LIB-TEST-001',
            'accession_numbers': ['LIB-1007']
        }
        resp = self.client.post(
            '/circulation/api/kiosk/checkout/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        copy2.refresh_from_db()
        self.assertEqual(copy2.status, 'ISSUED')
        self.assertTrue(Loan.objects.filter(member=self.profile, book_copy=copy2, status='ISSUED').exists())

    def test_kiosk_checkout_anonymous_walkup_csrf_exempt(self):
        """Anonymous walk-up kiosk patron checkout succeeds without session login or CSRF error."""
        anon_client = Client(enforce_csrf_checks=True)
        copy3 = BookCopy.objects.create(
            book=self.book,
            accession_number='LIB-1008',
            status='AVAILABLE',
            condition='GOOD'
        )
        payload = {
            'membership_number': 'LIB-TEST-001',
            'accession_numbers': ['LIB-1008']
        }
        resp = anon_client.post(
            '/circulation/api/kiosk/checkout/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        copy3.refresh_from_db()
        self.assertEqual(copy3.status, 'ISSUED')


