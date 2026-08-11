import io
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from pypdf import PdfWriter

from accounts.models import UserProfile
from catalog.models import Category, Author, Book, BookCopy, EBookMetadata
from circulation.models import Loan, Fine
from reservations.models import Reservation
from ebooks.models import EBookAccessLog
from ebooks import services as ebook_services


def create_demo_pdf_bytes():
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    stream = io.BytesIO()
    writer.write(stream)
    stream.seek(0)
    return stream.getvalue()


class Command(BaseCommand):
    help = 'Seeds the database with realistic demo categories, authors, books, copies, members, loans, fines, reservations, and e-books.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing existing catalog, circulation, and user demo data...")
        EBookAccessLog.objects.all().delete()
        Fine.objects.all().delete()
        Loan.objects.all().delete()
        Reservation.objects.all().delete()
        BookCopy.objects.all().delete()
        EBookMetadata.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write("Seeding demo Users & Profiles...")
        # Admin
        admin, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@library.org', 'first_name': 'System', 'last_name': 'Admin', 'is_staff': True, 'is_superuser': True})
        admin.set_password('admin123')
        admin.save()
        admin.profile.role = 'ADMIN'
        admin.profile.save()

        # Librarian
        lib, _ = User.objects.get_or_create(username='librarian', defaults={'email': 'librarian@library.org', 'first_name': 'Jane', 'last_name': 'Librarian'})
        lib.set_password('librarian123')
        lib.save()
        lib.profile.role = 'LIBRARIAN'
        lib.profile.save()

        # Members
        mem1, _ = User.objects.get_or_create(username='member', defaults={'email': 'member@example.com', 'first_name': 'John', 'last_name': 'Member'})
        mem1.set_password('member123')
        mem1.save()
        mem1.profile.role = 'MEMBER'
        mem1.profile.membership_status = 'ACTIVE'
        mem1.profile.phone_number = '555-0101'
        mem1.profile.save()

        mem2, _ = User.objects.get_or_create(username='alice_smith', defaults={'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Smith'})
        mem2.set_password('member123')
        mem2.save()
        mem2.profile.role = 'MEMBER'
        mem2.profile.membership_status = 'ACTIVE'
        mem2.profile.phone_number = '555-0102'
        mem2.profile.save()

        self.stdout.write("Creating Categories...")
        categories_data = [
            {'name': 'Science Fiction', 'description': 'Speculative fiction exploring imaginative concepts.'},
            {'name': 'History', 'description': 'Factual accounts of past events and periods.'},
            {'name': 'Technology', 'description': 'Books on computing, engineering, and digital culture.'},
            {'name': 'Literature', 'description': 'Classic and contemporary literary fiction.'}
        ]
        categories = {}
        for c in categories_data:
            cat = Category.objects.create(**c)
            categories[cat.name] = cat

        self.stdout.write("Creating Authors...")
        authors_data = [
            {'full_name': 'Dr. Aris Thorne', 'bio': 'A leading historian of the 20th century.'},
            {'full_name': 'Elara Vance', 'bio': 'Award-winning science fiction novelist.'},
            {'full_name': 'Alan Turing', 'bio': 'Pioneer of computer science.'},
            {'full_name': 'Jane Austen', 'bio': 'English novelist known for her realism.'}
        ]
        authors = {}
        for a in authors_data:
            auth = Author.objects.create(**a)
            authors[auth.full_name] = auth

        self.stdout.write("Creating Books & Physical Copies...")
        books_data = [
            {
                'title': 'The Quantum Horizon', 'isbn': '9781234567890',
                'category': categories['Science Fiction'], 'book_type': 'BOTH',
                'publisher': 'Future Press', 'publication_year': 2024,
                'description': 'A mind-bending journey through quantum mechanics and space exploration.',
                'author_names': ['Elara Vance']
            },
            {
                'title': 'Echoes of Antiquity', 'isbn': '9781234567891',
                'category': categories['History'], 'book_type': 'PHYSICAL',
                'publisher': 'Heritage Books', 'publication_year': 2021,
                'description': 'A comprehensive look at the rise and fall of ancient empires.',
                'author_names': ['Dr. Aris Thorne']
            },
            {
                'title': 'Algorithms of Tomorrow', 'isbn': '9781234567892',
                'category': categories['Technology'], 'book_type': 'EBOOK',
                'publisher': 'Tech Nexus', 'publication_year': 2025,
                'description': 'Understanding the next wave of artificial intelligence.',
                'author_names': ['Alan Turing']
            },
            {
                'title': 'Pride and Prejudice', 'isbn': '9781234567893',
                'category': categories['Literature'], 'book_type': 'BOTH',
                'publisher': 'Classic Editions', 'publication_year': 1813,
                'description': 'A timeless romance exploring manners and marriage.',
                'author_names': ['Jane Austen']
            },
        ]

        accession_counter = 1000
        created_copies = []
        created_ebooks = []

        demo_pdf_bytes = create_demo_pdf_bytes()

        for b_data in books_data:
            author_names = b_data.pop('author_names')
            book = Book.objects.create(**b_data)
            for a_name in author_names:
                book.authors.add(authors[a_name])
            
            if book.book_type in ['PHYSICAL', 'BOTH']:
                for i in range(2):
                    c = BookCopy.objects.create(
                        book=book,
                        accession_number=f"LIB-{accession_counter}",
                        shelf_location=f"Row {book.category.name[0]}, Shelf {accession_counter % 5 + 1}",
                        status='AVAILABLE'
                    )
                    created_copies.append(c)
                    accession_counter += 1

            if book.book_type in ['EBOOK', 'BOTH']:
                file_obj = SimpleUploadedFile(
                    f"{book.title.lower().replace(' ', '_')}.pdf",
                    demo_pdf_bytes,
                    content_type="application/pdf"
                )
                ebook = ebook_services.validate_and_save_ebook(
                    file_obj=file_obj,
                    book=book,
                    uploaded_by=lib,
                    access_mode='READ_AND_DOWNLOAD' if book.book_type == 'BOTH' else 'READ_ONLY',
                    rights_status='PUBLIC_DOMAIN' if book.book_type == 'BOTH' else 'DEMO_ONLY',
                    rights_text='Demo public domain content for local testing.'
                )
                created_ebooks.append(ebook)

        self.stdout.write("Creating Loans & Fines...")
        today = timezone.now().date()
        # Active Loan
        if len(created_copies) > 0:
            c1 = created_copies[0]
            c1.status = 'ISSUED'
            c1.save()
            loan1 = Loan.objects.create(
                member=mem1.profile,
                book_copy=c1,
                issued_by=lib,
                issue_date=today - timezone.timedelta(days=5),
                due_date=today + timezone.timedelta(days=9),
                status='ISSUED'
            )

        # Overdue Loan with Fine
        if len(created_copies) > 1:
            c2 = created_copies[1]
            c2.status = 'ISSUED'
            c2.save()
            loan2 = Loan.objects.create(
                member=mem2.profile,
                book_copy=c2,
                issued_by=lib,
                issue_date=today - timezone.timedelta(days=20),
                due_date=today - timezone.timedelta(days=6),
                status='ISSUED'
            )
            Fine.objects.create(
                loan=loan2,
                amount=Decimal('30.00'),
                overdue_days=6,
                status='PENDING'
            )

        self.stdout.write("Creating Reservations...")
        Reservation.objects.create(
            member=mem1.profile,
            book=Book.objects.first(),
            status='PENDING'
        )

        self.stdout.write("Creating E-Book Access Logs...")
        if created_ebooks:
            EBookAccessLog.objects.create(
                user=mem1,
                ebook=created_ebooks[0],
                action='READ'
            )
            EBookAccessLog.objects.create(
                user=mem1,
                ebook=created_ebooks[0],
                action='DOWNLOAD'
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded realistic demo data for LibrarySphere!'))
