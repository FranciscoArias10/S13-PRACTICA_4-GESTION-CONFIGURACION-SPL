from django.urls import path
from . import views

app_name = 'file_manager'

urlpatterns = [
    path('', views.attachment_list, name='list'),
]
