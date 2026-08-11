from .models import Notification

def create_notification(user, title, message, type='INFO', link=None):
    """
    Creates a new notification for a user.
    """
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=type,
        link=link
    )

def mark_as_read(notification_id, user):
    """
    Marks a specific notification as read.
    """
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.is_read = True
        notification.save()
        return True
    except Notification.DoesNotExist:
        return False

def mark_all_as_read(user):
    """
    Marks all notifications for a user as read.
    """
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)
