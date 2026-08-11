from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Book, Category

def catalog_list_view(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    book_type = request.GET.get('type', '')
    
    books = Book.objects.filter(is_active=True).select_related('category').prefetch_related('authors', 'copies')
    
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(authors__full_name__icontains=query) |
            Q(isbn__icontains=query)
        ).distinct()
        
    if category_id:
        books = books.filter(category_id=category_id)
        
    if book_type:
        books = books.filter(book_type=book_type)
        
    # Ordering
    books = books.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'selected_type': book_type,
    }
    return render(request, 'catalog/book_list.html', context)

def book_detail_view(request, book_id):
    book = get_object_or_404(Book.objects.select_related('category').prefetch_related('authors'), pk=book_id, is_active=True)
    available_physical_copies = book.copies.filter(status='AVAILABLE').count()
    total_physical_copies = book.copies.count()
    
    context = {
        'book': book,
        'available_physical_copies': available_physical_copies,
        'total_physical_copies': total_physical_copies,
    }
    return render(request, 'catalog/book_detail.html', context)
