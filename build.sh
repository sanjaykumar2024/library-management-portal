#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "📦 Installing project dependencies..."
pip install -r requirements.txt

echo "🎨 Collecting static assets with WhiteNoise..."
python manage.py collectstatic --noinput

echo "🗄️ Applying database migrations..."
python manage.py migrate

echo "📥 Loading initial system data (users, profiles, loans, reservations, reviews, badges)..."
python manage.py loaddata data/complete_library_fixture.json || true

echo "📚 Populating complete library catalog (173 books, 378 copies, covers & e-books)..."
python populate_expanded_library.py

echo "🎨 Generating book covers for all 173 books..."
python manage.py regenerate_book_covers

echo "👤 Ensuring default demo accounts (admin, librarian, member) are active..."
python manage.py shell -c "
from django.contrib.auth.models import User
from accounts.models import UserProfile

# Admin
admin_u, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@library.org', 'is_staff': True, 'is_superuser': True})
admin_u.set_password('admin123')
admin_u.is_staff = True
admin_u.is_superuser = True
admin_u.save()
UserProfile.objects.update_or_create(user=admin_u, defaults={'role': 'ADMIN', 'membership_number': 'LIB-ADMIN-001', 'is_approved': True, 'membership_status': 'ACTIVE'})

# Librarian
lib_u, _ = User.objects.get_or_create(username='librarian', defaults={'email': 'librarian@library.org', 'is_staff': True})
lib_u.set_password('librarian123')
lib_u.is_staff = True
lib_u.save()
UserProfile.objects.update_or_create(user=lib_u, defaults={'role': 'LIBRARIAN', 'membership_number': 'LIB-STAFF-001', 'is_approved': True, 'membership_status': 'ACTIVE'})

# Member
mem_u, _ = User.objects.get_or_create(username='member', defaults={'email': 'member@library.org'})
mem_u.set_password('member123')
mem_u.save()
UserProfile.objects.update_or_create(user=mem_u, defaults={'role': 'MEMBER', 'membership_number': 'LIB-MEM-001', 'is_approved': True, 'membership_status': 'ACTIVE'})
print('Default accounts verified and passwords set!')
"

echo "✅ Build completed successfully!"
