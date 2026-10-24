from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

import json
from .models import Book, Category
from .ai_services import AIAssistantEngine


def catalog_list_view(request):
    query = request.GET.get('q', '').strip()
    category_param = request.GET.get('category', '').strip()
    book_type = request.GET.get('type', '')
    sort_by = request.GET.get('sort', 'newest')
    avail_filter = request.GET.get('avail', '')
    search_mode = request.GET.get('mode', '')

    category_obj = Category.resolve(category_param) if category_param else None
    selected_category = str(category_obj.id) if category_obj else (category_param if category_param.isdigit() else '')

    is_semantic = (search_mode == 'semantic' and query)

    if is_semantic:
        # ── Semantic AI Search Mode ──
        ranked = AIAssistantEngine.rank_catalog_books(
            query,
            category_id=category_obj.id if category_obj else (int(category_param) if category_param.isdigit() else None),
            book_type=book_type or None,
            avail_only=(avail_filter == 'available'),
        )
        # ranked is list of (book, score%, passage)
        books_with_scores = []
        for book, score, passage in ranked:
            copies = book.copies.all()
            book.available_copies_count = sum(1 for c in copies if c.status == 'AVAILABLE')
            book.total_copies_count = len(copies)
            book.has_ebook_access = hasattr(book, 'ebook_metadata') and book.ebook_metadata and book.ebook_metadata.is_active
            book.semantic_score = score
            book.relevant_passage = passage
            books_with_scores.append(book)

        paginator = Paginator(books_with_scores, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        total_results = len(books_with_scores)
    else:
        # ── Standard Database Search Mode ──
        books = Book.objects.filter(is_active=True).select_related('category', 'ebook_metadata').prefetch_related('authors', 'copies')

        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(authors__full_name__icontains=query) |
                Q(isbn__icontains=query) |
                Q(description__icontains=query)
            ).distinct()

        if category_obj:
            books = books.filter(category=category_obj)
        elif category_param and category_param.isdigit():
            books = books.filter(category_id=int(category_param))
        elif category_param:
            books = books.filter(category__name__icontains=category_param)

        if book_type:
            books = books.filter(book_type=book_type)

        if avail_filter == 'available':
            books = books.filter(
                Q(copies__status='AVAILABLE') | Q(book_type__in=['EBOOK', 'BOTH'], ebook_metadata__is_active=True)
            ).distinct()

        # Ordering
        if sort_by == 'title':
            books = books.order_by('title')
        elif sort_by == 'year':
            books = books.order_by('-publication_year', '-created_at')
        else:
            books = books.order_by('-created_at')

        # Pagination
        paginator = Paginator(books, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        total_results = paginator.count

        # Pre-calculate copy availability for cards
        for book in page_obj:
            copies = book.copies.all()
            book.available_copies_count = sum(1 for c in copies if c.status == 'AVAILABLE')
            book.total_copies_count = len(copies)
            book.has_ebook_access = hasattr(book, 'ebook_metadata') and book.ebook_metadata and book.ebook_metadata.is_active

    categories = Category.objects.filter(is_active=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': selected_category,
        'selected_type': book_type,
        'selected_sort': sort_by,
        'selected_avail': avail_filter,
        'selected_mode': search_mode,
        'is_semantic': is_semantic,
        'total_results': total_results,
    }
    return render(request, 'catalog/book_list.html', context)


def book_detail_view(request, book_id):
    book = get_object_or_404(Book.objects.select_related('category').prefetch_related('authors', 'copies'), pk=book_id, is_active=True)
    copies = list(book.copies.all())
    available_physical_copies = sum(1 for c in copies if c.status == 'AVAILABLE')
    total_physical_copies = len(copies)

    from reservations import services as res_services
    avail_info = res_services.estimate_availability_for_book(book)

    user_reservation = None
    user_has_loan = False
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        from reservations.models import Reservation
        from circulation.models import Loan
        user_reservation = Reservation.objects.filter(
            member=request.user.profile,
            book=book,
            status__in=['PENDING', 'ALLOCATED']
        ).first()
        if user_reservation:
            user_reservation.queue_info = res_services.get_queue_info(user_reservation)

        user_has_loan = Loan.objects.filter(
            member=request.user.profile,
            book_copy__book=book,
            status='ISSUED'
        ).exists()

    # Related Books in same category
    related_books = Book.objects.filter(
        category=book.category, is_active=True
    ).exclude(id=book.id).prefetch_related('authors')[:4]

    # Reviews & Ratings
    from .models import BookReview, UserBookList
    reviews = book.reviews.filter(is_approved=True).select_related('user').order_by('-created_at')
    user_review = None
    user_shelves = []
    
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        user_shelves = list(UserBookList.objects.filter(user=request.user, book=book).values_list('shelf_type', flat=True))

    total_reviews = reviews.count()
    rating_histogram = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        if r.rating in rating_histogram:
            rating_histogram[r.rating] += 1
            
    rating_percentages = {}
    for stars, cnt in rating_histogram.items():
        rating_percentages[stars] = round((cnt / total_reviews * 100)) if total_reviews > 0 else 0

    context = {
        'book': book,
        'copies': copies,
        'available_physical_copies': available_physical_copies,
        'total_physical_copies': total_physical_copies,
        'avail_info': avail_info,
        'user_reservation': user_reservation,
        'user_has_loan': user_has_loan,
        'related_books': related_books,
        'reviews': reviews,
        'user_review': user_review,
        'user_shelves': user_shelves,
        'total_reviews': total_reviews,
        'rating_percentages': rating_percentages,
    }
    return render(request, 'catalog/book_detail.html', context)


@login_required
@require_POST
def add_book_review_view(request, book_id):
    """Submits or updates a patron rating and review."""
    from .models import BookReview
    book = get_object_or_404(Book, pk=book_id)
    
    try:
        rating = int(request.POST.get('rating', 5))
        rating = min(5, max(1, rating))
    except (ValueError, TypeError):
        rating = 5
        
    headline = request.POST.get('headline', '').strip()[:150]
    review_text = request.POST.get('review_text', '').strip()
    
    if not review_text:
        messages.error(request, "Please enter review comments before submitting.")
        return redirect('catalog:detail', book_id=book.id)
        
    review, created = BookReview.objects.update_or_create(
        book=book,
        user=request.user,
        defaults={
            'rating': rating,
            'headline': headline,
            'review_text': review_text,
            'is_approved': True,
        }
    )
    
    try:
        from core.models import log_activity
        log_activity('REVIEW_POSTED', f"Rated '{book.title}' {rating}★: {headline or 'No headline'}", user=request.user, request=request)
    except Exception:
        pass

    action = "submitted" if created else "updated"
    messages.success(request, f"Thank you! Your {rating}★ review has been {action}.")
    return redirect('catalog:detail', book_id=book.id)



@login_required
@require_POST
def toggle_bookshelf_api(request):
    """AJAX endpoint to add or remove a book from patron's bookshelf."""
    from .models import UserBookList
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        
    book_id = data.get('book_id')
    shelf_type = data.get('shelf_type', 'WANT_TO_READ')
    
    book = get_object_or_404(Book, pk=book_id)
    existing = UserBookList.objects.filter(user=request.user, book=book, shelf_type=shelf_type).first()
    
    if existing:
        existing.delete()
        action = 'removed'
        message = f"Removed '{book.title}' from your {existing.get_shelf_type_display()} shelf."
    else:
        entry = UserBookList.objects.create(user=request.user, book=book, shelf_type=shelf_type)
        action = 'added'
        message = f"Added '{book.title}' to your {entry.get_shelf_type_display()} shelf."
        
    return JsonResponse({
        'success': True,
        'action': action,
        'shelf_type': shelf_type,
        'message': message,
    })


@login_required
def my_bookshelf_view(request):
    """Personal Bookshelf / Reading Lists portal for members."""
    from .models import UserBookList
    entries = UserBookList.objects.filter(user=request.user).select_related('book', 'book__category').prefetch_related('book__authors').order_by('-added_at')
    
    shelves = {
        'WANT_TO_READ': entries.filter(shelf_type='WANT_TO_READ'),
        'CURRENTLY_READING': entries.filter(shelf_type='CURRENTLY_READING'),
        'FAVORITES': entries.filter(shelf_type='FAVORITES'),
        'COMPLETED': entries.filter(shelf_type='COMPLETED'),
    }
    
    active_tab = request.GET.get('tab', 'WANT_TO_READ')
    
    context = {
        'shelves': shelves,
        'active_tab': active_tab,
        'total_saved': entries.count(),
    }
    return render(request, 'catalog/my_bookshelf.html', context)



@login_required
def ai_assistant_view(request):
    """Render the AI Knowledge Assistant glassmorphic chat interface."""
    return render(request, 'catalog/ai_assistant.html')


@login_required
@require_POST
def ai_assistant_api(request):
    """API Endpoint: Processes natural language RAG queries and returns JSON response with citations."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        query = data.get('query', '')
    except (json.JSONDecodeError, UnicodeDecodeError):
        query = request.POST.get('query', '')

    result = AIAssistantEngine.search_and_generate_response(query)
    return JsonResponse(result)


def semantic_search_api(request):
    """GET API for global ⌘K semantic search modal. Returns JSON with RAG answer + citations."""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({
            'answer': '',
            'citations': [],
            'suggested_questions': [
                'What books are available on Technology or AI?',
                'Which e-books can I read online immediately?',
                'Recommend books about artificial intelligence.',
            ],
        })
    result = AIAssistantEngine.search_and_generate_response(query)
    return JsonResponse(result)


# ── Librarian Catalog Management ──────────────────────────────────────────────

def _is_librarian(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_librarian()


@login_required
def book_create_view(request):
    """Librarian: Add a new book to the catalogue."""
    if not _is_librarian(request.user):
        messages.error(request, "Permission denied. Librarian access required.")
        return redirect('catalog:list')

    from .forms import BookForm
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            try:
                from core.models import log_activity
                log_activity('BOOK_ADDED', f"Added '{book.title}' (ISBN: {book.isbn}) to catalogue", user=request.user, request=request)
            except Exception:
                pass
            messages.success(request, f"'{book.title}' has been added to the catalogue.")
            return redirect('catalog:detail', book_id=book.id)
    else:
        form = BookForm()

    return render(request, 'catalog/book_form.html', {'form': form, 'is_edit': False, 'form_title': 'Add New Book to Catalogue'})


@login_required
def book_edit_view(request, book_id):
    """Librarian: Edit an existing book's metadata."""
    if not _is_librarian(request.user):
        messages.error(request, "Permission denied. Librarian access required.")
        return redirect('catalog:list')

    book = get_object_or_404(Book, pk=book_id)
    from .forms import BookForm
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            try:
                from core.models import log_activity
                log_activity('BOOK_EDITED', f"Updated catalogue entry for '{book.title}'", user=request.user, request=request)
            except Exception:
                pass
            messages.success(request, f"'{book.title}' has been updated.")
            return redirect('catalog:detail', book_id=book.id)
    else:
        form = BookForm(instance=book)

    return render(request, 'catalog/book_form.html', {'form': form, 'book': book, 'is_edit': True, 'form_title': f'Edit: {book.title}'})


@login_required
def add_book_copy_view(request, book_id):
    """Librarian: Add a new physical copy to an existing book."""
    if not _is_librarian(request.user):
        messages.error(request, "Permission denied. Librarian access required.")
        return redirect('catalog:list')

    book = get_object_or_404(Book, pk=book_id)
    from .forms import BookCopyForm
    if request.method == 'POST':
        form = BookCopyForm(request.POST)
        if form.is_valid():
            copy = form.save(commit=False)
            copy.book = book
            copy.save()
            try:
                from core.models import log_activity
                log_activity('COPY_ADDED', f"Added copy {copy.accession_number} for '{book.title}'", user=request.user, request=request)
            except Exception:
                pass
            messages.success(request, f"New copy ({copy.accession_number}) added for '{book.title}'.")
            return redirect('catalog:detail', book_id=book.id)
    else:
        form = BookCopyForm()

    return render(request, 'catalog/book_form.html', {
        'form': form,
        'book': book,
        'is_edit': False,
        'is_copy': True,
        'form_title': f'Add Physical Copy — {book.title}'
    })

