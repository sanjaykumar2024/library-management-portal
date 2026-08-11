from django.urls import path
from . import views

app_name = 'circulation'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('issue/', views.issue_book_view, name='issue_book'),
    path('return/', views.return_book_list_view, name='return_list'),
    path('return/<int:loan_id>/', views.process_return_view, name='process_return'),
    path('loan/<int:loan_id>/', views.loan_detail_view, name='loan_detail'),
    path('loan/<int:loan_id>/renew/', views.renew_book_view, name='renew_book'),
    path('loan/<int:loan_id>/receipt/', views.loan_receipt_view, name='loan_receipt'),
    path('fines/', views.fine_list_view, name='fine_list'),
    path('fines/<int:fine_id>/pay/', views.pay_fine_view, name='pay_fine'),
    path('fines/<int:fine_id>/receipt/', views.fine_receipt_view, name='fine_receipt'),
]
