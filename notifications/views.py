from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .models import SystemNotification


def _ensure_notifications_enabled():
    """Resguardo adicional de variabilidad para el módulo de notificaciones."""
    if not settings.ENABLE_NOTIFICATIONS:
        raise Http404('El módulo opcional de notificaciones está desactivado en esta variante.')


def notification_center(request):
    """Centro de alertas y notificaciones (activo únicamente cuando ENABLE_NOTIFICATIONS=True)."""
    _ensure_notifications_enabled()

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'mark_all_read':
            SystemNotification.objects.filter(is_read=False).update(is_read=True)
            messages.success(request, 'Todas las notificaciones fueron marcadas como leídas.')
        elif action == 'create':
            title = request.POST.get('title', '').strip()
            msg = request.POST.get('message', '').strip()
            level = request.POST.get('level', 'INFO').strip()
            target_role = request.POST.get('target_role', 'Equipo SPL').strip()
            if title and msg:
                SystemNotification.objects.create(
                    title=title,
                    message=msg,
                    level=level,
                    target_role=target_role,
                )
                messages.success(request, f'Notificación "{title}" emitida correctamente.')
        return redirect('notifications:center')

    level_filter = request.GET.get('level', '').strip()
    items = SystemNotification.objects.all()
    if level_filter:
        items = items.filter(level=level_filter)

    return render(
        request,
        'notifications/center.html',
        {
            'notifications': items,
            'level_filter': level_filter,
            'level_choices': SystemNotification.LEVEL_CHOICES,
        },
    )


def mark_as_read(request, pk):
    """Marca una notificación individual como leída."""
    _ensure_notifications_enabled()
    notif = get_object_or_404(SystemNotification, pk=pk)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    messages.info(request, f'Notificación "{notif.title}" marcada como leída.')
    return redirect('notifications:center')
