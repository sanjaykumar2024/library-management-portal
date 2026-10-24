# 🗺️ LibrarySphere — Master Project File Map & Directory Guide

> **Welcome to LibrarySphere!**  
> This document is your comprehensive directory map. It explains **which file is for what**, how the codebase is organized, and where to find any feature, model, template, or configuration in the project.

---

## 📁 1. High-Level Folder Structure Overview

```
Public Library Membership Management and Book Reservation Tracking Portal/
│
├── ⚙️ config/                 → Django Project Configuration (Settings, Root URLs, WSGI/ASGI)
│
├── 👤 accounts/               → User Authentication, Member Profiles, Tiers & Digital Library Cards
├── 📚 catalog/                → Book Cataloguing, Physical Copies, Reviews & AI Semantic Search
├── 🔄 circulation/            → Borrow & Return Desk, 14-Day Loans, Fines & Quick Checkout Kiosk
├── 📱 ebooks/                 → In-Browser Reader Studio, AI TTS Narration, Kaggle & Web Ingestion
├── ⏳ reservations/           → FIFO Hold Queue, Waitlists, Automated Allocation & Pickup Passes
├── 📊 reports/                → 7 Institutional Analytical Reports & 1-Click CSV Data Export
├── 🔔 notifications/          → Automated Event Alerts (Due dates, Hold pickups, Fine notices)
├── 🌐 core/                   → Public Homepage, Role-Based Dashboards & Help/FAQ
│
├── 🎨 templates/              → HTML Templates for All Pages (Organized by App)
├── 💅 static/                 → CSS Stylesheets (site.css), JavaScript, PWA Service Worker
├── 📦 staticfiles/            → Collected Static Files for Production Serving
├── 🖼️ media/                  → Uploaded & Generated Book Covers
├── 🔒 protected_ebooks/       → Non-Public DRM Storage for Streamed E-Book Files
├── 📊 data/                   → Datasets (Kaggle Books CSV for 1-Click Ingestion)
│
├── 🧪 tests/                  → Automated Milestone & Integration Test Suites
├── 🎤 presentations/          → Review Presentations (PPTX), Scripts & Viva Defense Guides
├── 📖 docs/                   → Technical Guides (User Guide, Deployment, Demo Script, Archive)
│
├── 🚀 manage.py               → Django Command-Line Management Utility
├── 📋 requirements.txt        → Python Dependency List
├── 🗄️ db.sqlite3              → Main SQLite Database (Development & Production)
├── 🧪 test_db.sqlite3         → Isolated Test SQLite Database (Used by Automated Tests)
├── 🔐 .env                    → Secret Keys, Database Choice & Environment Settings
├── 📄 .env.example            → Template Environment File
└── 📜 README.md               → Project Quickstart & Overview
```

---

## 🔍 2. Detailed Breakdown of Every Folder & File

---

### ⚙️ `config/` — Django Project Configuration
This folder contains the master configuration and wiring for the entire application.

| File | Purpose & Explanation |
| :--- | :--- |
| [`config/settings.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/config/settings.py) | **Central Settings:** Configures installed apps, database connection (SQLite/MySQL via `.env`), media/static paths, authentication password validators, and security headers. |
| [`config/urls.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/config/urls.py) | **Root URL Router:** Maps top-level web addresses (e.g., `/catalog/`, `/circulation/`, `/ebooks/`, `/reports/`) to their respective app modules. |
| [`config/wsgi.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/config/wsgi.py) | **WSGI Entry Point:** Standard interface for deployment on production web servers (e.g., Gunicorn, Nginx). |
| [`config/asgi.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/config/asgi.py) | **ASGI Entry Point:** Interface for asynchronous capabilities or WebSockets if deployed. |
| [`config/test_settings.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/config/test_settings.py) | **Test Runner Settings:** Isolated configuration running tests safely on `test_db.sqlite3` without touching the main database. |

---

### 👤 `accounts/` — User Management, Profiles & Memberships
Handles registration, member library cards, subscription tiers, and role-based access.

| File | Purpose & Explanation |
| :--- | :--- |
| [`accounts/models.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/accounts/models.py) | Defines `MemberProfile` (stores library card number `LIB-YYYY-XXXXX`, tiers `STANDARD`/`SCHOLAR`, status `ACTIVE`/`SUSPENDED`/`EXPIRED`, reading goals, QR token) and `MembershipRequest` (tier upgrades & renewals). |
| [`accounts/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/accounts/views.py) | Implements login/logout, user registration, member profile views, digital QR library cards, status toggles, membership requests processing, and the AJAX theme toggle API. |
| [`accounts/forms.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/accounts/forms.py) | Web forms for patron registration, contact information editing, and administrative status updates. |
| [`accounts/urls.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/accounts/urls.py) | URL routing for `/accounts/login/`, `/accounts/profile/`, `/accounts/members/`, `/accounts/settings/`, etc. |
| [`accounts/signals.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/accounts/signals.py) | Auto-generates a `MemberProfile` and library card number whenever a new `User` registers. |

---

### 📚 `catalog/` — Books, Copies, Reviews & AI Semantic Search
Manages both physical shelf inventory and the AI-powered book discovery engine.

| File | Purpose & Explanation |
| :--- | :--- |
| [`catalog/models.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/catalog/models.py) | Database models for `Category`, `Author`, `Book`, physical `BookCopy` (with accession numbers `BOK-XXXX`, shelf locations, and status `AVAILABLE`/`ON_LOAN`/`ON_HOLD`), `BookReview`, and `Bookshelf`. |
| [`catalog/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/catalog/views.py) | Views for browsing books, faceted search filtering, book details, librarian book addition/editing, shelf copy management, member reviews, and the **AI Semantic Search API** (`/catalog/api/semantic-search/`). |
| [`catalog/forms.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/catalog/forms.py) | Forms for creating/editing titles, adding physical shelf copies, and submitting star ratings/reviews. |
| [`catalog/urls.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/catalog/urls.py) | URL paths for `/catalog/`, book details, bookshelf management, and AI search endpoints. |

---

### 🔄 `circulation/` — Borrow & Return Desk, Fines & Self-Checkout Kiosk
The operational core for loan lifecycles, return processing, late fee collection, and self-service.

| File | Purpose & Explanation |
| :--- | :--- |
| [`circulation/models.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/circulation/models.py) | Defines `Loan` (tracks 14-day loan lifecycle, renewal count, due dates, return timestamps) and `Fine` (calculates late penalties at ₹5/day with payment status `PENDING`/`PAID`). |
| [`circulation/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/circulation/views.py) | **Borrow & Return Desk:** Staff checkout/return views, loan slips, thermal fine receipts, fine payment handling, and the **Quick Checkout Self-Service Kiosk** (`/circulation/kiosk/`). |
| [`circulation/forms.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/circulation/forms.py) | Validation forms for issuing books (card QR + accession barcode) and collecting fine payments. |
| [`circulation/urls.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/circulation/urls.py) | Paths for `/circulation/` (Desk), `/circulation/issue/`, `/circulation/returns/`, `/circulation/kiosk/`, and fine management. |

---

### 📱 `ebooks/` — Digital Reading Studio, AI Audio & Ingestion
Manages digital books, DRM-protected streaming, audio narration, and Kaggle/Web imports.

| File | Purpose & Explanation |
| :--- | :--- |
| [`ebooks/models.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/ebooks/models.py) | Defines `EBook` (linked to a `Book`, formats `PDF`/`EPUB`/`STREAM`, reading permissions `READ_ONLY`/`READ_AND_DOWNLOAD`, file storage) and `EBookAccessLog` (reading analytics telemetry). |
| [`ebooks/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/ebooks/views.py) | Views for Online E-Books, Free Classic Books, **In-Browser Reading Studio**, chunked DRM stream view, download handler, **Add Kaggle Books** portal, and **Add Web Books** (Open Library). |
| [`ebooks/kaggle_service.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/ebooks/kaggle_service.py) | **Kaggle Ingestion Engine:** Parses `data/kaggle_books.csv`, generates synthetic chapters and high-contrast SVG/PNG covers, and populates the database automatically. |
| [`ebooks/forms.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/ebooks/forms.py) | Forms for uploading e-book files and Kaggle spreadsheet uploads. |
| [`ebooks/urls.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/ebooks/urls.py) | Routing for `/ebooks/`, `/ebooks/<id>/read/`, `/ebooks/kaggle-import/`, `/ebooks/open-source/`, etc. |
| [`ebooks/management/commands/import_kaggle_ebooks.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/ebooks/management/commands/import_kaggle_ebooks.py) | Terminal management command (`python manage.py import_kaggle_ebooks`) for batch data ingestion. |

---

### ⏳ `reservations/` — Automated Hold Queue & Waitlists
Controls book waitlists and auto-allocates copies when checked back in.

| File | Purpose & Explanation |
| :--- | :--- |
| [`reservations/models.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/reservations/models.py) | Defines `Reservation` (FIFO queue position, status `PENDING`/`ALLOCATED`/`FULFILLED`/`EXPIRED`, 2-day pickup deadline). |
| [`reservations/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/reservations/views.py) | Member hold creation, waitlist queue status, **printable pickup pass** with barcode, staff hold queue manager, and expired hold cleanup. |
| [`reservations/urls.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/reservations/urls.py) | Paths for `/reservations/my-reservations/` and `/reservations/manage/`. |

---

### 📊 `reports/` — Institutional Analytics & CSV Export
Provides management metrics and compliance data exports for academic accreditation.

| File | Purpose & Explanation |
| :--- | :--- |
| [`reports/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/reports/views.py) | Generates visual dashboards and tabular reports: Loans Report, Overdue Report, Reservations Report, Membership Demographics, E-Book Usage, and Fine Collections Revenue, with 1-click **CSV Export**. |
| [`reports/urls.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/reports/urls.py) | URL routing for `/reports/` and specific report detail pages. |

---

### 🔔 `notifications/` — Activity Alerts & Notifications
Keeps users informed about due dates, holds ready for pickup, and fine statuses.

| File | Purpose & Explanation |
| :--- | :--- |
| [`notifications/models.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/notifications/models.py) | Defines `Notification` (message, type, read status, action links). |
| [`notifications/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/notifications/views.py) | User notifications page, mark-as-read actions, and unread count badge API. |
| [`notifications/urls.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/notifications/urls.py) | URL endpoints for notification feeds and mark-as-read actions. |

---

### 🌐 `core/` — Public Website, Dashboards & Seeding
Contains public landing pages, customized role dashboards, and demo dataset generation.

| File | Purpose & Explanation |
| :--- | :--- |
| [`core/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/core/views.py) | Public home view, smart `/dashboard/` router (redirects to Admin, Librarian, or Member home based on role), Help/FAQ view, Privacy, and Terms. |
| [`core/urls.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/core/urls.py) | URL routes for homepage, dashboards, and static pages. |
| [`core/management/commands/seed_demo_data.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/core/management/commands/seed_demo_data.py) | **Demo Data Seeder:** Generates realistic test users, physical books, digital e-books, active loans, fines, and reservations with a single command. |

---

### 🎨 `templates/` — HTML Templates (Organized by App)
All frontend pages, written using Django templates and Bootstrap 5 with zero jargon.

```
templates/
├── base.html                     → Public layout (Navbar, Hero, Footer)
├── portal_base.html              → Authenticated Portal layout (Sidebar, Theme Switcher, Cmd+K AI Modal)
├── 403.html / 404.html / 500.html→ High-contrast error pages
├── core/                         → Home page, Help/FAQ, and Dashboards (Admin, Librarian, Member)
├── accounts/                     → Login, Register, My Profile, Member List, Member Detail, Settings
├── catalog/                      → Search Books, Book Detail, Book Add/Edit, Saved Bookshelf, AI Helper
├── circulation/                  → Borrow & Return Desk, Lend Book, Return Book, Fines, Quick Checkout Kiosk
├── ebooks/                       → Online E-Books, Free Classics, In-Browser Reader Studio, Add Kaggle Books
├── reservations/                 → Reserved Books (Pickup Pass), Book Holds Queue, Lend Reserved Book
├── reports/                      → Library Reports Index, Visual Charts & 7 Filterable Data Tables
└── notifications/                → Notifications Feed
```

---

### 💅 `static/` — Frontend Assets (Styles, Scripts & PWA)

| File | Purpose & Explanation |
| :--- | :--- |
| [`static/css/site.css`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/static/css/site.css) | **Global Theme Engine:** Defines CSS variables for Light Mode and Dark Mode, button border tokens (`#CBD5E1`), glassmorphism cards, and zero-flicker transitions. |
| [`static/js/sw.js`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/static/js/sw.js) | **Service Worker (PWA):** Enables offline caching for digital library cards and static icons. |
| [`static/manifest.json`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/static/manifest.json) | **PWA Web App Manifest:** Allows the portal to be installed on mobile phones and desktop computers like a native app. |

---

### 🎤 `presentations/` — Review Slides, Scripts & Viva Defense
All presentation preparation materials stored in one clean, convenient folder.

| File | Purpose & Explanation |
| :--- | :--- |
| `presentations/First_Review_Presentation.pptx` | 24-slide PowerPoint presentation matching institutional guidelines. |
| `presentations/generate_presentation.py` | Python script using `python-pptx` that programmatically builds the slides. |
| `presentations/FIRST_REVIEW_GUIDE.md` | Complete presentation guide and literature review for Review 1. |
| `presentations/SECOND_REVIEW_GUIDE.md` | Comprehensive preparation guide for Review 2 (Elevator pitch, features, novelties, live demo script, and viva defense). |

---

### 📊 `data/` — Data Files
| File | Purpose & Explanation |
| :--- | :--- |
| [`data/kaggle_books.csv`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/data/kaggle_books.csv) | High-quality dataset containing 90+ verified books across AI, Software Engineering, Literature, and Science used by the 1-click Kaggle ingestion engine. |

---

### 🔒 `protected_ebooks/` & 🖼️ `media/` — File Storage
- **`protected_ebooks/`**: A secured, non-web-accessible directory holding chapter files and protected PDFs. Files here cannot be accessed directly via web URLs—they can only be streamed through authenticated Django views to prevent piracy.
- **`media/`**: Stores public uploaded media, such as book cover images (`media/book_covers/`).

---

## 🧭 3. Quick "Where Do I Find..." Lookup Table

| If You Are Looking For... | Go To This Exact File / Location: |
| :--- | :--- |
| **The AI Semantic Search code** | [`catalog/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/catalog/views.py) (function `semantic_search_api`) & modal in [`templates/portal_base.html`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/templates/portal_base.html) |
| **The Kaggle Book Import logic** | [`ebooks/kaggle_service.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/ebooks/kaggle_service.py) & [`ebooks/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/ebooks/views.py) |
| **The Quick Checkout Kiosk** | View: [`circulation/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/circulation/views.py) (`kiosk_checkout`) & Template: [`templates/circulation/kiosk.html`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/templates/circulation/kiosk.html) |
| **The In-Browser E-Book Reader Studio** | View: [`ebooks/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/ebooks/views.py) (`reader_view`) & Template: [`templates/ebooks/reader.html`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/templates/ebooks/reader.html) |
| **The AI Text-to-Speech (TTS) Narration** | JavaScript in [`templates/ebooks/reader.html`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/templates/ebooks/reader.html) (Web Speech API) |
| **The Automated Fine Calculation** | [`circulation/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/circulation/views.py) (`process_return`) |
| **The Automated Hold Queue Allocation** | [`circulation/views.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/circulation/views.py) (inside return processing) & [`reservations/models.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/reservations/models.py) |
| **The Light / Dark Mode CSS & Engine** | Styles: [`static/css/site.css`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/static/css/site.css) & Script in [`templates/portal_base.html`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/templates/portal_base.html) |
| **The Database connection settings** | [`config/settings.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/config/settings.py) & [`.env`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/.env) |
| **The Automated Tests** | [`ebooks/tests.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/ebooks/tests.py) and [`tests/`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/tests/) |
| **Review 2 Presentation Guide & Demo Script** | [`presentations/SECOND_REVIEW_GUIDE.md`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/presentations/SECOND_REVIEW_GUIDE.md) |
