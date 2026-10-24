from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_list_view, name='list'),
    path('book/<int:book_id>/', views.book_detail_view, name='detail'),
    path('book/<int:book_id>/review/', views.add_book_review_view, name='add_review'),
    path('api/bookshelf/toggle/', views.toggle_bookshelf_api, name='api_toggle_bookshelf'),
    path('my-bookshelf/', views.my_bookshelf_view, name='my_bookshelf'),
    path('my-shelf/', views.my_bookshelf_view, name='my_shelf_alias'),
    path('ai-assistant/', views.ai_assistant_view, name='ai_assistant'),
    path('api/ai-assistant/', views.ai_assistant_api, name='ai_assistant_api'),
    path('api/semantic-search/', views.semantic_search_api, name='semantic_search_api'),
    # Librarian Catalog Management
    path('book/create/', views.book_create_view, name='book_create'),
    path('book/<int:book_id>/edit/', views.book_edit_view, name='book_edit'),
    path('book/<int:book_id>/add-copy/', views.add_book_copy_view, name='add_book_copy'),
]


