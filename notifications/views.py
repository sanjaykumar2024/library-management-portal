from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification
from . import services

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def mark_read_view(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        services.mark_as_read(notification_id, request.user)
        if notification.link:
            return redirect(notification.link)
    return redirect('notifications:list')

@login_required
def mark_all_read_view(request):
    if request.method == 'POST':
        services.mark_all_as_read(request.user)
    return redirect('notifications:list')
