from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('dashboard/member/', views.member_dashboard_view, name='member_dashboard'),
    path('dashboard/librarian/', views.librarian_dashboard_view, name='librarian_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('privacy/', views.privacy_policy_view, name='privacy'),
    path('terms/', views.terms_of_service_view, name='terms'),
    path('help/', views.help_faq_view, name='help'),
    path('dev-login/<str:username>/', views.dev_quick_login, name='dev_quick_login'),
]
