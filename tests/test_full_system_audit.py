from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse

from accounts.models import UserProfile
from catalog.models import Book, BookCopy, Category, Author
from reservations.models import Reservation
from reservations.services import can_member_reserve, create_reservation
from core.models import ActivityLog
from core.views import custom_404_view, custom_403_view, custom_500_view


class FullSystemAuditIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        # Admin
        self.admin_user = User.objects.create_superuser(
            username='audit_admin', password='password123', email='admin@audit.com'
        )
        self.admin_profile = self.admin_user.profile
        self.admin_profile.role = 'ADMIN'
        self.admin_profile.save()

        # Librarian
        self.librarian_user = User.objects.create_user(
            username='audit_librarian', password='password123', email='lib@audit.com'
        )
        self.librarian_profile = self.librarian_user.profile
        self.librarian_profile.role = 'LIBRARIAN'
        self.librarian_profile.save()

        # Member (Student tier)
        self.member_user = User.objects.create_user(
            username='audit_member', password='password123', email='member@audit.com'
        )
        self.member_profile = self.member_user.profile
        self.member_profile.role = 'MEMBER'
        self.member_profile.membership_status = 'ACTIVE'
        self.member_profile.tier = 'STUDENT'
        self.member_profile.save()

        # Catalog setup
        self.category = Category.objects.create(name='Classics')
        self.author = Author.objects.create(full_name='Jane Austen')
        self.book = Book.objects.create(
            title='Pride and Prejudice',
            isbn='9780141439518',
            category=self.category,
            book_type='PHYSICAL',
            description='A classic romance novel.'
        )
        self.book.authors.add(self.author)
        self.copy = BookCopy.objects.create(
            book=self.book,
            accession_number='LIB-AUD-001',
            shelf_location='Shelf A-1',
            status='AVAILABLE'
        )
        from catalog.models import EBookMetadata
        self.ebook = EBookMetadata.objects.create(
            book=self.book,
            page_count=350,
            format='HTML',
            rights_status='PUBLIC_DOMAIN',
            is_active=True
        )

    # ── Component 2: Catalog Management ───────────────────────────────────────

    def test_librarian_can_create_book(self):
        self.client.force_login(self.librarian_user)
        response = self.client.post(reverse('catalog:book_create'), {
            'title': 'Sense and Sensibility',
            'isbn': '9780141439662',
            'category': self.category.id,
            'author_names': 'Jane Austen, Anonymous Editor',
            'publisher': 'Penguin Classics',
            'publication_year': 1811,
            'language': 'English',
            'description': 'A novel by Jane Austen.',
            'book_type': 'PHYSICAL',
            'is_active': True,
        })
        self.assertEqual(response.status_code, 302)
        book = Book.objects.get(isbn='9780141439662')
        self.assertEqual(book.title, 'Sense and Sensibility')
        self.assertEqual(book.authors.count(), 2)
        # Check activity log emitted
        self.assertTrue(
            ActivityLog.objects.filter(action='BOOK_ADDED', user=self.librarian_user).exists()
        )

    def test_librarian_can_edit_book(self):
        self.client.force_login(self.librarian_user)
        response = self.client.post(reverse('catalog:book_edit', kwargs={'book_id': self.book.id}), {
            'title': 'Pride and Prejudice (Deluxe Edition)',
            'isbn': self.book.isbn,
            'category': self.category.id,
            'author_names': 'Jane Austen',
            'publisher': 'Penguin Deluxe',
            'publication_year': 1813,
            'language': 'English',
            'description': 'Updated description.',
            'book_type': 'PHYSICAL',
            'is_active': True,
        })
        self.assertEqual(response.status_code, 302)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Pride and Prejudice (Deluxe Edition)')
        self.assertTrue(
            ActivityLog.objects.filter(action='BOOK_EDITED', user=self.librarian_user).exists()
        )

    def test_librarian_can_add_book_copy(self):
        self.client.force_login(self.librarian_user)
        response = self.client.post(reverse('catalog:add_book_copy', kwargs={'book_id': self.book.id}), {
            'accession_number': 'LIB-AUD-002',
            'shelf_location=': 'Shelf A-2',
            'shelf_location': 'Shelf A-2',
            'condition': 'Brand New',
            'status': 'AVAILABLE',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BookCopy.objects.filter(accession_number='LIB-AUD-002').exists())
        self.assertTrue(
            ActivityLog.objects.filter(action='COPY_ADDED', user=self.librarian_user).exists()
        )

    def test_non_librarian_blocked_from_catalog_management(self):
        self.client.force_login(self.member_user)
        # Try book create
        resp_create = self.client.get(reverse('catalog:book_create'))
        self.assertEqual(resp_create.status_code, 302)
        # Try book edit
        resp_edit = self.client.get(reverse('catalog:book_edit', kwargs={'book_id': self.book.id}))
        self.assertEqual(resp_edit.status_code, 302)
        # Try add copy
        resp_copy = self.client.get(reverse('catalog:add_book_copy', kwargs={'book_id': self.book.id}))
        self.assertEqual(resp_copy.status_code, 302)

    # ── Component 3: Reservation UniqueConstraint & Premium Holds ─────────────

    def test_reservation_unique_active_constraint(self):
        # First active reservation
        Reservation.objects.create(
            member=self.member_profile,
            book=self.book,
            status='PENDING'
        )
        # Attempting second active reservation should violate database UniqueConstraint
        with self.assertRaises(IntegrityError):
            Reservation.objects.create(
                member=self.member_profile,
                book=self.book,
                status='PENDING'
            )

    def test_premium_scholar_unlimited_reservations(self):
        self.member_profile.tier = 'PREMIUM_SCHOLAR'
        self.member_profile.save()

        # Create 2 distinct books
        b2 = Book.objects.create(title='Book Two', isbn='9781111111111', category=self.category, description='Two')
        b3 = Book.objects.create(title='Book Three', isbn='9782222222222', category=self.category, description='Three')

        # Create 2 reservations (standard limit is 2)
        Reservation.objects.create(member=self.member_profile, book=self.book, status='PENDING')
        Reservation.objects.create(member=self.member_profile, book=b2, status='PENDING')

        # Premium scholar can reserve a 3rd book
        can_res, reason = can_member_reserve(self.member_profile)
        self.assertTrue(can_res)
        self.assertEqual(reason, "")

        res3 = create_reservation(self.member_profile, b3)
        self.assertIsNotNone(res3)
        self.assertEqual(res3.book, b3)

    # ── Component 4: Member Contact Self-Service ──────────────────────────────

    def test_member_can_update_contact_info(self):
        self.client.force_login(self.member_user)
        response = self.client.post(reverse('accounts:update_contact'), {
            'first_name': 'Audited',
            'last_name': 'Patron',
            'phone_number': '+91 99999 88888',
            'address': '221B Baker Street, London',
        })
        self.assertEqual(response.status_code, 302)
        self.member_user.refresh_from_db()
        self.member_profile.refresh_from_db()
        self.assertEqual(self.member_user.first_name, 'Audited')
        self.assertEqual(self.member_user.last_name, 'Patron')
        self.assertEqual(self.member_profile.phone_number, '+91 99999 88888')
        self.assertEqual(self.member_profile.address, '221B Baker Street, London')
        self.assertTrue(
            ActivityLog.objects.filter(action='PROFILE_UPDATED', user=self.member_user).exists()
        )

    # ── Component 5: Custom Error Handlers ────────────────────────────────────

    def test_custom_404_view(self):
        from django.contrib.auth.models import AnonymousUser
        req = self.factory.get('/nonexistent-page-url/')
        req.user = AnonymousUser()
        response = custom_404_view(req, exception=Exception("Page not found"))
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404', response.content)

    def test_custom_403_view(self):
        from django.contrib.auth.models import AnonymousUser
        req = self.factory.get('/forbidden/')
        req.user = AnonymousUser()
        response = custom_403_view(req, exception=Exception("Permission denied"))
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'403', response.content)

    def test_custom_500_view(self):
        from django.contrib.auth.models import AnonymousUser
        req = self.factory.get('/error/')
        req.user = AnonymousUser()
        response = custom_500_view(req)
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'500', response.content)
        self.assertIn(b'Server Error', response.content)

    # ── Component 5: Registration & Renewal Activity Logging ──────────────────

    def test_registration_and_renewal_emit_activity_logs(self):
        # Registration
        resp = self.client.post(reverse('accounts:register'), {
            'username': 'new_patron',
            'first_name': 'New',
            'last_name': 'Patron',
            'email': 'patron@audit.com',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
        })
        self.assertEqual(resp.status_code, 302)
        new_user = User.objects.get(username='new_patron')
        self.assertTrue(
            ActivityLog.objects.filter(action='MEMBER_REGISTERED', user=new_user).exists()
        )

        # Self-service renewal
        self.client.force_login(new_user)
        renew_resp = self.client.post(reverse('accounts:request_renewal'))
        self.assertEqual(renew_resp.status_code, 302)
        self.assertTrue(
            ActivityLog.objects.filter(action='MEMBERSHIP_RENEWED', user=new_user).exists()
        )

    # ── Pillar 2: Kiosk & Barcode Integration Tests ───────────────────────────

    def test_kiosk_view_renders(self):
        self.client.force_login(self.librarian_user)
        response = self.client.get(reverse('circulation:kiosk'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Quick Self-Checkout Station', response.content)

    def test_api_kiosk_lookup_member(self):
        self.client.force_login(self.librarian_user)
        response = self.client.get(
            reverse('circulation:api_kiosk_lookup_member') + f'?q={self.member_profile.membership_number}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['member']['membership_number'], self.member_profile.membership_number)
        self.assertTrue(data['member']['can_borrow'])

    def test_api_kiosk_lookup_book(self):
        self.client.force_login(self.librarian_user)
        response = self.client.get(
            reverse('circulation:api_kiosk_lookup_book') + f'?barcode={self.copy.accession_number}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['copy']['accession_number'], self.copy.accession_number)
        self.assertTrue(data['copy']['is_available'])

    def test_api_kiosk_checkout_flow(self):
        self.client.force_login(self.member_user)
        import json
        payload = {
            'membership_number': self.member_profile.membership_number,
            'accession_numbers': [self.copy.accession_number],
        }
        response = self.client.post(
            reverse('circulation:api_kiosk_checkout'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['loans']), 1)

        # Verify copy is marked ISSUED
        self.copy.refresh_from_db()
        self.assertEqual(self.copy.status, 'ISSUED')

        # Verify activity log
        self.assertTrue(
            ActivityLog.objects.filter(action='LOAN_ISSUED', user=self.member_user).exists()
        )

    # ── Pillar 3: E-Reader Highlights & Annotation Tests ──────────────────────

    def test_add_and_list_and_delete_annotation(self):
        self.client.force_login(self.member_user)
        import json

        # 1. Add annotation
        payload = {
            'selected_text': 'It is a truth universally acknowledged...',
            'note': 'Iconic opening line of English literature.',
            'color': 'yellow',
            'chapter_title': 'Chapter 1'
        }
        resp = self.client.post(
            reverse('ebooks:api_add_annotation', kwargs={'ebook_id': self.ebook.id}),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])
        annotation_id = data['annotation']['id']

        # 2. List annotations
        list_resp = self.client.get(
            reverse('ebooks:api_list_annotations', kwargs={'ebook_id': self.ebook.id})
        )
        self.assertEqual(list_resp.status_code, 200)
        list_data = list_resp.json()
        self.assertTrue(list_data['success'])
        self.assertEqual(len(list_data['annotations']), 1)
        self.assertEqual(list_data['annotations'][0]['color'], 'yellow')

        # 3. Delete annotation
        del_resp = self.client.post(
            reverse('ebooks:api_delete_annotation', kwargs={'annotation_id': annotation_id})
        )
        self.assertEqual(del_resp.status_code, 200)
        self.assertTrue(del_resp.json()['success'])

        # Verify 0 annotations remain
        list_resp2 = self.client.get(
            reverse('ebooks:api_list_annotations', kwargs={'ebook_id': self.ebook.id})
        )
        self.assertEqual(len(list_resp2.json()['annotations']), 0)

    # ── Pillar 5: Gamification & Reading Challenge Tests ──────────────────────

    def test_reading_challenge_progress_calculation(self):
        from catalog.models import ReadingChallenge, UserBookList
        challenge = ReadingChallenge.objects.create(
            user=self.member_user, year=2026, target_books=4
        )
        self.assertEqual(challenge.completed_count, 0)
        self.assertEqual(challenge.progress_pct, 0)

        # Mark book completed on patron's bookshelf
        UserBookList.objects.create(
            user=self.member_user, book=self.book, shelf_type='COMPLETED'
        )
        self.assertEqual(challenge.completed_count, 1)
        self.assertEqual(challenge.progress_pct, 25)

    def test_award_badge_and_notification(self):
        from catalog.models import PatronBadge, award_badge
        badge, created = award_badge(self.member_user, 'FIRST_BORROW')
        self.assertTrue(created)
        self.assertEqual(badge.badge_type, 'FIRST_BORROW')
        self.assertEqual(badge.title, 'First Checkout')

        # Check duplicate award is idempotent
        badge2, created2 = award_badge(self.member_user, 'FIRST_BORROW')
        self.assertFalse(created2)
        self.assertEqual(self.member_user.badges.count(), 1)

    def test_member_dashboard_renders_gamification(self):
        self.client.force_login(self.member_user)
        response = self.client.get(reverse('core:member_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Reading Challenge', response.content)
        self.assertIn(b'My Badges', response.content)

    # ── Pillar 6: PWA & Offline Support Tests ─────────────────────────────────

    def test_pwa_manifest_and_sw_exist(self):
        import os
        import json
        manifest_path = os.path.join('static', 'manifest.json')
        sw_path = os.path.join('static', 'js', 'sw.js')

        self.assertTrue(os.path.exists(manifest_path))
        self.assertTrue(os.path.exists(sw_path))

        with open(manifest_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['short_name'], 'LibrarySphere')
            self.assertEqual(data['display'], 'standalone')

    def test_member_can_pay_own_fine_online_and_view_receipt(self):
        """Verify members can access fine pay view for their own fine, pay online, and view receipt."""
        from circulation.models import Loan, Fine
        from django.utils import timezone
        import datetime

        loan = Loan.objects.create(
            member=self.member_profile,
            book_copy=self.copy,
            issued_by=self.librarian_user,
            issue_date=timezone.now().date() - datetime.timedelta(days=20),
            due_date=timezone.now().date() - datetime.timedelta(days=6),
            status='RETURNED',
            return_date=timezone.now().date(),
            returned_to=self.librarian_user
        )
        fine = Fine.objects.create(
            loan=loan,
            amount=30.00,
            overdue_days=6,
            status='PENDING'
        )

        # 1. Member can view the pay fine page (HTTP 200, not 403 or redirect to login)
        self.client.force_login(self.member_user)
        response = self.client.get(reverse('circulation:pay_fine', args=[fine.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pay Overdue Fine', response.content)

        # 2. Member can submit online payment
        post_response = self.client.post(
            reverse('circulation:pay_fine', args=[fine.id]),
            {'payment_method': 'UPI', 'notes': 'UPI Ref #123456'}
        )
        self.assertRedirects(post_response, reverse('accounts:profile'))

        fine.refresh_from_db()
        self.assertEqual(fine.status, 'PAID')
        self.assertIn('UPI', fine.notes)

        # 3. Member can view and print their official fine receipt
        receipt_response = self.client.get(reverse('circulation:fine_receipt', args=[fine.id]))
        self.assertEqual(receipt_response.status_code, 200)
        self.assertIn(b'Official Fine Payment Receipt', receipt_response.content)

    def test_unauthorized_member_cannot_pay_another_members_fine(self):
        """Verify members cannot view or pay another member's fine."""
        from circulation.models import Loan, Fine
        from django.utils import timezone
        import datetime

        other_user = User.objects.create_user(username='other_patron', password='password123')
        other_profile = other_user.profile
        other_profile.role = 'MEMBER'
        other_profile.membership_status = 'ACTIVE'
        other_profile.save()

        loan = Loan.objects.create(
            member=other_profile,
            book_copy=self.copy,
            issued_by=self.librarian_user,
            issue_date=timezone.now().date() - datetime.timedelta(days=20),
            due_date=timezone.now().date() - datetime.timedelta(days=6),
            status='RETURNED',
            return_date=timezone.now().date()
        )
        fine = Fine.objects.create(
            loan=loan,
            amount=25.00,
            overdue_days=5,
            status='PENDING'
        )

        # Log in as self.member_user and try to view or pay other_user's fine
        self.client.force_login(self.member_user)
        response = self.client.get(reverse('circulation:pay_fine', args=[fine.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('core:dashboard'), response.url)

        post_response = self.client.post(reverse('circulation:pay_fine', args=[fine.id]), {'payment_method': 'UPI'})
        self.assertEqual(post_response.status_code, 302)
        self.assertIn(reverse('core:dashboard'), post_response.url)
        fine.refresh_from_db()
        self.assertEqual(fine.status, 'PENDING')





