import os
import uuid
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from pypdf import PdfReader
from catalog.models import EBookMetadata
from .models import EBookAccessLog

def validate_and_save_ebook(file_obj, book, uploaded_by, access_mode, rights_status, rights_text, access_note='', existing_ebook=None):
    """
    Validates PDF file format, size, magic signature, and readability,
    saves the file to PROTECTED_EBOOK_ROOT with a randomized filename,
    and creates/updates the EBookMetadata model instance.
    """
    # 1. Check book type
    if book.book_type not in ['EBOOK', 'BOTH']:
        raise ValueError("Selected book must be configured as 'E-Book Only' or 'Both Physical and E-Book'.")

    # 2. Check file extension
    original_filename = file_obj.name
    ext = os.path.splitext(original_filename)[1].lower()
    if ext not in ['.pdf', '.html', '.htm']:
        raise ValueError("Invalid file extension. Only PDF (.pdf) and HTML (.html, .htm) files are supported.")

    # 3. Check file size
    max_size = getattr(settings, 'MAX_EBOOK_FILE_SIZE', 20 * 1024 * 1024)
    if file_obj.size > max_size:
        max_mb = max_size / (1024 * 1024)
        raise ValueError(f"File size exceeds maximum allowed limit of {max_mb:.0f} MB.")

    file_format = 'HTML' if ext in ['.html', '.htm'] else 'PDF'
    page_count = 1

    if file_format == 'PDF':
        # 4. Check magic bytes PDF signature (%PDF-)
        file_obj.seek(0)
        header = file_obj.read(1024)
        file_obj.seek(0)
        if not header.startswith(b'%PDF-'):
            raise ValueError("Invalid file format. File header is not a valid PDF document.")

        # 5. Parse PDF with pypdf to validate structure and get page count
        try:
            reader = PdfReader(file_obj)
            page_count = len(reader.pages)
            file_obj.seek(0)
        except Exception as e:
            file_obj.seek(0)
            raise ValueError(f"Corrupted or unreadable PDF file: {str(e)}")
    else:
        # Validate HTML content
        file_obj.seek(0)
        content = file_obj.read().decode('utf-8', errors='ignore')
        file_obj.seek(0)
        if not content.strip():
            raise ValueError("HTML file is empty.")
        # Estimate section/page count from headings or divs
        h_count = content.lower().count('<h') or content.lower().count('<div') or 1
        page_count = min(max(h_count, 1), 100)

    # 6. Prepare protected storage directory
    protected_root = Path(getattr(settings, 'PROTECTED_EBOOK_ROOT', settings.BASE_DIR / 'protected_ebooks'))
    os.makedirs(protected_root, exist_ok=True)

    # 7. Generate safe randomized filename
    new_protected_filename = f"{uuid.uuid4().hex}{ext}"
    new_file_path = protected_root / new_protected_filename

    # Save file chunks to protected path
    try:
        with open(new_file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
    except Exception as e:
        raise ValueError(f"Failed to write file to protected storage: {str(e)}")

    # Remove old protected file if replacing
    if existing_ebook and existing_ebook.protected_filename:
        old_file_path = protected_root / existing_ebook.protected_filename
        if old_file_path.exists():
            try:
                os.remove(old_file_path)
            except OSError:
                pass

    # 8. Create or update EBookMetadata
    if existing_ebook:
        ebook = existing_ebook
    else:
        ebook, created = EBookMetadata.objects.get_or_create(book=book)

    ebook.protected_filename = new_protected_filename
    ebook.original_file_name = original_filename
    ebook.uploaded_by = uploaded_by
    ebook.uploaded_at = timezone.now()
    ebook.file_size = file_obj.size
    ebook.page_count = page_count
    ebook.format = file_format
    ebook.access_mode = access_mode
    ebook.rights_status = rights_status
    ebook.rights_text = rights_text
    ebook.access_note = access_note
    ebook.is_active = True
    ebook.save()

    return ebook



def update_ebook_metadata_only(ebook, access_mode, rights_status, rights_text, access_note, is_active=True, rental_price=None):
    """Updates metadata fields without changing the uploaded PDF file."""
    ebook.access_mode = access_mode
    ebook.rights_status = rights_status
    ebook.rights_text = rights_text
    ebook.access_note = access_note
    ebook.is_active = is_active
    if rental_price is not None:
        ebook.rental_price = rental_price
    ebook.save()
    return ebook



def log_ebook_access(user, ebook, action, ip_address=None):
    """Records user access (READ or DOWNLOAD) in EBookAccessLog."""
    return EBookAccessLog.objects.create(
        user=user,
        ebook=ebook,
        action=action,
        ip_address=ip_address
    )


def get_protected_file_path(ebook):
    """Retrieves full absolute path to the protected file, auto-regenerating if missing."""
    protected_root = Path(getattr(settings, 'PROTECTED_EBOOK_ROOT', settings.BASE_DIR / 'protected_ebooks'))
    os.makedirs(protected_root, exist_ok=True)

    if not ebook.protected_filename:
        ebook.protected_filename = f"{uuid.uuid4().hex}.html"
        ebook.format = 'HTML'
        ebook.save(update_fields=['protected_filename', 'format'])

    file_path = protected_root / ebook.protected_filename

    if not file_path.exists():
        try:
            from .kaggle_service import KaggleEBookService
            book = ebook.book
            first_author = book.authors.first() if hasattr(book, 'authors') else None
            first_author_name = first_author.full_name if first_author else 'Unknown Author'
            cat_name = book.category.name if book.category else 'General'

            book_info = {
                'title': book.title,
                'subtitle': getattr(book, 'subtitle', '') or '',
                'author': first_author_name,
                'category': cat_name,
                'publisher': book.publisher or 'Public Library Digital Collection',
                'publication_year': book.publication_year or 2024,
                'description': book.description or f"Complete digital edition of {book.title}.",
                'isbn': book.isbn or '',
                'pages': ebook.page_count or 300,
                'average_rating': 4.5,
            }
            doc_html = KaggleEBookService._generate_reader_document(book_info)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc_html)
            ebook.file_size = len(doc_html.encode('utf-8'))
            ebook.save(update_fields=['file_size'])
        except Exception:
            raise FileNotFoundError("Protected e-book file was not found on server storage.")

    return file_path
