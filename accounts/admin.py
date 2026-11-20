from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'institutional_id', 'is_active_member')
    list_filter = ('role', 'is_active_member')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'institutional_id')
