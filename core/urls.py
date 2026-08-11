from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('dashboard/member/', views.member_dashboard_view, name='member_dashboard'),
    path('dashboard/librarian/', views.librarian_dashboard_view, name='librarian_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
]
