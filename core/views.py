from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.utils import timezone

from accounts.models import UserProfile
from catalog.models import Book, BookCopy, EBookMetadata, Category
from circulation.models import Loan, Fine
from reservations.models import Reservation
from notifications.models import Notification
from ebooks.models import EBookAccessLog
from core.models import ActivityLog


def home_view(request):
    """
    Public Library Home Portal inspired by Open Library & National Digital Library of India (NDLI).
    Displays omni-search, 3 welcome feature cards, curated book shelves with real covers,
    subjects directory, and live community statistics.
    """
    # 1. Trending Books (active books with covers, top reviewed / recent)
    trending_books = Book.objects.filter(is_active=True).prefetch_related(
        'authors', 'copies'
    ).select_related('category', 'ebook_metadata').order_by('-id')[:10]

    # 2. Free Classic Books (Open-access / Public Domain digital commons)
    classic_books = Book.objects.filter(
        is_active=True,
        ebook_metadata__rights_status='PUBLIC_DOMAIN'
    ).prefetch_related('authors', 'copies').select_related('category', 'ebook_metadata')[:10]

    # 3. Technology & Computing Books (Kaggle dataset & Tech collection)
    tech_books = Book.objects.filter(
        is_active=True,
        category__name__in=['Technology', 'Science Fiction', 'Computer Science']
    ).prefetch_related('authors', 'copies').select_related('category', 'ebook_metadata')[:10]

    # 4. Books We Love / Curated Literature
    curated_books = Book.objects.filter(
        is_active=True,
        category__name__in=['Literature', 'Romance & Classic Fiction', 'History']
    ).prefetch_related('authors', 'copies').select_related('category', 'ebook_metadata')[:10]

    # 5. Active Categories with book counts
    categories = Category.objects.filter(is_active=True).annotate(
        book_count=Count('books')
    ).filter(book_count__gt=0).order_by('-book_count')[:14]

    # 6. Live "Around the Library" Statistics
    stats = {
        'total_books': Book.objects.filter(is_active=True).count(),
        'total_ebooks': EBookMetadata.objects.filter(is_active=True).count(),
        'total_copies': BookCopy.objects.filter(status='AVAILABLE').count(),
        'total_members': UserProfile.objects.filter(membership_status='ACTIVE').count(),
        'total_loans': Loan.objects.count(),
    }

    context = {
        'trending_books': trending_books,
        'classic_books': classic_books,
        'tech_books': tech_books,
        'curated_books': curated_books,
        'categories': categories,
        'stats': stats,
    }
    return render(request, 'core/home.html', context)


@login_required
def dashboard_redirect(request):
    if not hasattr(request.user, 'profile'):
        return redirect('core:member_dashboard') # Fallback
        
    role = request.user.profile.role
    if role == 'ADMIN':
        return redirect('core:admin_dashboard')
    elif role == 'LIBRARIAN':
        return redirect('core:librarian_dashboard')
    else:
        return redirect('core:member_dashboard')


@login_required
def member_dashboard_view(request):
    if hasattr(request.user, 'profile') and request.user.profile.role not in ['MEMBER', 'ADMIN', 'LIBRARIAN']:
        return redirect('core:home')
        
    today = timezone.now().date()
    profile = getattr(request.user, 'profile', None)
    
    my_active_loans = []
    overdue_loans = []
    my_active_reservations = []
    recent_notifications = []
    recent_ebook_access = []
    
    if profile:
        my_active_loans = Loan.objects.filter(
            member=profile, status='ISSUED'
        ).select_related('book_copy', 'book_copy__book').order_by('due_date')
        
        overdue_loans = [l for l in my_active_loans if l.due_date < today]
        
        my_active_reservations = list(Reservation.objects.filter(
            member=profile, status__in=['PENDING', 'ALLOCATED']
        ).select_related('book', 'allocated_copy').order_by('-reservation_date'))
        
        from reservations import services as res_services
        for r in my_active_reservations:
            r.queue_info = res_services.get_queue_info(r)
        
    recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    recent_ebook_access = EBookAccessLog.objects.filter(
        user=request.user
    ).select_related('ebook', 'ebook__book').order_by('-accessed_at')[:4]

    
    recommended_books = Book.objects.filter(is_active=True).prefetch_related('authors').order_by('-created_at')[:4]
    
    # Pillar 5: Gamification & Reading Challenge
    from catalog.models import ReadingChallenge, PatronBadge, award_badge
    reading_challenge, _ = ReadingChallenge.objects.get_or_create(
        user=request.user, year=today.year, defaults={'target_books': 12}
    )
    
    # Check automated badge unlocks
    if Loan.objects.filter(member=profile).exists():
        award_badge(request.user, 'FIRST_BORROW')
    if reading_challenge.completed_count >= 5:
        award_badge(request.user, 'BOOKWORM')
    if timezone.now().hour >= 22:
        award_badge(request.user, 'NIGHT_OWL')
        
    badges = list(request.user.badges.all())
    unlocked_types = {b.badge_type for b in badges}
    all_badge_types = [
        {'type': k, 'title': v[0], 'desc': v[1], 'icon': v[2], 'color': v[3], 'unlocked': k in unlocked_types}
        for k, v in PatronBadge.BADGE_INFO.items()
    ]

    context = {
        'today': today,
        'profile': profile,
        'my_active_loans': my_active_loans,
        'overdue_loans': overdue_loans,
        'has_overdue': len(overdue_loans) > 0,
        'my_active_reservations': my_active_reservations,
        'recent_notifications': recent_notifications,
        'recent_ebook_access': recent_ebook_access,
        'recommended_books': recommended_books,
        'reading_challenge': reading_challenge,
        'badges': badges,
        'all_badge_types': all_badge_types,
        'user': request.user
    }
    return render(request, 'core/dashboards/member_dashboard.html', context)


@login_required
def librarian_dashboard_view(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_librarian():
        return redirect('core:member_dashboard')
        
    today = timezone.now().date()
    
    issued_today_count = Loan.objects.filter(issue_date=today).count()
    returned_today_count = Loan.objects.filter(return_date=today).count()
    active_loans_count = Loan.objects.filter(status='ISSUED').count()
    overdue_loans_count = Loan.objects.filter(status='ISSUED', due_date__lt=today).count()
    
    pending_reservations_count = Reservation.objects.filter(status='PENDING').count()
    ready_reservations_count = Reservation.objects.filter(status='ALLOCATED').count()
    
    available_copies_count = BookCopy.objects.filter(status='AVAILABLE').count()
    recent_books = Book.objects.prefetch_related('authors').order_by('-created_at')[:5]
    
    most_read_ebooks = EBookMetadata.objects.select_related('book').annotate(
        read_count=Count('access_logs', filter=Q(access_logs__action='READ'))
    ).filter(read_count__gt=0).order_by('-read_count')[:5]

    context = {
        'today': today,
        'issued_today_count': issued_today_count,
        'returned_today_count': returned_today_count,
        'active_loans_count': active_loans_count,
        'overdue_loans_count': overdue_loans_count,
        'pending_reservations_count': pending_reservations_count,
        'ready_reservations_count': ready_reservations_count,
        'available_copies': available_copies_count,
        'total_books': Book.objects.count(),
        'total_ebooks': EBookMetadata.objects.count(),
        'active_ebooks': EBookMetadata.objects.filter(is_active=True).count(),
        'total_reads': EBookAccessLog.objects.filter(action='READ').count(),
        'total_downloads': EBookAccessLog.objects.filter(action='DOWNLOAD').count(),
        'most_read_ebooks': most_read_ebooks,
        'recent_books': recent_books,
    }
    return render(request, 'core/dashboards/librarian_dashboard.html', context)


@login_required
def admin_dashboard_view(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin():
        return redirect('core:librarian_dashboard') if hasattr(request.user, 'profile') and request.user.profile.is_librarian() else redirect('core:member_dashboard')
        
    today = timezone.now().date()
    
    total_members = UserProfile.objects.filter(role='MEMBER').count()
    active_members = UserProfile.objects.filter(role='MEMBER', membership_status='ACTIVE').count()
    expired_members = UserProfile.objects.filter(role='MEMBER', membership_status='EXPIRED').count()
    suspended_members = UserProfile.objects.filter(role='MEMBER', membership_status='SUSPENDED').count()
    total_librarians = UserProfile.objects.filter(role='LIBRARIAN').count()
    
    total_titles = Book.objects.count()
    total_physical_copies = BookCopy.objects.count()
    available_copies = BookCopy.objects.filter(status='AVAILABLE').count()
    issued_copies = BookCopy.objects.filter(status='ISSUED').count()
    reserved_copies = BookCopy.objects.filter(status='RESERVED').count()
    
    total_ebooks = EBookMetadata.objects.count()
    active_reservations = Reservation.objects.filter(status__in=['PENDING', 'ALLOCATED']).count()
    overdue_loans = Loan.objects.filter(status='ISSUED', due_date__lt=today).count()
    
    pending_fines_aggregate = Fine.objects.filter(status='PENDING').aggregate(total=Sum('amount'))['total']
    total_pending_fines = pending_fines_aggregate if pending_fines_aggregate is not None else Decimal('0.00')
    
    recent_loans = Loan.objects.select_related('member__user', 'book_copy__book').order_by('-issue_date')[:5]
    recent_reservations = Reservation.objects.select_related('member__user', 'book').order_by('-reservation_date')[:5]
    
    most_read_ebooks = EBookMetadata.objects.select_related('book').annotate(
        read_count=Count('access_logs', filter=Q(access_logs__action='READ'))
    ).filter(read_count__gt=0).order_by('-read_count')[:5]

    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]

    context = {
        'today': today,
        'total_members': total_members,
        'active_members': active_members,
        'expired_members': expired_members,
        'suspended_members': suspended_members,
        'total_librarians': total_librarians,
        'total_titles': total_titles,
        'total_physical_copies': total_physical_copies,
        'available_copies': available_copies,
        'issued_copies': issued_copies,
        'reserved_copies': reserved_copies,
        'total_ebooks': total_ebooks,
        'active_reservations': active_reservations,
        'overdue_loans': overdue_loans,
        'total_pending_fines': total_pending_fines,
        'recent_loans': recent_loans,
        'recent_reservations': recent_reservations,
        'recent_activities': recent_activities,
        'active_ebooks': EBookMetadata.objects.filter(is_active=True).count(),
        'total_reads': EBookAccessLog.objects.filter(action='READ').count(),
        'total_downloads': EBookAccessLog.objects.filter(action='DOWNLOAD').count(),
        'most_read_ebooks': most_read_ebooks,
    }
    return render(request, 'core/dashboards/admin_dashboard.html', context)


def privacy_policy_view(request):
    """Informational privacy policy page."""
    return render(request, 'core/privacy.html')


def terms_of_service_view(request):
    """Informational terms of service page."""
    return render(request, 'core/terms.html')


def help_faq_view(request):
    """Help & FAQ page."""
    return render(request, 'core/help.html')


# ── Custom Error Handlers ────────────────────────────────────────────────────

def dev_quick_login(request, username):
    """Developer fast-login helper in debug mode."""
    from django.conf import settings
    if settings.DEBUG:
        from django.contrib.auth import login
        from django.contrib.auth.models import User
        user = User.objects.filter(username=username).first()
        if user:
            login(request, user)
            return redirect(request.GET.get('next') or '/circulation/kiosk/')
    return redirect('/')


def custom_404_view(request, exception):
    """Custom 404 handler that works for both authenticated and anonymous users."""
    return render(request, '404.html', status=404)


def custom_403_view(request, exception):
    """Custom 403 handler for permission denied."""
    return render(request, '403.html', status=403)


def custom_500_view(request):
    """Custom 500 handler — uses standalone HTML, no template context needed."""
    return render(request, '500.html', status=500)

