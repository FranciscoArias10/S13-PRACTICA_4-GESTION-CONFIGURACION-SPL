from django.contrib import admin
from .models import Attachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'reference_tag', 'category', 'uploaded_by', 'size_kb', 'uploaded_at')
    list_filter = ('category',)
    search_fields = ('title', 'reference_tag', 'uploaded_by')
