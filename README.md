# LibrarySphere — Public Library Membership Management and Book Reservation Tracking Portal

A comprehensive Django-based library portal with membership management, book cataloguing, physical/digital circulation, secure e-book access, analytics dashboards, reports, CSV data export, and full production preparation.

## Technology Stack

- **Backend:** Python 3.13, Django 6.0
- **Database:** MySQL 8.0 (via `mysqlclient`) / SQLite3 fallback for development
- **PDF Engine:** `pypdf`
- **Frontend:** Django Templates, Bootstrap 5, Glassmorphism Custom CSS
- **Static Files:** WhiteNoise

## Quick Start

### 1. Clone and set up

```bash
cd "Public Library Membership Management and Book Reservation Tracking Portal"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings (or use defaults for local dev)
```

### 3. Apply migrations and seed demo data

```bash
python manage.py migrate
python manage.py seed_demo_data
```

The seed command creates demo users, categories, authors, books (with physical copies and e-books), loans, fines, reservations, and access logs.

### 4. Run the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**

### Demo Accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Librarian | `librarian` | `librarian123` |
| Member | `member` | `member123` |
| Member | `alice_smith` | `member123` |

## Running Tests

```bash
python manage.py test tests.test_milestone3 tests.test_milestone4 tests.test_milestone5 tests.test_milestone6 catalog --settings=config.test_settings -v2
```

**Result: 56 tests pass with 0 failures.**

## Deployment Check

```bash
python manage.py check --deploy
```

## Project Structure

| App | Purpose |
|---|---|
| `core` | Landing page, role-aware dashboards (Admin, Librarian, Member) |
| `accounts` | User registration, login, profile, UserProfile model, membership status |
| `catalog` | Category, Author, Book, BookCopy, EBookMetadata models; catalogue views |
| `circulation` | Physical book issue, return, renewal, and fine tracking |
| `reservations` | Hold request queue, instant copy allocation, expiration handler |
| `notifications` | In-site notifications for holds and circulation alerts |
| `ebooks` | Protected PDF storage, online reader, download controls, access audit log |
| `reports` | System reports (8 types) and filtered CSV data export (7 endpoints) |

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | dev fallback | Cryptographic secret key |
| `DJANGO_DEBUG` | `False` | Debug mode toggle |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `USE_SQLITE` | `True` | Use SQLite instead of MySQL |
| `DB_NAME` | `library_portal_db` | MySQL database name |
| `DB_USER` | `library_portal_user` | MySQL username |
| `DB_PASSWORD` | (empty) | MySQL password |
| `DB_HOST` | `127.0.0.1` | MySQL host |
| `DB_PORT` | `3306` | MySQL port |
| `SECURE_SSL_REDIRECT` | `False` | Redirect HTTP to HTTPS |
| `SESSION_COOKIE_SECURE` | `False` | Secure session cookies |
| `CSRF_COOKIE_SECURE` | `False` | Secure CSRF cookies |
| `SECURE_HSTS_SECONDS` | `0` | HTTP Strict Transport Security |

## Documentation

- [User Guide](docs/USER_GUIDE.md)
- [Test Report](docs/TEST_REPORT.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [Backup & Restore](docs/BACKUP_RESTORE.md)
- [Demo Script](docs/DEMO_SCRIPT.md)

## Milestones

- [x] **Milestone 1** — Foundation, database setup, glassmorphism design
- [x] **Milestone 2** — Accounts, catalogue, role-aware dashboards
- [x] **Milestone 3** — Membership management, circulation desk, fines, reservations, notifications
- [x] **Milestone 4** — Secure PDF e-books, online streaming, controlled downloads, access logging
- [x] **Milestone 5** — Comprehensive dashboards, reports hub, filtered CSV exports, data privacy
- [x] **Milestone 6** — Full testing (56 tests), production preparation, demo data, documentation
