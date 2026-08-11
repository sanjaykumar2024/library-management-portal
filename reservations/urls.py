from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('my-reservations/', views.my_reservations_view, name='my_reservations'),
    path('book/<int:book_id>/reserve/', views.reserve_book_view, name='reserve_book'),
    path('cancel/<int:reservation_id>/', views.cancel_reservation_view, name='cancel_reservation'),
    
    # Librarian views
    path('manage/', views.manage_reservations_view, name='manage_reservations'),
    path('fulfill/<int:reservation_id>/', views.fulfill_reservation_view, name='fulfill_reservation'),
]
