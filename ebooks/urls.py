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
    path('<int:ebook_id>/unlock/', views.ebook_unlock_view, name='unlock'),
    path('<int:ebook_id>/download/', views.ebook_download_view, name='download'),
    path('<int:ebook_id>/edit/', views.ebook_edit_view, name='edit'),
    path('commons/', views.ebook_commons_view, name='commons'),
    path('open-source/', views.open_source_discovery_view, name='open_source_discovery'),
    path('kaggle-import/', views.kaggle_import_view, name='kaggle_import'),
    path('api/import-open-source/', views.import_open_source_book_api, name='api_import_open_source'),
    path('<int:ebook_id>/deactivate/', views.ebook_deactivate_view, name='deactivate'),
    path('<int:ebook_id>/revalidate/', views.ebook_revalidate_view, name='revalidate'),
    # Pillar 3: Highlights & Annotations
    path('api/<int:ebook_id>/annotations/add/', views.api_add_annotation, name='api_add_annotation'),
    path('api/<int:ebook_id>/annotations/list/', views.api_list_annotations, name='api_list_annotations'),
    path('api/annotations/<int:annotation_id>/delete/', views.api_delete_annotation, name='api_delete_annotation'),
]
