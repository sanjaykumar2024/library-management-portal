from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('my-reservations/', views.my_reservations_view, name='my_reservations'),
    path('my/', views.my_reservations_view, name='my_reservations_alias'),
    path('book/<int:book_id>/reserve/', views.reserve_book_view, name='reserve_book'),
    path('cancel/<int:reservation_id>/', views.cancel_reservation_view, name='cancel_reservation'),
    
    # Librarian views
    path('manage/', views.manage_reservations_view, name='manage_reservations'),
    path('allocate/<int:reservation_id>/', views.allocate_reservation_view, name='allocate_reservation'),
    path('extend/<int:reservation_id>/', views.extend_reservation_view, name='extend_reservation'),
    path('expire-overdue/', views.batch_expire_reservations_view, name='expire_overdue'),
    path('fulfill/<int:reservation_id>/', views.fulfill_reservation_view, name='fulfill_reservation'),
]


