from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('export/pdf/', views.export_projects_pdf, name='export_pdf'),
    path('export/csv/', views.export_projects_csv, name='export_csv'),
]
