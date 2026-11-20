from django.contrib import admin
from .models import AcademicProject


@admin.register(AcademicProject)
class AcademicProjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'category', 'leader', 'status', 'progress', 'delivery_date')
    list_filter = ('status', 'category')
    search_fields = ('code', 'title', 'leader')
