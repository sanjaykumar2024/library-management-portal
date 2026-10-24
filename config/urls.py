"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from core.views import custom_404_view, custom_403_view, custom_500_view

from django.views.generic.base import RedirectView

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/book-half.svg', permanent=True)),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('catalog/', include('catalog.urls')),
    path('circulation/', include('circulation.urls')),
    path('reservations/', include('reservations.urls')),
    path('notifications/', include('notifications.urls')),
    path('ebooks/', include('ebooks.urls')),
    path('reports/', include('reports.urls')),
    path('', include('core.urls')),
]

handler404 = custom_404_view
handler403 = custom_403_view
handler500 = custom_500_view

# Serve media files in both development and production (for platforms like Render/PythonAnywhere)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

