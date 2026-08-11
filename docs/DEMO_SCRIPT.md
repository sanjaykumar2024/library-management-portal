# LibrarySphere — Final Demo Script

This script walks through all major features of the LibrarySphere portal for a live demonstration.

## Prerequisites

```bash
cd "Public Library Membership Management and Book Reservation Tracking Portal"
source .venv/bin/activate
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## Step 1: Landing Page

- Show the glassmorphism-styled landing page.
- Highlight the login and register buttons.
- Note the responsive design by resizing the browser window.

## Step 2: Admin Dashboard

1. Log in as **admin** / **admin123**.
2. View the Admin Dashboard showing:
   - Total members, active/expired/suspended breakdown
   - Total book titles, physical copies, and e-books
   - Available, issued, and reserved copies
   - Overdue loans count and pending fines total
   - Recent loans and reservations tables
3. Click **Reports & Analytics** in the sidebar.

## Step 3: Reports & CSV Export

1. Navigate to `/reports/`.
2. Open the **Membership Report** — show filtering by status.
3. Click **Export CSV** to download filtered membership data.
4. Open the **Overdue Books Report** — show contact information for follow-up.
5. Open the **Popular Books** report — show top titles by loan volume.

## Step 4: Librarian — Add a Book

1. Log out. Log in as **librarian** / **librarian123**.
2. Go to Django Admin (`/admin/`) → Books → Add Book.
3. Create a new book titled "Demo Library Book" with category "Technology".
4. Add 2 physical copies with accession numbers (e.g., LIB-DEMO-001, LIB-DEMO-002).
5. Return to the Librarian Dashboard to verify the new book appears.

## Step 5: Member Registration & Login

1. Log out. Click **Register** on the landing page.
2. Register a new member: username **demo_reader**, password **demopass123**.
3. Log in as the new member.
4. View the Member Dashboard showing membership status and available books.

## Step 6: Issue a Physical Book

1. Log out. Log in as **librarian** / **librarian123**.
2. Go to **Circulation** → **Issue Book**.
3. Enter the new member's membership number and an available accession number.
4. Submit to issue the book.
5. View the updated Librarian Dashboard — "Books Issued Today" should increment.

## Step 7: Reservation Queue

1. Log in as another member (**alice_smith** / **member123**).
2. Browse the catalogue and find the book that was just issued.
3. Click **Reserve** to place a hold.
4. View **My Reservations** showing the pending hold.

## Step 8: Return Book & Notification

1. Log in as **librarian** / **librarian123**.
2. Go to **Circulation** → **Process Return**.
3. Search for the issued book and process the return.
4. The system automatically allocates the returned copy to the waiting reservation.
5. Log in as **alice_smith** and check the notification bell — it should show "Your reserved book is ready for pickup".

## Step 9: E-Book Upload & Protected Reading

1. Log in as **librarian** / **librarian123**.
2. Go to **E-Books** → **Manage** → **Upload New E-Book**.
3. Select a book title, upload a demo PDF, set access mode to "Read & Download", rights to "Public Domain".
4. Submit the upload.
5. Log in as **member** / **member123**.
6. Go to **E-Books** catalogue.
7. Click an e-book to open the protected online reader.
8. Demonstrate that the PDF renders in the browser viewer.
9. Click **Download** to save the PDF (if access mode permits).
10. Go to **My Reading History** to show the access log.

## Step 10: Mobile Layout

1. Open browser Developer Tools (F12).
2. Toggle device toolbar to mobile view (iPhone / Android).
3. Navigate through:
   - Landing page
   - Catalogue
   - Member Dashboard
   - E-Book Reader
4. Show that all pages adapt cleanly to small screens.

## Step 11: Final Summary

Highlight the completed milestones:

1. ✅ Project foundation with MySQL and glassmorphism design
2. ✅ User accounts, catalogue, and role-based dashboards
3. ✅ Full circulation desk (issue, return, renewal, fines, reservations, notifications)
4. ✅ Secure e-book management (upload, protected reading, download control, access audit)
5. ✅ Comprehensive dashboards, reports, and CSV data export
6. ✅ Production preparation, testing (56 automated tests), and documentation
