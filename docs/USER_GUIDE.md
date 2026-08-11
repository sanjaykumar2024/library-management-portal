# LibrarySphere — User Guide

## Overview

LibrarySphere is a public library membership management and book reservation tracking portal. It supports three user roles: Admin, Librarian, and Member.

## Getting Started

### Accessing the Portal

Open your browser and navigate to **http://127.0.0.1:8000/**.

### Demo Accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Librarian | `librarian` | `librarian123` |
| Member | `member` | `member123` |

### Registering as a New Member

1. Click **Register** on the landing page.
2. Fill in username, email, and password.
3. Your account is created with MEMBER role and ACTIVE membership status.
4. Log in to access the Member Dashboard.

## User Roles & Permissions

### Admin

- Full system access including Django Admin (`/admin/`).
- View system-wide dashboard with real-time metrics (members, books, loans, fines).
- Access all reports and CSV exports.
- Manage librarian accounts.

### Librarian

- Issue, return, and renew physical books.
- Add/edit books, authors, categories, and physical copies via Django Admin.
- Upload and manage e-books (PDF).
- Process reservations.
- View circulation dashboard and reports.
- Export filtered data as CSV.

### Member

- Browse the book catalogue with search and filters.
- View personal dashboard with active loans, due dates, and overdue warnings.
- Place reservations (holds) on unavailable books.
- Read e-books online through the protected PDF viewer.
- Download e-books marked as READ_AND_DOWNLOAD.
- View personal reading history and notifications.

## Key Features

### Book Catalogue

- Browse at `/catalog/`.
- Search by title, author, or ISBN.
- Filter by category and book format (Physical, E-Book, Both).
- Click any book to view details, availability, and e-book access.

### Physical Book Circulation

- **Issue**: Librarian enters membership number and accession number at `/circulation/issue/`.
- **Return**: Librarian processes returns at `/circulation/return/`.
- **Renewal**: Librarian can renew active loans (up to 2 renewals per loan).
- **Overdue Fines**: Automatically calculated at ₹5/day when books are returned late.

### Reservations

- Members can reserve books that have no available copies.
- When a copy is returned, the system automatically allocates it to the next waiting member.
- Members receive in-app notifications when their reserved book is ready.
- Reservations expire after 2 days if not collected.

### E-Book Access

- Browse digital catalogue at `/ebooks/`.
- Read PDFs online in the protected viewer.
- Download permitted e-books.
- Access is controlled by membership status (must be ACTIVE).
- All reads and downloads are logged for audit purposes.

### Reports & Analytics (Admin/Librarian Only)

- Access at `/reports/`.
- Available reports: Membership, Book Inventory, Loans, Overdue, Fines, Reservations, E-Book Usage, Popular Books.
- All reports support filtering and CSV export.

### Notifications

- In-app notifications for reservation readiness, overdue alerts, and system messages.
- Notification bell icon in the sidebar shows unread count.
- Mark individual or all notifications as read.

## Mobile Support

The portal is fully responsive. All major pages adapt to mobile screen sizes with collapsible navigation and touch-friendly controls.
