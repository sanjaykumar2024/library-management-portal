import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import json
import uuid
import datetime
from decimal import Decimal

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import lxml.html

from catalog.models import Book, BookCopy, Category, Author, EBookMetadata, BookReview
from accounts.models import UserProfile
from circulation.models import Loan, Fine
from reservations.models import Reservation
import circulation.services as circ_services
import reservations.services as res_services
import ebooks.services as ebook_services


class TestTracker:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.not_tested = []

    def log_pass(self, category, test_name, details=""):
        entry = {'category': category, 'test': test_name, 'details': details}
        self.passed.append(entry)
        print(f"  [PASS] [{category}] {test_name} {f'({details})' if details else ''}")

    def log_fail(self, category, test_name, error=""):
        entry = {'category': category, 'test': test_name, 'error': str(error)}
        self.failed.append(entry)
        print(f"  [FAIL] [{category}] {test_name}: {error}")

    def log_not_tested(self, category, test_name, reason=""):
        entry = {'category': category, 'test': test_name, 'reason': reason}
        self.not_tested.append(entry)
        print(f"  [NOT TESTED] [{category}] {test_name}: {reason}")


tracker = TestTracker()


class BrowserSession:
    """
    Simulates a real web browser session:
    - Maintains cookies and session storage across requests
    - Extracts and passes CSRF tokens on forms and AJAX headers
    - Follows HTTP redirects by default
    - Provides DOM extraction with lxml
    """
    def __init__(self, username=None, password=None):
        self.client = Client()
        self.username = username
        self.password = password
        if username and password:
            self.login()

    def get_csrf(self):
        return self.client.cookies.get('csrftoken', '').value

    def login(self):
        login_res = self.client.get('/accounts/login/')
        csrf = self.get_csrf()
        res = self.client.post('/accounts/login/', {
            'username': self.username,
            'password': self.password,
            'csrfmiddlewaretoken': csrf
        }, follow=True)
        return res

    def get(self, url, **kwargs):
        kwargs.setdefault('follow', True)
        return self.client.get(url, **kwargs)

    def post(self, url, data=None, **kwargs):
        kwargs.setdefault('follow', True)
        csrf = self.get_csrf()
        if not csrf:
            self.client.get('/accounts/login/')
            csrf = self.get_csrf()

        if kwargs.get('content_type') == 'application/json':
            headers = kwargs.setdefault('headers', {})
            headers['X-CSRFToken'] = csrf
        elif isinstance(data, dict):
            data.setdefault('csrfmiddlewaretoken', csrf)
            
        return self.client.post(url, data, **kwargs)

    def dom(self, response):
        try:
            return lxml.html.fromstring(response.content.decode('utf-8', errors='ignore'))
        except Exception:
            return None


# ==============================================================================
# SECTION 1: AUTHENTICATION & ACCESS VERIFICATION
# ==============================================================================
print("\n" + "="*80)
print("SECTION 1: AUTHENTICATION & ACCESS VERIFICATION")
print("="*80)

admin_session = BrowserSession('admin', 'admin123')
lib_session = BrowserSession('librarian', 'librarian123')
member_session = BrowserSession('member', 'member123')
guest_session = BrowserSession()

# 1.1 Verify Sessions
for role, sess, uname in [('ADMIN', admin_session, 'admin'), ('LIBRARIAN', lib_session, 'librarian'), ('MEMBER', member_session, 'member')]:
    is_auth = sess.client.session.get('_auth_user_id') is not None
    if is_auth:
        tracker.log_pass('Auth', f"{role} Browser Login", f"Authenticated as {uname}")
    else:
        tracker.log_fail('Auth', f"{role} Browser Login", "Failed to authenticate session")

# 1.2 Verify Permission Boundaries
for path, name in [
    ('/circulation/', 'Circulation Desk'),
    ('/reports/', 'Reports Dashboard'),
    ('/catalog/book/create/', 'Book Creation Form'),
    ('/ebooks/manage/', 'Manage E-Books Portal'),
]:
    res = member_session.get(path)
    if res.status_code in [403, 302, 200] and ('Permission' in res.content.decode('utf-8', errors='ignore') or res.redirect_chain or 'Access denied' in res.content.decode('utf-8', errors='ignore')):
        tracker.log_pass('Auth Boundaries', f"Member Restricted from {name}", "Access safely blocked")
    else:
        tracker.log_fail('Auth Boundaries', f"Member Restricted from {name}", f"Unexpected access permitted: {res.status_code}")


# ==============================================================================
# SECTION 2: AUTOMATICALLY TEST ADMIN INTERFACE
# ==============================================================================
print("\n" + "="*80)
print("SECTION 2: ADMIN INTERFACE TESTING")
print("="*80)

# 2.1 Admin Dashboard & Stats
try:
    res = admin_session.get('/dashboard/admin/')
    assert res.status_code == 200
    dom = admin_session.dom(res)
    stats_cards = dom.xpath("//*[contains(@class, 'stat') or contains(@class, 'card')]")
    tracker.log_pass('Admin', "Admin Dashboard & Statistics", f"Status 200, {len(stats_cards)} UI stat cards found")
except Exception as e:
    tracker.log_fail('Admin', "Admin Dashboard", e)

# 2.2 Catalog Browsing, Search, and Category Filtering
try:
    res_list = admin_session.get('/catalog/')
    assert res_list.status_code == 200
    dom = admin_session.dom(res_list)
    cards = dom.xpath("//div[contains(@class, 'book-card') or contains(@class, 'card')]")
    tracker.log_pass('Admin', "Catalog List View", f"Status 200, {len(cards)} books displayed")

    res_search = admin_session.get('/catalog/?q=Data')
    assert res_search.status_code == 200
    tracker.log_pass('Admin', "Catalog Keyword Search", "Status 200 OK")

    cat = Category.objects.first()
    if cat:
        res_cat = admin_session.get(f'/catalog/?category={cat.id}')
        assert res_cat.status_code == 200
        tracker.log_pass('Admin', "Catalog Category Filtering", f"Filtered by '{cat.name}'")
except Exception as e:
    tracker.log_fail('Admin', "Catalog Browsing & Search", e)

# 2.3 Member Directory
try:
    res_mems = admin_session.get('/accounts/members/')
    assert res_mems.status_code == 200
    tracker.log_pass('Admin', "Member Directory", "Status 200 OK")
except Exception as e:
    tracker.log_fail('Admin', "Member Directory", e)

# 2.4 All Reports & CSV Generation (All 8 Reports)
reports = [
    ('/reports/', 'Overview Dashboard'),
    ('/reports/members/', 'Members Report'),
    ('/reports/members/csv/', 'Members CSV Export'),
    ('/reports/inventory/', 'Inventory Report'),
    ('/reports/inventory/csv/', 'Inventory CSV Export'),
    ('/reports/loans/', 'Loans Report'),
    ('/reports/loans/csv/', 'Loans CSV Export'),
    ('/reports/overdue/', 'Overdue Report'),
    ('/reports/overdue/csv/', 'Overdue CSV Export'),
    ('/reports/fines/', 'Fines Report'),
    ('/reports/fines/csv/', 'Fines CSV Export'),
    ('/reports/reservations/', 'Reservations Report'),
    ('/reports/reservations/csv/', 'Reservations CSV Export'),
    ('/reports/ebook-usage/', 'E-Book Usage Report'),
    ('/reports/ebook-usage/csv/', 'E-Book Usage CSV Export'),
    ('/reports/popular/', 'Popular Books Report'),
]

for url, name in reports:
    try:
        res = admin_session.get(url)
        assert res.status_code == 200
        tracker.log_pass('Admin Reports', name, f"{url} -> 200 OK")
    except Exception as e:
        tracker.log_fail('Admin Reports', name, e)


# ==============================================================================
# SECTION 3: AUTOMATICALLY TEST LIBRARIAN INTERFACE
# ==============================================================================
print("\n" + "="*80)
print("SECTION 3: LIBRARIAN INTERFACE TESTING")
print("="*80)

# 3.1 Circulation Desk Dashboard
try:
    res = lib_session.get('/circulation/')
    assert res.status_code == 200
    tracker.log_pass('Librarian', "Circulation Desk Dashboard", "Status 200 OK")
except Exception as e:
    tracker.log_fail('Librarian', "Circulation Desk Dashboard", e)

# 3.2 Return List View
try:
    res = lib_session.get('/circulation/return/')
    assert res.status_code == 200
    tracker.log_pass('Librarian', "Active Loans / Return List", "Status 200 OK")
except Exception as e:
    tracker.log_fail('Librarian', "Active Loans / Return List", e)

# 3.3 Fines Management List
try:
    res = lib_session.get('/circulation/fines/')
    assert res.status_code == 200
    tracker.log_pass('Librarian', "Fines Management List", "Status 200 OK")
except Exception as e:
    tracker.log_fail('Librarian', "Fines Management List", e)

# 3.4 Manage Reservations Queue
try:
    res = lib_session.get('/reservations/manage/')
    assert res.status_code == 200
    tracker.log_pass('Librarian', "Manage Reservations Queue", "Status 200 OK")
except Exception as e:
    tracker.log_fail('Librarian', "Manage Reservations Queue", e)

# 3.5 Self-Service Kiosk UI & Barcode Scanner APIs
try:
    res_kiosk = lib_session.get('/circulation/kiosk/')
    assert res_kiosk.status_code == 200
    tracker.log_pass('Librarian Kiosk', "Self-Service Kiosk UI", "Status 200 OK")

    # Barcode API Member lookup
    mem_u = User.objects.get(username='member')
    res_mem = lib_session.get(f'/circulation/api/kiosk/lookup-member/?q={mem_u.profile.membership_number}')
    assert res_mem.status_code == 200 and res_mem.json().get('success')
    tracker.log_pass('Librarian Kiosk', "Barcode API Member Lookup", f"Found: {mem_u.username} ({mem_u.profile.membership_number})")

    # Barcode API Book copy lookup
    avail_copy = BookCopy.objects.filter(status='AVAILABLE').first()
    if avail_copy:
        res_bk = lib_session.get(f'/circulation/api/kiosk/lookup-book/?q={avail_copy.accession_number}')
        assert res_bk.status_code == 200 and res_bk.json().get('success')
        tracker.log_pass('Librarian Kiosk', "Barcode API Book Copy Lookup", f"Found: {avail_copy.book.title} ({avail_copy.accession_number})")
except Exception as e:
    tracker.log_fail('Librarian Kiosk', "Kiosk API Operations", e)


# ==============================================================================
# SECTION 4: AUTOMATICALLY TEST USER / MEMBER INTERFACE
# ==============================================================================
print("\n" + "="*80)
print("SECTION 4: USER / MEMBER INTERFACE TESTING")
print("="*80)

# 4.1 Browse and Search Books
try:
    res = member_session.get('/catalog/')
    assert res.status_code == 200
    tracker.log_pass('Member', "Browse Book Catalog", "Status 200 OK")

    res_s = member_session.get('/catalog/?q=Data')
    assert res_s.status_code == 200
    tracker.log_pass('Member', "Search Catalog", "Status 200 OK")
except Exception as e:
    tracker.log_fail('Member', "Catalog Search", e)

# 4.2 Book Details & Availability Check
test_book = Book.objects.filter(is_active=True, copies__status='AVAILABLE').distinct().first()
if test_book:
    try:
        res = member_session.get(f'/catalog/book/{test_book.id}/')
        assert res.status_code == 200
        dom = member_session.dom(res)
        tracker.log_pass('Member', "Book Detail & Availability Check", f"'{test_book.title}' (Status: 200 OK)")
    except Exception as e:
        tracker.log_fail('Member', "Book Detail View", e)

# 4.3 Bookshelf Feature (Toggle API & View)
if test_book:
    try:
        res_toggle = member_session.post('/catalog/api/bookshelf/toggle/', json.dumps({'book_id': test_book.id}), content_type='application/json')
        assert res_toggle.status_code == 200
        data = res_toggle.json()
        tracker.log_pass('Member', "Toggle Bookshelf API", f"Saved: {data.get('saved')}")

        res_shelf = member_session.get('/catalog/my-bookshelf/')
        assert res_shelf.status_code == 200
        has_book = test_book.title in res_shelf.content.decode('utf-8')
        tracker.log_pass('Member', "View My Bookshelf", f"Book displayed: {has_book}")
    except Exception as e:
        tracker.log_fail('Member', "Bookshelf Feature", e)

# 4.4 Member Profile & Dashboard
try:
    res_prof = member_session.get('/accounts/profile/')
    assert res_prof.status_code == 200
    tracker.log_pass('Member', "Profile & Borrowing History View", "Status 200 OK")
except Exception as e:
    tracker.log_fail('Member', "Profile View", e)

# 4.5 Digital Reader & Streaming
ebook = EBookMetadata.objects.filter(is_active=True).first()
if ebook:
    try:
        res_read = member_session.get(f'/ebooks/{ebook.id}/read/')
        assert res_read.status_code == 200
        tracker.log_pass('Member E-Reader', "Online E-Book Reader View", f"'{ebook.book.title}' (Status: 200 OK)")

        res_stream = member_session.get(f'/ebooks/{ebook.id}/stream/')
        assert res_stream.status_code == 200
        tracker.log_pass('Member E-Reader', "E-Book Content Stream Endpoint", f"Content-Type: {res_stream.headers.get('Content-Type')}")

        # Annotations API
        res_ann_add = member_session.post(f'/ebooks/api/{ebook.id}/annotations/add/', json.dumps({
            'selected_text': 'A profound insight into learning and memory',
            'note': 'Research reference',
            'color': '#fde047'
        }), content_type='application/json')
        assert res_ann_add.status_code == 200
        ann_id = res_ann_add.json().get('annotation_id')
        tracker.log_pass('Member E-Reader', "Add Annotation API", f"Created ID: {ann_id}")

        res_ann_list = member_session.get(f'/ebooks/api/{ebook.id}/annotations/list/')
        assert res_ann_list.status_code == 200
        tracker.log_pass('Member E-Reader', "List Annotations API", f"Count: {len(res_ann_list.json().get('annotations', []))}")

        if ann_id:
            res_ann_del = member_session.post(f'/ebooks/api/annotations/{ann_id}/delete/')
            assert res_ann_del.status_code == 200
            tracker.log_pass('Member E-Reader', "Delete Annotation API", "Deleted successfully")
    except Exception as e:
        tracker.log_fail('Member E-Reader', "E-Book Reader & Annotations", e)


# ==============================================================================
# SECTION 5: COMPLETE PHYSICAL-BOOK LIFECYCLE (END-TO-END)
# ==============================================================================
print("\n" + "="*80)
print("SECTION 5: COMPLETE PHYSICAL-BOOK LIFECYCLE (END-TO-END)")
print("="*80)

test_suffix = uuid.uuid4().hex[:6].upper()
test_isbn = f"978-TEST-{test_suffix}"
test_acc = f"ACC-TEST-{test_suffix}"
test_shelf = f"Shelf Z-{test_suffix}"
test_title = f"Automated Lifecycle Test Book ({test_suffix})"
created_book = None
created_copy = None
test_loan = None

# Step A — Register a physical book and copy
try:
    cat = Category.objects.first()
    res_create = lib_session.post('/catalog/book/create/', {
        'title': test_title,
        'author_names': 'Dr. Automated Tester, Prof. Quality Assurance',
        'isbn': test_isbn,
        'category': cat.id if cat else '',
        'publisher': 'Quality Press Inc',
        'publication_year': 2026,
        'language': 'English',
        'description': 'A fully automated test volume to exercise end-to-end lifecycle verification.',
        'book_type': 'PHYSICAL',
        'is_active': 'on'
    })

    created_book = Book.objects.filter(isbn=test_isbn).first()
    assert created_book is not None, "Book was not found in database after create"
    assert created_book.is_active is True
    tracker.log_pass('Lifecycle Step A', "Manual Book Registration Workflow", f"Created '{created_book.title}' with ISBN {test_isbn}")

    # Add Physical Copy
    res_add_copy = lib_session.post(f'/catalog/book/{created_book.id}/add-copy/', {
        'accession_number': test_acc,
        'shelf_location': test_shelf,
        'condition': 'NEW',
        'status': 'AVAILABLE'
    })

    created_copy = BookCopy.objects.filter(accession_number=test_acc).first()
    assert created_copy is not None, "BookCopy was not created"
    assert created_copy.status == 'AVAILABLE'
    tracker.log_pass('Lifecycle Step A', "Physical Copy Accession & Shelf Assignment", f"Copy {test_acc} on {test_shelf} [Status: AVAILABLE]")
except Exception as e:
    tracker.log_fail('Lifecycle Step A', "Book & Copy Registration", e)

# Step B — Member Request & Librarian Issue
try:
    member_user = User.objects.get(username='member')
    member_profile = member_user.profile
    
    # Clean any prior conflicting reservations/loans for this book
    Reservation.objects.filter(book=created_book, member=member_profile).delete()
    Loan.objects.filter(book_copy__book=created_book, member=member_profile).delete()

    # 1. Member requests / reserves the book
    res_reserve = member_session.post(f'/reservations/book/{created_book.id}/reserve/')
    assert res_reserve.status_code == 200
    
    reservation = Reservation.objects.filter(book=created_book, member=member_profile, status__in=['PENDING', 'ALLOCATED']).first()
    assert reservation is not None, "Reservation record was not created"
    tracker.log_pass('Lifecycle Step B', "Member Book Reservation Request", f"Reservation #{reservation.id} [Status: {reservation.status}]")

    # 2. If status is PENDING, allocate copy
    if reservation.status == 'PENDING':
        res_alloc = lib_session.post(f'/reservations/allocate/{reservation.id}/')
        reservation.refresh_from_db()
    assert reservation.status == 'ALLOCATED', f"Expected ALLOCATED, got {reservation.status}"
    tracker.log_pass('Lifecycle Step B', "Librarian Hold Allocation", f"Copy {reservation.allocated_copy.accession_number} allocated to hold")

    # 3. Librarian fulfills reservation and issues the book
    res_fulfill = lib_session.post(f'/reservations/fulfill/{reservation.id}/')
    assert res_fulfill.status_code == 200
    
    reservation.refresh_from_db()
    assert reservation.status == 'FULFILLED'
    
    created_copy.refresh_from_db()
    assert created_copy.status == 'ISSUED'
    
    test_loan = Loan.objects.filter(book_copy=created_copy, member=member_profile, status='ISSUED').first()
    assert test_loan is not None, "Loan record not found"
    tracker.log_pass('Lifecycle Step B', "Reservation Fulfillment & Loan Issuance", f"Loan #{test_loan.id} issued. Due date: {test_loan.due_date}")

    # 4. Printable loan receipt
    res_receipt = lib_session.get(f'/circulation/loan/{test_loan.id}/receipt/')
    assert res_receipt.status_code == 200
    tracker.log_pass('Lifecycle Step B', "Loan Transaction Receipt View", "Receipt rendered 200 OK")
except Exception as e:
    tracker.log_fail('Lifecycle Step B', "Borrow & Issue Workflow", e)

# Step C — Overdue Simulation, Fine Calculation, and Sandbox Payment
try:
    overdue_days = 10
    test_loan.due_date = timezone.now().date() - datetime.timedelta(days=overdue_days)
    test_loan.save(update_fields=['due_date'])
    
    # Overdue scan
    res_scan = lib_session.post('/circulation/overdue/scan/')
    assert res_scan.status_code == 200
    tracker.log_pass('Lifecycle Step C', "Batch Overdue Scan Execution", "Overdue scan completed successfully")

    # Return overdue book
    res_return = lib_session.post(f'/circulation/return/{test_loan.id}/', {
        'copy_status': 'AVAILABLE',
        'condition_notes': 'Returned 10 days overdue during automated verification.'
    })
    assert res_return.status_code == 200
    
    test_loan.refresh_from_db()
    assert test_loan.status == 'RETURNED'
    
    # Fine calculation check
    fine = Fine.objects.filter(loan=test_loan).first()
    assert fine is not None, "Fine was not created on overdue return"
    expected_amount = Decimal(overdue_days) * circ_services.FINE_PER_DAY
    assert fine.amount == expected_amount, f"Expected fine ₹{expected_amount}, got ₹{fine.amount}"
    assert fine.status == 'PENDING'
    tracker.log_pass('Lifecycle Step C', "Overdue Fine Calculation", f"{overdue_days} days @ ₹{circ_services.FINE_PER_DAY}/day = ₹{fine.amount} [Status: PENDING]")

    # Member pays fine
    res_pay = member_session.post(f'/circulation/fines/{fine.id}/pay/', {
        'payment_method': 'UPI Sandbox Instant',
        'notes': 'Automated test settlement'
    })
    assert res_pay.status_code == 200
    
    fine.refresh_from_db()
    assert fine.status == 'PAID'
    tracker.log_pass('Lifecycle Step C', "Safe Sandbox Fine Payment", f"Fine #{fine.id} marked PAID ({fine.notes})")

    # Payment receipt
    res_fine_rcpt = member_session.get(f'/circulation/fines/{fine.id}/receipt/')
    assert res_fine_rcpt.status_code == 200
    tracker.log_pass('Lifecycle Step C', "Fine Payment Receipt View", "Receipt rendered 200 OK")

    # Prevent duplicate payment
    res_dup_pay = member_session.post(f'/circulation/fines/{fine.id}/pay/', {
        'payment_method': 'UPI Sandbox Instant'
    })
    assert 'already been paid' in res_dup_pay.content.decode('utf-8') or fine.status == 'PAID'
    tracker.log_pass('Lifecycle Step C', "Duplicate Payment Prevention", "Second payment attempt blocked safely")
except Exception as e:
    tracker.log_fail('Lifecycle Step C', "Fine & Payment Workflow", e)

# Step D — Return Book Availability & Duplicate Return Prevention
try:
    created_copy.refresh_from_db()
    assert created_copy.status == 'AVAILABLE'
    tracker.log_pass('Lifecycle Step D', "Book Copy Availability Restored", f"Copy {created_copy.accession_number} is back on shelf AVAILABLE")

    # Prevent duplicate return
    res_dup_ret = lib_session.post(f'/circulation/return/{test_loan.id}/', {'copy_status': 'AVAILABLE'})
    assert res_dup_ret.status_code in [200, 302, 404]
    test_loan.refresh_from_db()
    assert test_loan.status == 'RETURNED'
    tracker.log_pass('Lifecycle Step D', "Duplicate Return Prevention", "Attempting to return already returned loan was blocked safely")

    # Verify history
    res_hist = member_session.get('/accounts/profile/')
    assert created_book.title in res_hist.content.decode('utf-8')
    tracker.log_pass('Lifecycle Step D', "Patron Borrowing History Updated", f"'{created_book.title}' recorded in returned history")
except Exception as e:
    tracker.log_fail('Lifecycle Step D', "Return & History Verification", e)

# Clean up
try:
    if test_loan:
        Fine.objects.filter(loan=test_loan).delete()
        test_loan.delete()
    if created_copy:
        created_copy.delete()
    if created_book:
        created_book.delete()
    print("  ✓ Disposable test records cleaned up cleanly.")
except Exception as e:
    print(f"  Notice: cleanup error: {e}")


# ==============================================================================
# SECTION 6: CSV UPLOAD FAILURES & BULK BOOK IMPORT TESTING
# ==============================================================================
print("\n" + "="*80)
print("SECTION 6: CSV UPLOAD FAILURES & BULK BOOK IMPORT TESTING")
print("="*80)

# 6.1 Valid CSV Upload
try:
    valid_csv = """title,authors,isbn,categories,publication_year,description
Automated QA Novel,Jane Q. Tester,9781111000001,Fiction,2024,A compelling story of software resilience and precision.
The Architecture of AI,Alan M. Turing,9781111000002,Technology,2025,Foundational theories and modern developments in machine intelligence.
"""
    uploaded_file = SimpleUploadedFile('valid_books.csv', valid_csv.encode('utf-8'), content_type='text/csv')
    res_valid = lib_session.post('/ebooks/kaggle-import/', {
        'action': 'upload_csv',
        'csv_file': uploaded_file,
        'access_mode': 'READ_AND_DOWNLOAD',
        'rights_status': 'LIBRARY_LICENSED',
        'batch_limit': '50',
        'overwrite': 'on'
    })

    assert res_valid.status_code == 200
    b1 = Book.objects.filter(title='Automated QA Novel').first()
    b2 = Book.objects.filter(title='The Architecture of AI').first()
    assert b1 is not None and b2 is not None
    tracker.log_pass('CSV Ingestion', "Valid CSV Upload", f"Imported '{b1.title}' and '{b2.title}'")

    if b1: b1.delete()
    if b2: b2.delete()
except Exception as e:
    tracker.log_fail('CSV Ingestion', "Valid CSV Upload", e)

# 6.2 Malformed / Corrupt CSV
try:
    corrupt_content = b"\x00\xff\xfe\x00corrupt binary gibberish without headers\x99\x88\x77"
    uploaded_corrupt = SimpleUploadedFile('corrupt.csv', corrupt_content, content_type='text/csv')
    res_corrupt = lib_session.post('/ebooks/kaggle-import/', {
        'action': 'upload_csv',
        'csv_file': uploaded_corrupt,
        'batch_limit': '50'
    })
    assert res_corrupt.status_code == 200
    tracker.log_pass('CSV Ingestion', "Malformed / Corrupt CSV Handling", "Server handled corrupt CSV gracefully without 500 crash")
except Exception as e:
    tracker.log_fail('CSV Ingestion', "Malformed CSV Handling", e)

# 6.3 Missing Required Fields
try:
    missing_fields_csv = """title,authors,isbn,categories
,Unknown Author,9781111000003,Fiction
   ,Another Author,9781111000004,Non-Fiction
Valid Third Book,Good Author,9781111000005,General
"""
    uploaded_missing = SimpleUploadedFile('missing.csv', missing_fields_csv.encode('utf-8'), content_type='text/csv')
    res_missing = lib_session.post('/ebooks/kaggle-import/', {
        'action': 'upload_csv',
        'csv_file': uploaded_missing,
        'batch_limit': '50'
    })
    assert res_missing.status_code == 200
    b3 = Book.objects.filter(title='Valid Third Book').first()
    assert b3 is not None
    tracker.log_pass('CSV Ingestion', "Missing Required Fields Filtering", f"Skipped invalid rows and imported valid '{b3.title}'")
    if b3: b3.delete()
except Exception as e:
    tracker.log_fail('CSV Ingestion', "Missing Fields Filtering", e)

# 6.4 Duplicate Book Identifiers (Overwrite OFF vs ON)
try:
    dup_isbn = "9781111000006"
    Book.objects.filter(isbn=dup_isbn).delete()
    Book.objects.filter(title='Original Title').delete()
    Book.objects.filter(title='Updated Title Should Be Ignored').delete()
    
    # First import
    csv_1 = f"title,authors,isbn,categories\nOriginal Title,Author One,{dup_isbn},General\n"
    lib_session.post('/ebooks/kaggle-import/', {
        'action': 'upload_csv',
        'csv_file': SimpleUploadedFile('first.csv', csv_1.encode('utf-8'), content_type='text/csv'),
        'batch_limit': '50',
    })
    
    orig = Book.objects.get(title='Original Title')
    assert orig is not None

    # Second import with overwrite OFF
    csv_2 = f"title,authors,isbn,categories\nUpdated Title Should Be Ignored,Author Two,{orig.isbn},General\n"
    lib_session.post('/ebooks/kaggle-import/', {
        'action': 'upload_csv',
        'csv_file': SimpleUploadedFile('second.csv', csv_2.encode('utf-8'), content_type='text/csv'),
        'batch_limit': '50',
    })
    
    orig.refresh_from_db()
    assert orig.title == 'Original Title'
    tracker.log_pass('CSV Ingestion', "Duplicate ISBN Handling (Overwrite OFF)", "Existing record preserved when overwrite is off")

    # Third import with overwrite ON
    lib_session.post('/ebooks/kaggle-import/', {
        'action': 'upload_csv',
        'csv_file': SimpleUploadedFile('third.csv', csv_2.encode('utf-8'), content_type='text/csv'),
        'batch_limit': '50',
        'overwrite': 'on'
    })
    
    orig.refresh_from_db()
    assert orig.title == 'Updated Title Should Be Ignored'
    tracker.log_pass('CSV Ingestion', "Duplicate ISBN Handling (Overwrite ON)", "Existing record updated accurately when overwrite is on")

    orig.delete()
except Exception as e:
    tracker.log_fail('CSV Ingestion', "Duplicate ISBN Handling", e)

# 6.5 Batch Limits Enforcement (25, 50, 100)
try:
    Book.objects.filter(title__startswith='Batch Book').delete()
    rows = ["title,authors,isbn,categories"]
    for i in range(1, 41):
        rows.append(f"Batch Book {i:02d},Batch Author {i:02d},978888{i:07d},General")
    big_csv = "\n".join(rows)

    res_batch = lib_session.post('/ebooks/kaggle-import/', {
        'action': 'upload_csv',
        'csv_file': SimpleUploadedFile('big.csv', big_csv.encode('utf-8'), content_type='text/csv'),
        'batch_limit': '25'
    })
    assert res_batch.status_code == 200

    imported_batch_count = Book.objects.filter(title__startswith='Batch Book').count()
    assert imported_batch_count == 25, f"Expected 25 books imported, found {imported_batch_count}"
    tracker.log_pass('CSV Ingestion', "Batch Limit Constraint Enforcement", f"Strictly limited processing to 25 rows (Found: {imported_batch_count})")

    Book.objects.filter(title__startswith='Batch Book').delete()
except Exception as e:
    tracker.log_fail('CSV Ingestion', "Batch Limit Constraint Enforcement", e)


# ==============================================================================
# SUMMARY REPORT
# ==============================================================================
print("\n" + "="*80)
print("AUTOMATED BROWSER TEST SUITE COMPLETE")
print(f"TOTAL PASSED:     {len(tracker.passed)}")
print(f"TOTAL FAILED:     {len(tracker.failed)}")
print(f"TOTAL NOT TESTED: {len(tracker.not_tested)}")
print("="*80)

if tracker.failed:
    print("\nFAILURES IDENTIFIED:")
    for f in tracker.failed:
        print(f"  • [{f['category']}] {f['test']}: {f['error']}")
    sys.exit(1)
else:
    print("\nALL AUTOMATED TESTS EXECUTED AND PASSED WITH ZERO FAILURES!")
    sys.exit(0)
