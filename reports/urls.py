from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_index, name='index'),
    path('members/', views.membership_report, name='membership'),
    path('memberships/', views.membership_report, name='membership_alias'),
    path('members/csv/', views.membership_csv, name='membership_csv'),
    path('memberships/csv/', views.membership_csv, name='membership_csv_alias'),
    path('inventory/', views.inventory_report, name='inventory'),
    path('inventory/csv/', views.inventory_csv, name='inventory_csv'),
    path('loans/', views.loan_report, name='loans'),
    path('loans/csv/', views.loan_csv, name='loans_csv'),
    path('overdue/', views.overdue_report, name='overdue'),
    path('overdue/csv/', views.overdue_csv, name='overdue_csv'),
    path('fines/', views.fine_report, name='fines'),
    path('fines/csv/', views.fine_csv, name='fines_csv'),
    path('reservations/', views.reservation_report, name='reservations'),
    path('reservations/csv/', views.reservation_csv, name='reservations_csv'),
    path('ebook-usage/', views.ebook_usage_report, name='ebook_usage'),
    path('ebook-usage/csv/', views.ebook_usage_csv, name='ebook_usage_csv'),
    path('popular/', views.popular_report, name='popular'),
]
