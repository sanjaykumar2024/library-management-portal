from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('api/toggle-theme/', views.api_toggle_theme, name='api_toggle_theme'),
    path('profile/update-contact/', views.update_contact_view, name='update_contact'),
    path('profile/request-renewal/', views.request_membership_renewal_view, name='request_renewal'),
    path('profile/submit-request/', views.submit_membership_request_view, name='submit_request'),
    
    # Librarian/Admin Member Management
    path('members/', views.MemberListView.as_view(), name='member_list'),
    path('members/requests/', views.manage_membership_requests_view, name='manage_requests'),
    path('members/<int:pk>/', views.MemberDetailView.as_view(), name='member_detail'),
    path('members/<int:pk>/edit/', views.MemberUpdateView.as_view(), name='member_edit'),
    path('members/<int:pk>/renew/', views.renew_membership_view, name='member_renew'),
    path('members/<int:pk>/toggle-status/', views.toggle_member_status_view, name='member_toggle_status'),
]

