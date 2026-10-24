# 📚 LibrarySphere — Hybrid Public Library Management & Intellectual Knowledge Portal

[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Tests](https://img.shields.io/badge/Tests-30%20Passed%20(100%25)-brightgreen.svg)]()
[![PWA](https://img.shields.io/badge/PWA-Ready-orange.svg)]()

> An autonomous hybrid library management portal that seamlessly converges physical bookshelf tracking with interactive digital reading, AI semantic book discovery, automated Kaggle & Web catalog ingestion, and hardware-free self-checkout kiosks.

---

## ⚡ Quick Start

### 1. Environment Setup
```bash
# Clone or navigate to the directory
cd "Public Library Membership Management and Book Reservation Tracking Portal"

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

### 2. Database Initialization
```bash
# Apply database migrations
python manage.py migrate

# (Optional) Seed realistic demo users, books, loans & reservations
python manage.py seed_demo_data
```

### 3. Run Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 🔑 Demo Login Accounts

| Role | Username | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full system oversight, Membership Requests, Analytics & Reports |
| **Librarian** | `librarian` | `librarian123` | Borrow & Return Desk, Kaggle Ingestion, Web Books, Hold Queue |
| **Member / Patron** | `member` | `member123` | Search Books, E-Book Studio with AI Audio, Saved Shelf, Goals |
| **Scholar Member** | `alice_smith`| `member123` | Scholar Tier (5 simultaneous loans), Reviews, Waitlists |

---

## 🌟 Key Features Overview

- **Unified Hybrid Catalog:** Track physical shelf locations, accession barcodes (`BOK-XXXX`), and instant digital reading availability in one place.
- **AI Semantic Intent Search (`Cmd+K` / `Ctrl+K`):** Conversational search returning relevance percentages, contextual citations, and 1-click action pills.
- **Multi-Source E-Book Acquisition:**
  - **1-Click Kaggle Ingestion:** Import 90+ verified books with auto-generated covers and chapters from `data/kaggle_books.csv`.
  - **Open Library API:** Live web discovery and importing of public domain classics.
- **In-Browser E-Book Studio:** Distraction-free reader with font sizing, Sepia/Light/Dark themes, and **AI Speech Audio Narration (Text-to-Speech)**.
- **Hardware-Free Quick Checkout Kiosk:** Self-service touch and camera station for patrons to borrow books in seconds using standard device cameras.
- **Automated Hold Queue:** FIFO reservation queue that automatically re-allocates returned physical books and issues printable pickup passes.
- **Overdue Fine Engine:** Automated ₹5/day calculation with printable thermal payment receipts.
- **PWA & Offline Digital Card:** Installable mobile web app with offline QR library card verification.
- **Dual Mode (Light & Dark):** High-contrast, zero-flicker theme engine with plain-English terminology across all 15+ sub-modules.

---

## 🗺️ Project Architecture & Directory Map

For a full line-by-line guide of **which file is for what**, please see **[`PROJECT_MAP.md`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/PROJECT_MAP.md)**.

```
├── config/              # Django Master Settings, Root URLs, WSGI/ASGI
├── accounts/            # User Profiles, Library Cards, Tiers & Requests
├── catalog/             # Books, Physical Copies, Reviews & AI Semantic Search
├── circulation/         # Borrow & Return Desk, Loans, Fines & Camera Kiosk
├── ebooks/              # E-Book Reader Studio, AI TTS, Kaggle & Web Ingestion
├── reservations/        # FIFO Hold Queues, Automated Allocation & Pickup Passes
├── reports/             # 7 Institutional Analytical Reports & CSV Export
├── notifications/       # User Notification Alerts & Event Feeds
├── core/                # Homepage, Role Dashboards & Help/FAQ
├── templates/           # All HTML Templates organized cleanly by app
├── static/              # CSS Stylesheets (site.css), JavaScript, PWA Manifest
├── media/               # Uploaded and Generated Book Covers
├── protected_ebooks/    # DRM-Secured Storage for Streamed E-Books (Non-Public)
├── data/                # Dataset Files (kaggle_books.csv)
├── tests/               # Milestone & Integration Test Suites
├── presentations/       # Review Slides (PPTX), Python Generators & Viva Guides
└── docs/                # Technical Guides, User Manual & Documentation Archive
```

---

## 🧪 Running Automated Tests

Run the full automated test suite:
```bash
python manage.py test
```
*Current Status: All 30 test cases pass cleanly with 0 failures.*

---

## 🎤 Presentation & Review Materials

Review slides, presentation scripts, and viva defense answers are neatly organized in the [`presentations/`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/presentations/) folder:
- **[`presentations/SECOND_REVIEW_GUIDE.md`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/presentations/SECOND_REVIEW_GUIDE.md)**: 2-minute pitch, feature breakdown, real-world utility, technical novelty, live demo script, and viva defense answers.
- **[`presentations/First_Review_Presentation.pptx`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/presentations/First_Review_Presentation.pptx)**: 24-slide presentation deck.
- **[`presentations/generate_presentation.py`](file:///Users/sk/Documents/Public%20Library%20Membership%20Management%20and%20Book%20Reservation%20Tracking%20Portal/presentations/generate_presentation.py)**: Python script used to build PowerPoint slides.

---

## 📄 License & Attribution
Academic Project Work II (`24S7INT369`) — Developed at Bannari Amman Institute of Technology.
