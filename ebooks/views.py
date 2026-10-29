from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponseForbidden, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.conf import settings
from pathlib import Path
import uuid

from catalog.models import Book, Category, EBookMetadata
from .models import EBookAccessLog
from .forms import EBookUploadForm, EBookEditForm
from . import services
from core.decorators import librarian_required

def is_librarian(user):
    return user.is_authenticated and (user.profile.is_librarian() or user.profile.is_admin())

def can_user_access_ebook(user, ebook):
    """
    Checks if a user is permitted to view/read/stream an e-book.
    Free library e-books (rental_price == 0), public domain, and open licenses
    are accessible to all visitors and patrons.
    For paid/restricted e-books, user must be authenticated with active membership
    and have an active digital reading pass.
    """
    if not ebook.is_active:
        return False, "This e-book is currently inactive or unavailable."

    if is_librarian(user):
        return True, ""

    # All free library collection books, public domain classics, and open licenses are open for online reading
    if ebook.rental_price == 0 or ebook.rights_status in ['PUBLIC_DOMAIN', 'OPEN_LICENSE', 'LIBRARY_LICENSED']:
        return True, ""

    if not user.is_authenticated:
        return False, "Authentication required to access this e-book."
        
    # Regular member check
    profile = getattr(user, 'profile', None)
    if profile:
        if profile.membership_status == 'SUSPENDED':
            return False, "Your account has been suspended by the library administration."
        if not getattr(profile, 'can_access_ebooks', True):
            return False, "E-book reading privileges have been disabled for this account."
    if not profile or profile.membership_status != 'ACTIVE':
        return False, "Active library membership is required to access e-books."
        
    # Check concurrent reader limit (15 min active window)
    if ebook.max_concurrent_readers > 0:
        from django.utils import timezone
        import datetime
        recent_window = timezone.now() - datetime.timedelta(minutes=15)
        active_readers_count = ebook.access_logs.filter(
            action='READ',
            accessed_at__gte=recent_window
        ).values('user').distinct().count()

        already_reading = False
        if user.is_authenticated:
            already_reading = ebook.access_logs.filter(
                user=user, action='READ', accessed_at__gte=recent_window
            ).exists()
        
        if not already_reading and active_readers_count >= ebook.max_concurrent_readers:
            return False, f"All {ebook.max_concurrent_readers} simultaneous reader licenses for this e-book are currently in use. Please try again shortly."

    # Check digital reading pass requirement (if rental_price > 0)
    if ebook.rental_price > 0:
        from .models import EBookPass
        has_pass = EBookPass.objects.filter(user=user, ebook=ebook, is_active=True).exists()
        if not has_pass:
            return False, "PAYMENT_REQUIRED"

    return True, ""




def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def ebook_catalog_view(request):
    """Public/Member E-Book catalogue with search and filtering."""
    q = request.GET.get('q', '')
    category_id = request.GET.get('category', '').strip()
    rights_status = request.GET.get('rights', '')
    access_mode = request.GET.get('mode', '')
    
    category_obj = Category.resolve(category_id) if category_id else None
    selected_category = str(category_obj.id) if category_obj else (category_id if category_id.isdigit() else '')
    
    ebooks = EBookMetadata.objects.select_related('book', 'book__category').prefetch_related('book__authors')
    
    # Non-librarians can only see active e-books
    if not is_librarian(request.user):
        ebooks = ebooks.filter(is_active=True)
        
    if q:
        ebooks = ebooks.filter(
            Q(book__title__icontains=q) |
            Q(book__authors__full_name__icontains=q) |
            Q(book__isbn__icontains=q)
        ).distinct()
        
    if category_obj:
        ebooks = ebooks.filter(book__category=category_obj)
    elif category_id and category_id.isdigit():
        ebooks = ebooks.filter(book__category_id=int(category_id))
    elif category_id:
        ebooks = ebooks.filter(book__category__name__icontains=category_id)
        
    if rights_status:
        ebooks = ebooks.filter(rights_status=rights_status)
        
    if access_mode:
        ebooks = ebooks.filter(access_mode=access_mode)
        
    categories = Category.objects.all().order_by('name')
    
    context = {
        'ebooks': ebooks,
        'categories': categories,
        'q': q,
        'selected_category': selected_category,
        'selected_rights': rights_status,
        'selected_mode': access_mode,
        'rights_choices': EBookMetadata.RIGHTS_STATUS_CHOICES,
        'mode_choices': EBookMetadata.ACCESS_MODE_CHOICES,
    }
    return render(request, 'ebooks/ebook_catalog.html', context)


def ebook_detail_view(request, ebook_id):
    """Detailed view for a specific e-book."""
    ebook = get_object_or_404(EBookMetadata.objects.select_related('book', 'book__category', 'uploaded_by'), id=ebook_id)
    
    from .models import EBookPass
    if request.user.is_authenticated:
        has_unlocked = is_librarian(request.user) or (ebook.rental_price == 0) or EBookPass.objects.filter(user=request.user, ebook=ebook, is_active=True).exists()
    else:
        has_unlocked = (ebook.rental_price == 0) or (ebook.rights_status == 'PUBLIC_DOMAIN')

    # Read & download counts for Librarians/Admins only
    read_count = 0
    download_count = 0
    if request.user.is_authenticated and is_librarian(request.user):
        read_count = ebook.access_logs.filter(action='READ').count()
        download_count = ebook.access_logs.filter(action='DOWNLOAD').count()
        
    context = {
        'ebook': ebook,
        'has_unlocked': has_unlocked,
        'read_count': read_count,
        'download_count': download_count,
        'can_download': ebook.access_mode == 'READ_AND_DOWNLOAD',
    }
    return render(request, 'ebooks/ebook_detail.html', context)


def ebook_read_view(request, ebook_id):
    """Online protected reader view."""
    ebook = get_object_or_404(EBookMetadata.objects.select_related('book'), id=ebook_id)
    
    can_access, reason = can_user_access_ebook(request.user, ebook)
    if not can_access:
        if not request.user.is_authenticated:
            messages.info(request, "Please sign in or use a quick demo login to read this e-book.")
            return redirect_to_login(request.get_full_path())
        if reason == "PAYMENT_REQUIRED":
            return redirect('ebooks:unlock', ebook_id=ebook.id)
        messages.error(request, reason)
        return redirect('ebooks:catalog')
        
    # Log the reading access if authenticated
    if request.user.is_authenticated:
        services.log_ebook_access(request.user, ebook, 'READ', get_client_ip(request))
    
    context = {
        'ebook': ebook,
        'stream_url': f"/ebooks/{ebook.id}/stream/",
    }
    return render(request, 'ebooks/ebook_reader.html', context)


import uuid

@login_required
def ebook_unlock_view(request, ebook_id):
    """Render and process affordable digital pass payment."""
    ebook = get_object_or_404(EBookMetadata.objects.select_related('book'), id=ebook_id)
    
    if is_librarian(request.user):
        return redirect('ebooks:read', ebook_id=ebook.id)

    from .models import EBookPass
    existing_pass = EBookPass.objects.filter(user=request.user, ebook=ebook, is_active=True).first()
    if existing_pass:
        return redirect('ebooks:read', ebook_id=ebook.id)

    if request.method == 'POST':
        tx_id = f"PASS-{uuid.uuid4().hex[:12].upper()}"
        EBookPass.objects.create(
            user=request.user,
            ebook=ebook,
            amount_paid=ebook.rental_price,
            transaction_id=tx_id,
            payment_method='UPI Instant Pass'
        )
        
        # Create notification
        from notifications.services import create_notification
        create_notification(
            user=request.user,
            title="E-Book Pass Unlocked",
            message=f"Successfully purchased digital reading pass (₹{ebook.rental_price}) for '{ebook.book.title}'. Transaction ID: {tx_id}",
            type='SUCCESS',
            link=f"/ebooks/{ebook.id}/read/"
        )

        messages.success(request, f"Reading pass unlocked successfully! Enjoy reading '{ebook.book.title}'.")
        return redirect('ebooks:read', ebook_id=ebook.id)

    return render(request, 'ebooks/ebook_unlock.html', {'ebook': ebook})



from django.views.decorators.clickjacking import xframe_options_sameorigin

@xframe_options_sameorigin
def ebook_stream_view(request, ebook_id):
    """Serves inline binary/HTML stream directly to embedded viewer."""
    ebook = get_object_or_404(EBookMetadata, id=ebook_id)
    
    can_access, reason = can_user_access_ebook(request.user, ebook)
    if not can_access:
        return HttpResponseForbidden(f"Access denied: {reason}")
        
    try:
        file_path = services.get_protected_file_path(ebook)
        is_html = ebook.format == 'HTML' or str(file_path).endswith('.html') or str(file_path).endswith('.htm')
        content_type = 'text/html; charset=utf-8' if is_html else 'application/pdf'
        default_ext = '.html' if is_html else '.pdf'
        
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{ebook.original_file_name or "ebook" + default_ext}"'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
    except FileNotFoundError:
        raise Http404("Protected e-book file not found on server storage.")



@login_required
def ebook_download_view(request, ebook_id):
    """Handles protected file download for PDF or HTML files."""
    ebook = get_object_or_404(EBookMetadata.objects.select_related('book'), id=ebook_id)
    
    can_access, reason = can_user_access_ebook(request.user, ebook)
    if not can_access:
        if reason == "PAYMENT_REQUIRED":
            return redirect('ebooks:unlock', ebook_id=ebook.id)
        messages.error(request, reason)
        return redirect('ebooks:catalog')

        
    if ebook.access_mode != 'READ_AND_DOWNLOAD':
        messages.error(request, "This e-book is read-only and cannot be downloaded.")
        return redirect('ebooks:detail', ebook_id=ebook.id)
        
    try:
        file_path = services.get_protected_file_path(ebook)
        is_html = ebook.format == 'HTML' or str(file_path).endswith('.html') or str(file_path).endswith('.htm')
        content_type = 'text/html; charset=utf-8' if is_html else 'application/pdf'
        default_ext = '.html' if is_html else '.pdf'
        
        # Log download access
        services.log_ebook_access(request.user, ebook, 'DOWNLOAD', get_client_ip(request))
        
        download_filename = ebook.original_file_name or f"{ebook.book.title}{default_ext}"
        response = FileResponse(open(file_path, 'rb'), content_type=content_type, as_attachment=True, filename=download_filename)
        return response
    except FileNotFoundError:
        messages.error(request, "E-book file not found on server storage.")
        return redirect('ebooks:detail', ebook_id=ebook.id)



@librarian_required
def ebook_manage_view(request):
    """Librarian management dashboard for e-books."""
    q = request.GET.get('q', '')
    rights_status = request.GET.get('rights', '')
    access_mode = request.GET.get('mode', '')
    active_status = request.GET.get('active', '')
    
    ebooks = EBookMetadata.objects.select_related('book', 'book__category', 'uploaded_by').annotate(
        read_count=Count('access_logs', filter=Q(access_logs__action='READ')),
        download_count=Count('access_logs', filter=Q(access_logs__action='DOWNLOAD'))
    ).order_by('-uploaded_at')
    
    if q:
        ebooks = ebooks.filter(
            Q(book__title__icontains=q) |
            Q(original_file_name__icontains=q)
        )
        
    if rights_status:
        ebooks = ebooks.filter(rights_status=rights_status)
        
    if access_mode:
        ebooks = ebooks.filter(access_mode=access_mode)
        
    if active_status == 'true':
        ebooks = ebooks.filter(is_active=True)
    elif active_status == 'false':
        ebooks = ebooks.filter(is_active=False)
        
    # Stats cards
    total_ebooks = EBookMetadata.objects.count()
    active_ebooks = EBookMetadata.objects.filter(is_active=True).count()
    total_reads = EBookAccessLog.objects.filter(action='READ').count()
    total_downloads = EBookAccessLog.objects.filter(action='DOWNLOAD').count()
    
    most_read = EBookMetadata.objects.annotate(
        total_accesses=Count('access_logs')
    ).filter(total_accesses__gt=0).order_by('-total_accesses')[:5]
    
    page_number = request.GET.get('page', 1)
    paginator = Paginator(ebooks, 25)
    page_obj = paginator.get_page(page_number)

    context = {
        'ebooks': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'total_ebooks': total_ebooks,
        'active_ebooks': active_ebooks,
        'total_reads': total_reads,
        'total_downloads': total_downloads,
        'most_read': most_read,
        'q': q,
        'selected_rights': rights_status,
        'selected_mode': access_mode,
        'selected_active': active_status,
        'rights_choices': EBookMetadata.RIGHTS_STATUS_CHOICES,
        'mode_choices': EBookMetadata.ACCESS_MODE_CHOICES,
    }
    return render(request, 'ebooks/ebook_manage.html', context)


@librarian_required
def ebook_revalidate_view(request, ebook_id):
    """Admin action to re-verify or regenerate an e-book document on disk."""
    ebook = get_object_or_404(EBookMetadata.objects.select_related('book', 'book__category'), id=ebook_id)
    book = ebook.book
    protected_root = Path(getattr(settings, 'PROTECTED_EBOOK_ROOT', settings.BASE_DIR / 'protected_ebooks'))
    
    if not ebook.protected_filename:
        ebook.protected_filename = f"{uuid.uuid4().hex}.html"
        ebook.save(update_fields=['protected_filename'])
        
    fpath = protected_root / ebook.protected_filename
    
    first_author = book.authors.first() if hasattr(book, 'authors') else None
    first_author_name = first_author.full_name if first_author else 'Unknown Author'
    category_name = book.category.name if book.category else 'General'

    from .kaggle_service import KaggleEBookService
    book_info = {
        'title': book.title,
        'subtitle': getattr(book, 'subtitle', '') or '',
        'author': first_author_name,
        'category': category_name,
        'publisher': book.publisher or 'Public Library Digital Collection',
        'publication_year': book.publication_year or 2024,
        'description': book.description or f"Complete digital edition of {book.title}.",
        'isbn': book.isbn or '',
        'pages': ebook.page_count or 300,
        'average_rating': 4.5,
    }

    try:
        doc_html, authentic_pages = KaggleEBookService._generate_reader_document(book_info)
        encoded = doc_html.encode('utf-8')
        with open(fpath, 'wb') as f:
            f.write(encoded)
        ebook.file_size = len(encoded)
        ebook.format = 'HTML'
        ebook.page_count = authentic_pages
        ebook.save(update_fields=['file_size', 'format', 'page_count'])
        messages.success(request, f"E-Book '{book.title}' successfully verified and synchronized ({authentic_pages} pages).")
    except Exception as e:
        messages.error(request, f"Failed to re-validate '{book.title}': {e}")
        
    return redirect('ebooks:manage')


@librarian_required
def ebook_upload_view(request):
    """Upload page for Librarians/Admins."""
    if request.method == 'POST':
        form = EBookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                target_book = form.cleaned_data.get('book')
                manual_title = form.cleaned_data.get('manual_title')

                if not target_book and manual_title:
                    import random
                    title_clean = manual_title.strip()
                    target_book = Book.objects.filter(title__iexact=title_clean).first()
                    if not target_book:
                        cat = Category.objects.filter(is_active=True).first()
                        if not cat:
                            cat = Category.objects.create(name='Digital Books', description='Digital & E-Book Library Collection')
                        isbn = f"978{random.randint(100000999, 999999999)}"
                        target_book = Book.objects.create(
                            title=title_clean,
                            isbn=isbn,
                            category=cat,
                            book_type='EBOOK',
                            description=f"Digital E-Book: {title_clean}"
                        )

                ebook = services.validate_and_save_ebook(
                    file_obj=request.FILES['file'],
                    book=target_book,
                    uploaded_by=request.user,
                    access_mode=form.cleaned_data['access_mode'],
                    rights_status=form.cleaned_data['rights_status'],
                    rights_text=form.cleaned_data['rights_text'],
                    access_note=form.cleaned_data.get('access_note', '')
                )
                # Save rental price
                ebook.rental_price = form.cleaned_data.get('rental_price', 0)
                ebook.save(update_fields=['rental_price'])
                messages.success(request, f"E-Book for '{ebook.book.title}' uploaded successfully ({ebook.page_count} pages).")
                return redirect('ebooks:manage')
            except ValueError as e:
                messages.error(request, str(e))

    else:
        form = EBookUploadForm()
        
    return render(request, 'ebooks/ebook_upload.html', {'form': form})


@librarian_required
def ebook_edit_view(request, ebook_id):
    """Edit metadata & replace file for Librarians/Admins."""
    ebook = get_object_or_404(EBookMetadata.objects.select_related('book'), id=ebook_id)
    
    if request.method == 'POST':
        form = EBookEditForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                rental_price = form.cleaned_data.get('rental_price', 0)
                if request.FILES.get('file'):
                    updated_ebook = services.validate_and_save_ebook(
                        file_obj=request.FILES['file'],
                        book=ebook.book,
                        uploaded_by=request.user,
                        access_mode=form.cleaned_data['access_mode'],
                        rights_status=form.cleaned_data['rights_status'],
                        rights_text=form.cleaned_data['rights_text'],
                        access_note=form.cleaned_data.get('access_note', ''),
                        existing_ebook=ebook
                    )
                    updated_ebook.rental_price = rental_price
                    updated_ebook.save(update_fields=['rental_price'])
                else:
                    services.update_ebook_metadata_only(
                        ebook=ebook,
                        access_mode=form.cleaned_data['access_mode'],
                        rights_status=form.cleaned_data['rights_status'],
                        rights_text=form.cleaned_data['rights_text'],
                        access_note=form.cleaned_data.get('access_note', ''),
                        is_active=form.cleaned_data.get('is_active', True),
                        rental_price=rental_price
                    )
                messages.success(request, f"E-Book '{ebook.book.title}' updated successfully.")
                return redirect('ebooks:manage')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = EBookEditForm(initial={
            'access_mode': ebook.access_mode,
            'rental_price': ebook.rental_price,
            'rights_status': ebook.rights_status,
            'rights_text': ebook.rights_text,
            'access_note': ebook.access_note,
            'is_active': ebook.is_active,
        })
        
    return render(request, 'ebooks/ebook_edit.html', {'form': form, 'ebook': ebook})


@librarian_required
def ebook_deactivate_view(request, ebook_id):
    """Toggles active/inactive status of an e-book."""
    ebook = get_object_or_404(EBookMetadata, id=ebook_id)
    if request.method == 'POST':
        ebook.is_active = not ebook.is_active
        ebook.save()
        status_str = "activated" if ebook.is_active else "deactivated"
        messages.success(request, f"E-Book '{ebook.book.title}' has been {status_str}.")
    return redirect('ebooks:manage')


@login_required
def member_reading_history_view(request):
    """Personal e-book access history for members."""
    logs = EBookAccessLog.objects.filter(user=request.user).select_related('ebook', 'ebook__book').order_by('-accessed_at')
    return render(request, 'ebooks/reading_history.html', {'logs': logs})


@librarian_required
def ebook_usage_report_view(request):
    """Detailed e-book usage report for Librarians/Admins."""
    logs = EBookAccessLog.objects.select_related('user', 'ebook', 'ebook__book').order_by('-accessed_at')[:100]
    
    top_read_ebooks = EBookMetadata.objects.annotate(
        read_count=Count('access_logs', filter=Q(access_logs__action='READ')),
        download_count=Count('access_logs', filter=Q(access_logs__action='DOWNLOAD'))
    ).order_by('-read_count')[:10]
    
    context = {
        'logs': logs,
        'top_read_ebooks': top_read_ebooks,
    }
    return render(request, 'ebooks/usage_report.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .open_source import OpenSourceEBookService

@librarian_required
def open_source_discovery_view(request):
    """Librarian & Admin console for searching and importing open-source public domain e-books."""
    q = request.GET.get('q', '').strip()
    topic = request.GET.get('topic', '').strip()
    
    if q or topic:
        books = OpenSourceEBookService.fetch_from_gutendex(search_query=q, topic=topic)
    else:
        books = OpenSourceEBookService.get_curated_classics()
        
    context = {
        'books': books,
        'q': q,
        'selected_topic': topic,
        'total_count': len(books),
    }
    return render(request, 'ebooks/open_source_discovery.html', context)


@librarian_required
@require_POST
def import_open_source_book_api(request):
    """API endpoint to 1-click import an open-source book into the library catalog."""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload'}, status=400)

    gutenberg_id = data.get('gutenberg_id')
    book_id_str = data.get('id', '')
    
    # Try finding in curated list
    classics = OpenSourceEBookService.get_curated_classics()
    target = None
    for c in classics:
        if str(c.get('gutenberg_id')) == str(gutenberg_id) or c.get('id') == book_id_str:
            target = c
            break
            
    # If not in curated classics, check live Gutendex
    if not target:
        results = OpenSourceEBookService.fetch_from_gutendex(search_query=data.get('title', ''))
        for r in results:
            if str(r.get('gutenberg_id')) == str(gutenberg_id):
                target = r
                break

    if not target:
        target = data  # fallback to payload if metadata provided

    try:
        book, was_created = OpenSourceEBookService.import_book_to_catalog(target, uploaded_by=request.user)
        return JsonResponse({
            'success': True,
            'book_id': book.id,
            'ebook_id': book.ebook_metadata.id if hasattr(book, 'ebook_metadata') else None,
            'title': book.title,
            'was_created': was_created,
            'message': f"'{book.title}' is ready in the library catalog!"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def ebook_commons_view(request):
    """
    Open Access Digital Commons portal for members and visitors.
    Lists free, unlimited public-domain classics with zero queue times and instant browser reading.
    """
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()

    category_obj = Category.resolve(category_id) if category_id else None
    selected_category = str(category_obj.id) if category_obj else (category_id if category_id.isdigit() else '')

    ebooks = EBookMetadata.objects.filter(
        rights_status='PUBLIC_DOMAIN',
        is_active=True
    ).select_related('book', 'book__category').prefetch_related('book__authors')

    if q:
        ebooks = ebooks.filter(
            Q(book__title__icontains=q) |
            Q(book__authors__full_name__icontains=q) |
            Q(book__description__icontains=q)
        ).distinct()

    if category_obj:
        ebooks = ebooks.filter(book__category=category_obj)
    elif category_id and category_id.isdigit():
        ebooks = ebooks.filter(book__category_id=int(category_id))
    elif category_id:
        ebooks = ebooks.filter(book__category__name__icontains=category_id)

    categories = Category.objects.filter(
        books__ebook_metadata__rights_status='PUBLIC_DOMAIN'
    ).distinct().order_by('name')

    context = {
        'ebooks': ebooks,
        'categories': categories,
        'q': q,
        'selected_category': selected_category,
        'total_count': ebooks.count(),
    }
    return render(request, 'ebooks/commons.html', context)


# ── Pillar 3: In-Reader Highlights & Annotation APIs ──────────────────────────

from .models import EBookAnnotation


@login_required
@require_POST
def api_add_annotation(request, ebook_id):
    """Save a patron text highlight and marginalia note for an e-book."""
    ebook = get_object_or_404(EBookMetadata, id=ebook_id)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data.'}, status=400)

    selected_text = data.get('selected_text', '').strip()
    note = data.get('note', '').strip()
    color = data.get('color', 'yellow')
    chapter_title = data.get('chapter_title', '')

    if not selected_text:
        return JsonResponse({'success': False, 'error': 'Selected text cannot be empty.'}, status=400)

    annotation = EBookAnnotation.objects.create(
        user=request.user,
        ebook=ebook,
        selected_text=selected_text,
        note=note,
        color=color if color in ['yellow', 'green', 'pink', 'blue'] else 'yellow',
        chapter_title=chapter_title,
    )

    return JsonResponse({
        'success': True,
        'annotation': {
            'id': annotation.id,
            'selected_text': annotation.selected_text,
            'note': annotation.note,
            'color': annotation.color,
            'chapter_title': annotation.chapter_title,
            'created_at': annotation.created_at.strftime('%b %d, %Y %I:%M %p'),
        }
    })


@login_required
def api_list_annotations(request, ebook_id):
    """Retrieve all highlights and notes saved by current patron for an e-book."""
    ebook = get_object_or_404(EBookMetadata, id=ebook_id)
    annotations = EBookAnnotation.objects.filter(user=request.user, ebook=ebook).order_by('-created_at')

    return JsonResponse({
        'success': True,
        'annotations': [
            {
                'id': a.id,
                'selected_text': a.selected_text,
                'note': a.note,
                'color': a.color,
                'chapter_title': a.chapter_title,
                'created_at': a.created_at.strftime('%b %d, %Y %I:%M %p'),
            }
            for a in annotations
        ]
    })


@login_required
@require_POST
def api_delete_annotation(request, annotation_id):
    """Delete a patron annotation."""
    annotation = get_object_or_404(EBookAnnotation, id=annotation_id, user=request.user)
    annotation.delete()
    return JsonResponse({'success': True, 'message': 'Annotation removed.'})


from pathlib import Path
from django.conf import settings
from .kaggle_service import KaggleEBookService


@librarian_required
def kaggle_import_view(request):
    """Librarian & Admin portal for importing books from Kaggle datasets."""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'import_curated':
            csv_path = Path(settings.BASE_DIR) / 'data' / 'kaggle_books.csv'
            if not csv_path.exists():
                messages.error(request, "Default Kaggle dataset 'data/kaggle_books.csv' was not found.")
            else:
                stats = KaggleEBookService.import_from_csv(
                    csv_path,
                    uploaded_by=request.user,
                    access_mode='READ_AND_DOWNLOAD',
                    rights_status='LIBRARY_LICENSED',
                    overwrite=True
                )
                messages.success(
                    request,
                    f"Successfully ingested curated Kaggle collection: {stats['imported']} imported, {stats['skipped']} skipped."
                )
            return redirect('ebooks:kaggle_import')

        elif action == 'upload_csv':
            csv_file = request.FILES.get('csv_file')
            if not csv_file or not csv_file.name.lower().endswith('.csv'):
                messages.error(request, "Please upload a valid .csv dataset file.")
                return redirect('ebooks:kaggle_import')

            overwrite = request.POST.get('overwrite') == 'on'
            mode = request.POST.get('access_mode', 'READ_AND_DOWNLOAD')
            rights = request.POST.get('rights_status', 'LIBRARY_LICENSED')

            try:
                batch_limit = int(request.POST.get('batch_limit', 50))
            except (ValueError, TypeError):
                batch_limit = 50
            batch_limit = max(1, min(batch_limit, 100))

            try:
                stats = KaggleEBookService.import_from_csv(
                    csv_file,
                    limit=batch_limit,
                    uploaded_by=request.user,
                    access_mode=mode,
                    rights_status=rights,
                    overwrite=overwrite
                )
                if stats.get('imported', 0) > 0 or stats.get('updated', 0) > 0:
                    messages.success(
                        request,
                        f"Kaggle CSV Ingestion Complete: {stats['imported']} new books added, {stats.get('updated', 0)} existing books updated, {stats['skipped']} skipped/existing ({min(stats['total_rows'], batch_limit)} rows processed)."
                    )
                else:
                    messages.info(
                        request,
                        f"All {stats['skipped']} books in this CSV batch are already cataloged in your library! "
                        f"They were skipped to prevent duplicate records. If you wish to update them with new data from your CSV, check 'Update existing books if ISBN matches' below and click upload."
                    )
            except Exception as e:
                messages.error(request, f"Error processing Kaggle CSV: {str(e)}")
            return redirect('ebooks:kaggle_import')

    # GET
    kaggle_ebooks = EBookMetadata.objects.filter(
        Q(rights_text__icontains='Kaggle') | Q(access_note__icontains='Kaggle')
    ).select_related('book', 'book__category').prefetch_related('book__authors').order_by('-id')

    total_kaggle = kaggle_ebooks.count()
    categories_count = Category.objects.filter(books__in=kaggle_ebooks.values('book')).distinct().count()

    context = {
        'kaggle_ebooks': kaggle_ebooks[:100],
        'total_kaggle': total_kaggle,
        'categories_count': categories_count,
        'total_ebooks': EBookMetadata.objects.filter(is_active=True).count(),
    }
    return render(request, 'ebooks/kaggle_import.html', context)

