from django.contrib import admin
from .models import SystemNotification


@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'target_role', 'is_read', 'created_at')
    list_filter = ('level', 'is_read')
    search_fields = ('title', 'message')
