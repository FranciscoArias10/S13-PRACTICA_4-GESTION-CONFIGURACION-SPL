"""Context processor para inyectar las banderas SPL en todas las plantillas."""

from django.apps import apps
from django.conf import settings


def spl_context(request):
    """Expone variante activa, feature flags y contador opcional de notificaciones."""
    unread_notifications = 0
    if settings.ENABLE_NOTIFICATIONS and apps.is_installed('notifications'):
        from notifications.models import SystemNotification
        unread_notifications = SystemNotification.objects.filter(is_read=False).count()

    return {
        'ACTIVE_VARIANT': settings.ACTIVE_VARIANT,
        'ACTIVE_CONFIG': settings.ACTIVE_CONFIG,
        'ENABLE_REPORTS': settings.ENABLE_REPORTS,
        'ENABLE_NOTIFICATIONS': settings.ENABLE_NOTIFICATIONS,
        'UNREAD_NOTIFICATIONS': unread_notifications,
    }
