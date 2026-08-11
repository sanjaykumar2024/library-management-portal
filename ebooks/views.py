from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponseForbidden, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from catalog.models import Book, Category, EBookMetadata
from .models import EBookAccessLog
from .forms import EBookUploadForm, EBookEditForm
from . import services

def is_librarian(user):
    return user.is_authenticated and (user.profile.is_librarian() or user.profile.is_admin())

def can_user_access_ebook(user, ebook):
    """
    Checks if a user is permitted to view/read/download an e-book.
    Must be authenticated and an active member, librarian, or admin.
    Enforces maximum concurrent reader capacity.
    """
    if not user.is_authenticated:
        return False, "Authentication required to access e-books."
        
    if is_librarian(user):
        return True, ""
        
    # Regular member check
    profile = getattr(user, 'profile', None)
    if not profile or profile.membership_status != 'ACTIVE':
        return False, "Active library membership is required to access e-books."
        
    if not ebook.is_active:
        return False, "This e-book is currently inactive or unavailable."
        
    # Check concurrent reader limit (15 min active window)
    if ebook.max_concurrent_readers > 0:
        from django.utils import timezone
        import datetime
        recent_window = timezone.now() - datetime.timedelta(minutes=15)
        active_readers_count = ebook.access_logs.filter(
            action='READ',
            accessed_at__gte=recent_window
        ).values('user').distinct().count()

        # If user is not already in active readers list and capacity is reached
        already_reading = ebook.access_logs.filter(
            user=user, action='READ', accessed_at__gte=recent_window
        ).exists()
        
        if not already_reading and active_readers_count >= ebook.max_concurrent_readers:
            return False, f"All {ebook.max_concurrent_readers} simultaneous reader licenses for this e-book are currently in use. Please try again shortly."

    return True, ""


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def ebook_catalog_view(request):
    """Public/Member E-Book catalogue with search and filtering."""
    q = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    rights_status = request.GET.get('rights', '')
    access_mode = request.GET.get('mode', '')
    
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
        
    if category_id:
        ebooks = ebooks.filter(book__category_id=category_id)
        
    if rights_status:
        ebooks = ebooks.filter(rights_status=rights_status)
        
    if access_mode:
        ebooks = ebooks.filter(access_mode=access_mode)
        
    categories = Category.objects.all().order_by('name')
    
    context = {
        'ebooks': ebooks,
        'categories': categories,
        'q': q,
        'selected_category': category_id,
        'selected_rights': rights_status,
        'selected_mode': access_mode,
        'rights_choices': EBookMetadata.RIGHTS_STATUS_CHOICES,
        'mode_choices': EBookMetadata.ACCESS_MODE_CHOICES,
    }
    return render(request, 'ebooks/ebook_catalog.html', context)


@login_required
def ebook_detail_view(request, ebook_id):
    """Detailed view for a specific e-book."""
    ebook = get_object_or_404(EBookMetadata.objects.select_related('book', 'book__category', 'uploaded_by'), id=ebook_id)
    
    can_access, reason = can_user_access_ebook(request.user, ebook)
    if not can_access:
        messages.error(request, reason)
        return redirect('ebooks:catalog')
        
    # Read & download counts for Librarians/Admins only
    read_count = 0
    download_count = 0
    if is_librarian(request.user):
        read_count = ebook.access_logs.filter(action='READ').count()
        download_count = ebook.access_logs.filter(action='DOWNLOAD').count()
        
    context = {
        'ebook': ebook,
        'read_count': read_count,
        'download_count': download_count,
        'can_download': ebook.access_mode == 'READ_AND_DOWNLOAD',
    }
    return render(request, 'ebooks/ebook_detail.html', context)


@login_required
def ebook_read_view(request, ebook_id):
    """Online protected reader view."""
    ebook = get_object_or_404(EBookMetadata.objects.select_related('book'), id=ebook_id)
    
    can_access, reason = can_user_access_ebook(request.user, ebook)
    if not can_access:
        messages.error(request, reason)
        return redirect('ebooks:catalog')
        
    # Log the reading access
    services.log_ebook_access(request.user, ebook, 'READ', get_client_ip(request))
    
    context = {
        'ebook': ebook,
        'stream_url': f"/ebooks/{ebook.id}/stream/",
    }
    return render(request, 'ebooks/ebook_reader.html', context)


@login_required
def ebook_stream_view(request, ebook_id):
    """Serves inline PDF binary stream directly to embedded viewer."""
    ebook = get_object_or_404(EBookMetadata, id=ebook_id)
    
    can_access, reason = can_user_access_ebook(request.user, ebook)
    if not can_access:
        return HttpResponseForbidden(f"Access denied: {reason}")
        
    try:
        file_path = services.get_protected_file_path(ebook)
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{ebook.original_file_name or "ebook.pdf"}"'
        return response
    except FileNotFoundError:
        raise Http404("Protected PDF file not found on server storage.")


@login_required
def ebook_download_view(request, ebook_id):
    """Handles protected PDF file download."""
    ebook = get_object_or_404(EBookMetadata.objects.select_related('book'), id=ebook_id)
    
    can_access, reason = can_user_access_ebook(request.user, ebook)
    if not can_access:
        messages.error(request, reason)
        return redirect('ebooks:catalog')
        
    if ebook.access_mode != 'READ_AND_DOWNLOAD':
        messages.error(request, "This e-book is read-only and cannot be downloaded.")
        return redirect('ebooks:detail', ebook_id=ebook.id)
        
    try:
        file_path = services.get_protected_file_path(ebook)
        
        # Log download access
        services.log_ebook_access(request.user, ebook, 'DOWNLOAD', get_client_ip(request))
        
        download_filename = ebook.original_file_name or f"{ebook.book.title}.pdf"
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf', as_attachment=True, filename=download_filename)
        return response
    except FileNotFoundError:
        messages.error(request, "E-book file not found on server storage.")
        return redirect('ebooks:detail', ebook_id=ebook.id)


@login_required
@user_passes_test(is_librarian)
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
    
    context = {
        'ebooks': ebooks,
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


@login_required
@user_passes_test(is_librarian)
def ebook_upload_view(request):
    """Upload page for Librarians/Admins."""
    if request.method == 'POST':
        form = EBookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                ebook = services.validate_and_save_ebook(
                    file_obj=request.FILES['file'],
                    book=form.cleaned_data['book'],
                    uploaded_by=request.user,
                    access_mode=form.cleaned_data['access_mode'],
                    rights_status=form.cleaned_data['rights_status'],
                    rights_text=form.cleaned_data['rights_text'],
                    access_note=form.cleaned_data.get('access_note', '')
                )
                messages.success(request, f"E-Book for '{ebook.book.title}' uploaded successfully ({ebook.page_count} pages).")
                return redirect('ebooks:manage')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = EBookUploadForm()
        
    return render(request, 'ebooks/ebook_upload.html', {'form': form})


@login_required
@user_passes_test(is_librarian)
def ebook_edit_view(request, ebook_id):
    """Edit metadata & replace file for Librarians/Admins."""
    ebook = get_object_or_404(EBookMetadata.objects.select_related('book'), id=ebook_id)
    
    if request.method == 'POST':
        form = EBookEditForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                if request.FILES.get('file'):
                    services.validate_and_save_ebook(
                        file_obj=request.FILES['file'],
                        book=ebook.book,
                        uploaded_by=request.user,
                        access_mode=form.cleaned_data['access_mode'],
                        rights_status=form.cleaned_data['rights_status'],
                        rights_text=form.cleaned_data['rights_text'],
                        access_note=form.cleaned_data.get('access_note', ''),
                        existing_ebook=ebook
                    )
                else:
                    services.update_ebook_metadata_only(
                        ebook=ebook,
                        access_mode=form.cleaned_data['access_mode'],
                        rights_status=form.cleaned_data['rights_status'],
                        rights_text=form.cleaned_data['rights_text'],
                        access_note=form.cleaned_data.get('access_note', ''),
                        is_active=form.cleaned_data.get('is_active', True)
                    )
                messages.success(request, f"E-Book '{ebook.book.title}' updated successfully.")
                return redirect('ebooks:manage')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = EBookEditForm(initial={
            'access_mode': ebook.access_mode,
            'rights_status': ebook.rights_status,
            'rights_text': ebook.rights_text,
            'access_note': ebook.access_note,
            'is_active': ebook.is_active,
        })
        
    return render(request, 'ebooks/ebook_edit.html', {'form': form, 'ebook': ebook})


@login_required
@user_passes_test(is_librarian)
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


@login_required
@user_passes_test(is_librarian)
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
