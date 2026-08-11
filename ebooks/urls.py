from django.urls import path
from . import views

app_name = 'ebooks'

urlpatterns = [
    path('', views.ebook_catalog_view, name='catalog'),
    path('manage/', views.ebook_manage_view, name='manage'),
    path('upload/', views.ebook_upload_view, name='upload'),
    path('history/', views.member_reading_history_view, name='history'),
    path('reports/', views.ebook_usage_report_view, name='reports'),
    path('<int:ebook_id>/', views.ebook_detail_view, name='detail'),
    path('<int:ebook_id>/read/', views.ebook_read_view, name='read'),
    path('<int:ebook_id>/stream/', views.ebook_stream_view, name='stream'),
    path('<int:ebook_id>/download/', views.ebook_download_view, name='download'),
    path('<int:ebook_id>/edit/', views.ebook_edit_view, name='edit'),
    path('<int:ebook_id>/deactivate/', views.ebook_deactivate_view, name='deactivate'),
]
