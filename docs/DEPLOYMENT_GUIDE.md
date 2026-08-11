# LibrarySphere — Deployment Preparation Guide

## Prerequisites

- Python 3.13+
- MySQL 8.0+ (or SQLite for development)
- pip / virtualenv

## Step 1: Clone the Project

```bash
git clone <repository-url>
cd "Public Library Membership Management and Book Reservation Tracking Portal"
```

## Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

Copy the example environment file and fill in production values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DJANGO_SECRET_KEY=your-secure-random-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

USE_SQLITE=False
DB_NAME=library_portal_db
DB_USER=library_portal_user
DB_PASSWORD=your-strong-password
DB_HOST=127.0.0.1
DB_PORT=3306

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

Generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 4: Set Up MySQL Database

```sql
CREATE DATABASE library_portal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'library_portal_user'@'localhost' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON library_portal_db.* TO 'library_portal_user'@'localhost';
FLUSH PRIVILEGES;
```

## Step 5: Apply Migrations

```bash
python manage.py migrate
```

## Step 6: Create Admin Account

```bash
python manage.py createsuperuser
```

## Step 7: Seed Demo Data (Optional)

```bash
python manage.py seed_demo_data
```

This creates demo users (admin/librarian/member), categories, authors, books, physical copies, e-books with valid demo PDFs, loans, fines, reservations, and access logs.

## Step 8: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## Step 9: Create Protected E-Book Directory

```bash
mkdir -p protected_ebooks
chmod 700 protected_ebooks
```

Ensure this directory is NOT served by your web server (Nginx/Apache). It should only be accessible by the Django process.

## Step 10: Run Deployment Checks

```bash
python manage.py check --deploy
```

Fix any remaining warnings before going live.

## Step 11: Run with Gunicorn (Production)

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## Nginx Configuration (Example)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/project/staticfiles/;
    }

    location /media/ {
        alias /path/to/project/media/;
    }

    # IMPORTANT: Do NOT serve /protected_ebooks/ via Nginx

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Checklist

- [ ] `DJANGO_DEBUG=False`
- [ ] `DJANGO_SECRET_KEY` is unique and random
- [ ] `ALLOWED_HOSTS` is set to your domain(s)
- [ ] SSL certificate installed (Let's Encrypt / Cloudflare)
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `SECURE_HSTS_SECONDS=31536000`
- [ ] `.env` file is not committed to version control
- [ ] `protected_ebooks/` directory is not served by web server
- [ ] Database credentials are not in source code
- [ ] `python manage.py check --deploy` passes with no warnings
