from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class AccountStatusMiddleware:
    """
    Enforces active account security.
    If an authenticated user's account has been suspended by an administrator,
    immediately terminates their active session, flushes auth cookies,
    and redirects them to the login page with an explicit security alert.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            profile = request.user.profile
            if profile.membership_status == 'SUSPENDED':
                current_path = request.path_info
                logout_url = reverse('accounts:logout')
                login_url = reverse('accounts:login')

                # Allow logout or static/media paths without loop
                if current_path != logout_url and current_path != login_url and not current_path.startswith('/static/') and not current_path.startswith('/media/'):
                    username = request.user.username
                    logout(request)
                    messages.error(
                        request,
                        f"Account '{username}' has been suspended by the library administration. Access has been revoked."
                    )
                    return redirect('accounts:login')

        response = self.get_response(request)
        return response
