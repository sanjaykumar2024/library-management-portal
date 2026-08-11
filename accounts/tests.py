from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile


class RegistrationTest(TestCase):
    def test_registration_creates_member_profile(self):
        """Public registration must create a UserProfile with role MEMBER."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newmember',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password1': 'Str0ng!Pass99',
            'password2': 'Str0ng!Pass99',
        })
        self.assertEqual(User.objects.filter(username='newmember').count(), 1)
        user = User.objects.get(username='newmember')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'MEMBER')

    def test_superuser_gets_admin_role(self):
        """Superuser creation via create_superuser must produce an ADMIN profile."""
        user = User.objects.create_superuser('admin', 'admin@test.com', 'Admin!Pass99')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'ADMIN')


class DashboardAccessTest(TestCase):
    def setUp(self):
        self.member = User.objects.create_user('member1', password='Test!Pass99')
        # profile auto-created by signal with role MEMBER

        self.librarian = User.objects.create_user('librarian1', password='Test!Pass99')
        self.librarian.profile.role = 'LIBRARIAN'
        self.librarian.profile.save()

        self.admin_user = User.objects.create_superuser('admin1', 'a@a.com', 'Test!Pass99')

    def test_member_redirected_to_member_dashboard(self):
        self.client.login(username='member1', password='Test!Pass99')
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, reverse('core:member_dashboard'))

    def test_librarian_redirected_to_librarian_dashboard(self):
        self.client.login(username='librarian1', password='Test!Pass99')
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, reverse('core:librarian_dashboard'))

    def test_admin_redirected_to_admin_dashboard(self):
        self.client.login(username='admin1', password='Test!Pass99')
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, reverse('core:admin_dashboard'))

    def test_member_cannot_access_admin_dashboard(self):
        self.client.login(username='member1', password='Test!Pass99')
        response = self.client.get(reverse('core:admin_dashboard'))
        # Should redirect away from admin dashboard
        self.assertNotEqual(response.status_code, 200)

    def test_member_cannot_access_librarian_dashboard(self):
        self.client.login(username='member1', password='Test!Pass99')
        response = self.client.get(reverse('core:librarian_dashboard'))
        self.assertNotEqual(response.status_code, 200)
