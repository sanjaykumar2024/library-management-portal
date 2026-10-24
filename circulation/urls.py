from django.urls import path
from . import views

app_name = 'circulation'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard_alias'),
    path('issue/', views.issue_book_view, name='issue_book'),
    path('return/', views.return_book_list_view, name='return_list'),
    path('returns/', views.return_book_list_view, name='returns_alias'),
    path('return/<int:loan_id>/', views.process_return_view, name='process_return'),
    path('loan/<int:loan_id>/', views.loan_detail_view, name='loan_detail'),
    path('loan/<int:loan_id>/renew/', views.renew_book_view, name='renew_book'),
    path('loan/<int:loan_id>/receipt/', views.loan_receipt_view, name='loan_receipt'),
    path('fines/', views.fine_list_view, name='fine_list'),
    path('fines/<int:fine_id>/pay/', views.pay_fine_view, name='pay_fine'),
    path('fines/<int:fine_id>/receipt/', views.fine_receipt_view, name='fine_receipt'),
    path('overdue/scan/', views.trigger_overdue_check_view, name='trigger_overdue_check'),
    path('loan/<int:loan_id>/send-notice/', views.send_overdue_notice_view, name='send_overdue_notice'),
    # Pillar 2: Self-Service Kiosk & Barcode APIs
    path('kiosk/', views.kiosk_view, name='kiosk'),
    path('api/kiosk/lookup-member/', views.api_kiosk_lookup_member, name='api_kiosk_lookup_member'),
    path('api/kiosk/lookup-book/', views.api_kiosk_lookup_book, name='api_kiosk_lookup_book'),
    path('api/kiosk/checkout/', views.api_kiosk_checkout, name='api_kiosk_checkout'),
]

