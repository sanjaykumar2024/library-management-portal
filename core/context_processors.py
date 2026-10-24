from notifications.models import Notification


def notification_count(request):
    """Provide unread notification count to all templates."""
    if hasattr(request, 'user') and request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notification_count': count}
    return {'unread_notification_count': 0}


def theme_context(request):
    """Provide active theme ('light' or 'dark') to all templates."""
    theme = 'light'
    session = getattr(request, 'session', None)
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            theme = request.user.profile.theme_preference or 'light'
        except Exception:
            if session:
                theme = session.get('theme_preference', 'light')
    elif session:
        theme = session.get('theme_preference', 'light')
    return {
        'theme_preference': theme,
        'is_dark_mode': theme == 'dark',
    }
