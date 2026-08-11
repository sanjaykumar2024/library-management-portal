import csv
from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.utils import timezone

from accounts.models import UserProfile
from catalog.models import Book, BookCopy, Category, EBookMetadata
from circulation.models import Loan, Fine
from reservations.models import Reservation
from ebooks.models import EBookAccessLog


def is_librarian_or_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_librarian()


# ---------------------------------------------------------------------------
# Report Index Hub
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_librarian_or_admin)
def report_index(request):
    today = timezone.now().date()
    context = {
        'total_members': UserProfile.objects.filter(role='MEMBER').count(),
        'total_books': Book.objects.count(),
        'active_loans': Loan.objects.filter(status='ISSUED').count(),
        'overdue_loans': Loan.objects.filter(status='ISSUED', due_date__lt=today).count(),
        'total_fines': Fine.objects.filter(status='PENDING').aggregate(t=Sum('amount'))['t'] or Decimal('0.00'),
        'total_reservations': Reservation.objects.filter(status='PENDING').count(),
        'total_ebook_reads': EBookAccessLog.objects.filter(action='READ').count(),
    }
    return render(request, 'reports/report_index.html', context)


# ---------------------------------------------------------------------------
# 1. Membership Report
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_librarian_or_admin)
def membership_report(request):
    status = request.GET.get('status', '')
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    members = UserProfile.objects.filter(role='MEMBER').select_related('user').order_by('-joining_date')

    if status:
        members = members.filter(membership_status=status)
    if query:
        members = members.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(membership_number__icontains=query) |
            Q(phone_number__icontains=query)
        )
    if start_date:
        members = members.filter(joining_date__gte=start_date)
    if end_date:
        members = members.filter(joining_date__lte=end_date)

    context = {
        'members': members,
        'selected_status': status,
        'q': query,
        'start_date': start_date,
        'end_date': end_date,
        'total_count': members.count(),
        'status_choices': UserProfile.STATUS_CHOICES,
    }
    return render(request, 'reports/membership_report.html', context)


@login_required
@user_passes_test(is_librarian_or_admin)
def membership_csv(request):
    status = request.GET.get('status', '')
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    members = UserProfile.objects.filter(role='MEMBER').select_related('user').order_by('-joining_date')

    if status:
        members = members.filter(membership_status=status)
    if query:
        members = members.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(membership_number__icontains=query)
        )
    if start_date:
        members = members.filter(joining_date__gte=start_date)
    if end_date:
        members = members.filter(joining_date__lte=end_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="membership_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Membership #', 'Username', 'Full Name', 'Email', 'Phone', 'Joining Date', 'Expiry Date', 'Status'])

    for m in members:
        writer.writerow([
            m.membership_number,
            m.user.username,
            m.user.get_full_name(),
            m.user.email,
            m.phone_number or '',
            m.joining_date or '',
            m.membership_expiry_date or '',
            m.get_membership_status_display()
        ])

    return response


# ---------------------------------------------------------------------------
# 2. Book Inventory Report
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_librarian_or_admin)
def inventory_report(request):
    category_id = request.GET.get('category', '')
    book_type = request.GET.get('type', '')
    copy_status = request.GET.get('copy_status', '')
    query = request.GET.get('q', '')

    copies = BookCopy.objects.select_related('book', 'book__category').order_by('accession_number')

    if category_id:
        copies = copies.filter(book__category_id=category_id)
    if book_type:
        copies = copies.filter(book__book_type=book_type)
    if copy_status:
        copies = copies.filter(status=copy_status)
    if query:
        copies = copies.filter(
            Q(book__title__icontains=query) |
            Q(book__isbn__icontains=query) |
            Q(accession_number__icontains=query)
        )

    categories = Category.objects.all()

    context = {
        'copies': copies,
        'categories': categories,
        'selected_category': category_id,
        'selected_type': book_type,
        'selected_copy_status': copy_status,
        'q': query,
        'total_copies': copies.count(),
        'copy_status_choices': BookCopy.STATUS_CHOICES,
        'book_type_choices': Book.BOOK_TYPE_CHOICES,
    }
    return render(request, 'reports/inventory_report.html', context)


@login_required
@user_passes_test(is_librarian_or_admin)
def inventory_csv(request):
    category_id = request.GET.get('category', '')
    book_type = request.GET.get('type', '')
    copy_status = request.GET.get('copy_status', '')
    query = request.GET.get('q', '')

    copies = BookCopy.objects.select_related('book', 'book__category').order_by('accession_number')

    if category_id:
        copies = copies.filter(book__category_id=category_id)
    if book_type:
        copies = copies.filter(book__book_type=book_type)
    if copy_status:
        copies = copies.filter(status=copy_status)
    if query:
        copies = copies.filter(
            Q(book__title__icontains=query) |
            Q(book__isbn__icontains=query) |
            Q(accession_number__icontains=query)
        )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="book_inventory_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Accession Number', 'Title', 'ISBN', 'Category', 'Format', 'Shelf Location', 'Status'])

    for c in copies:
        writer.writerow([
            c.accession_number,
            c.book.title,
            c.book.isbn,
            c.book.category.name if c.book.category else '',
            c.book.get_book_type_display(),
            c.shelf_location or '',
            c.get_status_display()
        ])

    return response


# ---------------------------------------------------------------------------
# 3. Loan & Return Report
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_librarian_or_admin)
def loan_report(request):
    status = request.GET.get('status', '')
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    loans = Loan.objects.select_related('member__user', 'book_copy__book').order_by('-issue_date')

    if status:
        loans = loans.filter(status=status)
    if query:
        loans = loans.filter(
            Q(member__user__username__icontains=query) |
            Q(member__user__first_name__icontains=query) |
            Q(member__user__last_name__icontains=query) |
            Q(book_copy__book__title__icontains=query) |
            Q(book_copy__accession_number__icontains=query)
        )
    if start_date:
        loans = loans.filter(issue_date__gte=start_date)
    if end_date:
        loans = loans.filter(issue_date__lte=end_date)

    context = {
        'loans': loans,
        'selected_status': status,
        'q': query,
        'start_date': start_date,
        'end_date': end_date,
        'total_loans': loans.count(),
        'loan_status_choices': Loan.STATUS_CHOICES,
    }
    return render(request, 'reports/loan_report.html', context)


@login_required
@user_passes_test(is_librarian_or_admin)
def loan_csv(request):
    status = request.GET.get('status', '')
    query = request.GET.get('q', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    loans = Loan.objects.select_related('member__user', 'book_copy__book').order_by('-issue_date')

    if status:
        loans = loans.filter(status=status)
    if query:
        loans = loans.filter(
            Q(member__user__username__icontains=query) |
            Q(book_copy__book__title__icontains=query)
        )
    if start_date:
        loans = loans.filter(issue_date__gte=start_date)
    if end_date:
        loans = loans.filter(issue_date__lte=end_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="loan_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Loan ID', 'Member', 'Book Title', 'Accession #', 'Issue Date', 'Due Date', 'Return Date', 'Status'])

    for l in loans:
        writer.writerow([
            l.id,
            l.member.user.get_full_name() or l.member.user.username,
            l.book_copy.book.title,
            l.book_copy.accession_number,
            l.issue_date,
            l.due_date,
            l.return_date or '',
            l.get_status_display()
        ])

    return response


# ---------------------------------------------------------------------------
# 4. Overdue Books Report
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_librarian_or_admin)
def overdue_report(request):
    today = timezone.now().date()
    loans = Loan.objects.filter(status='ISSUED', due_date__lt=today).select_related('member__user', 'book_copy__book').order_by('due_date')

    context = {
        'loans': loans,
        'today': today,
        'total_overdue': loans.count(),
    }
    return render(request, 'reports/overdue_report.html', context)


@login_required
@user_passes_test(is_librarian_or_admin)
def overdue_csv(request):
    today = timezone.now().date()
    loans = Loan.objects.filter(status='ISSUED', due_date__lt=today).select_related('member__user', 'book_copy__book').order_by('due_date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="overdue_loans_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Loan ID', 'Member Name', 'Member Phone', 'Book Title', 'Accession #', 'Due Date', 'Days Overdue'])

    for l in loans:
        days_overdue = (today - l.due_date).days
        writer.writerow([
            l.id,
            l.member.user.get_full_name() or l.member.user.username,
            l.member.phone_number or '',
            l.book_copy.book.title,
            l.book_copy.accession_number,
            l.due_date,
            days_overdue
        ])

    return response


# ---------------------------------------------------------------------------
# 5. Fine Report
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_librarian_or_admin)
def fine_report(request):
    status = request.GET.get('status', '')
    query = request.GET.get('q', '')

    fines = Fine.objects.select_related('loan__member__user', 'loan__book_copy__book').order_by('-created_at')

    if status:
        fines = fines.filter(status=status)
    if query:
        fines = fines.filter(
            Q(loan__member__user__username__icontains=query) |
            Q(loan__member__user__first_name__icontains=query) |
            Q(loan__member__user__last_name__icontains=query) |
            Q(loan__book_copy__book__title__icontains=query)
        )

    total_amount = fines.aggregate(t=Sum('amount'))['t'] or Decimal('0.00')

    context = {
        'fines': fines,
        'selected_status': status,
        'q': query,
        'total_fines_count': fines.count(),
        'total_amount': total_amount,
        'fine_status_choices': Fine.STATUS_CHOICES,
    }
    return render(request, 'reports/fine_report.html', context)


@login_required
@user_passes_test(is_librarian_or_admin)
def fine_csv(request):
    status = request.GET.get('status', '')
    query = request.GET.get('q', '')

    fines = Fine.objects.select_related('loan__member__user', 'loan__book_copy__book').order_by('-created_at')

    if status:
        fines = fines.filter(status=status)
    if query:
        fines = fines.filter(
            Q(loan__member__user__username__icontains=query) |
            Q(loan__book_copy__book__title__icontains=query)
        )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fines_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Fine ID', 'Member', 'Book Title', 'Amount ($)', 'Overdue Days', 'Status', 'Issued Date'])

    for f in fines:
        writer.writerow([
            f.id,
            f.loan.member.user.get_full_name() or f.loan.member.user.username,
            f.loan.book_copy.book.title if f.loan else 'N/A',
            f.amount,
            f.overdue_days,
            f.get_status_display(),
            f.created_at.strftime("%Y-%m-%d")
        ])

    return response


# ---------------------------------------------------------------------------
# 6. Reservation Report
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_librarian_or_admin)
def reservation_report(request):
    status = request.GET.get('status', '')
    query = request.GET.get('q', '')

    reservations = Reservation.objects.select_related('member__user', 'book').order_by('-reservation_date')

    if status:
        reservations = reservations.filter(status=status)
    if query:
        reservations = reservations.filter(
            Q(member__user__username__icontains=query) |
            Q(book__title__icontains=query)
        )

    context = {
        'reservations': reservations,
        'selected_status': status,
        'q': query,
        'total_reservations': reservations.count(),
        'reservation_status_choices': Reservation.STATUS_CHOICES,
    }
    return render(request, 'reports/reservation_report.html', context)


@login_required
@user_passes_test(is_librarian_or_admin)
def reservation_csv(request):
    status = request.GET.get('status', '')
    query = request.GET.get('q', '')

    reservations = Reservation.objects.select_related('member__user', 'book').order_by('-reservation_date')

    if status:
        reservations = reservations.filter(status=status)
    if query:
        reservations = reservations.filter(
            Q(member__user__username__icontains=query) |
            Q(book__title__icontains=query)
        )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reservations_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Reservation ID', 'Member', 'Book Title', 'Requested Date', 'Status'])

    for r in reservations:
        writer.writerow([
            r.id,
            r.member.user.get_full_name() or r.member.user.username,
            r.book.title,
            r.reservation_date.strftime("%Y-%m-%d %H:%M"),
            r.get_status_display()
        ])

    return response


# ---------------------------------------------------------------------------
# 7. E-Book Usage Report
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_librarian_or_admin)
def ebook_usage_report(request):
    action = request.GET.get('action', '')
    query = request.GET.get('q', '')

    logs = EBookAccessLog.objects.select_related('user', 'ebook', 'ebook__book').order_by('-accessed_at')

    if action:
        logs = logs.filter(action=action)
    if query:
        logs = logs.filter(
            Q(user__username__icontains=query) |
            Q(ebook__book__title__icontains=query)
        )

    context = {
        'logs': logs,
        'selected_action': action,
        'q': query,
        'total_logs': logs.count(),
        'action_choices': EBookAccessLog.ACTION_CHOICES,
    }
    return render(request, 'reports/ebook_usage_report.html', context)


@login_required
@user_passes_test(is_librarian_or_admin)
def ebook_usage_csv(request):
    action = request.GET.get('action', '')
    query = request.GET.get('q', '')

    logs = EBookAccessLog.objects.select_related('user', 'ebook', 'ebook__book').order_by('-accessed_at')

    if action:
        logs = logs.filter(action=action)
    if query:
        logs = logs.filter(
            Q(user__username__icontains=query) |
            Q(ebook__book__title__icontains=query)
        )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ebook_access_history.csv"'

    writer = csv.writer(response)
    writer.writerow(['Log ID', 'User', 'E-Book Title', 'Action', 'Accessed At'])

    for l in logs:
        writer.writerow([
            l.id,
            l.user.get_full_name() or l.user.username,
            l.ebook.book.title,
            l.get_action_display(),
            l.accessed_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    return response


# ---------------------------------------------------------------------------
# 8. Popular Books & E-Books Report
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_librarian_or_admin)
def popular_report(request):
    popular_physical = Book.objects.annotate(
        loan_count=Count('copies__loans')
    ).order_by('-loan_count')[:10]

    popular_ebooks = EBookMetadata.objects.annotate(
        read_count=Count('access_logs', filter=Q(access_logs__action='READ')),
        download_count=Count('access_logs', filter=Q(access_logs__action='DOWNLOAD'))
    ).order_by('-read_count')[:10]

    context = {
        'popular_physical': popular_physical,
        'popular_ebooks': popular_ebooks,
    }
    return render(request, 'reports/popular_report.html', context)
