from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login


def is_librarian_or_admin(user):
    return user.is_authenticated and (
        user.is_superuser or
        (hasattr(user, 'profile') and (user.profile.is_librarian() or user.profile.is_admin()))
    )


def is_admin_user(user):
    return user.is_authenticated and (
        user.is_superuser or
        (hasattr(user, 'profile') and user.profile.is_admin())
    )


def librarian_required(view_func):
    """
    Ensures user is authenticated.
    If authenticated but not a librarian or administrator, raises PermissionDenied (403).
    Prevents infinite redirect loops between LoginView and staff views.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if is_librarian_or_admin(request.user):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You do not have librarian privileges to access this page.")
    return _wrapped_view


def admin_required(view_func):
    """
    Ensures user is authenticated.
    If authenticated but not an administrator, raises PermissionDenied (403).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if is_admin_user(request.user):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You must be an administrator to access this page.")
    return _wrapped_view
