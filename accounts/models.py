from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """Perfil extendido reutilizable para cualquier proyecto Django institucional."""

    ROLE_CHOICES = [
        ('ADMIN', 'Administrador SPL'),
        ('DOCENTE', 'Docente Tutor'),
        ('ESTUDIANTE', 'Estudiante'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='spl_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ESTUDIANTE')
    department = models.CharField(max_length=120, default='Facultad de Ciencias e Ingeniería')
    institutional_id = models.CharField(max_length=30, blank=True)
    is_active_member = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['role', 'user__first_name', 'user__username']
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        full_name = self.user.get_full_name() or self.user.username
        return f'{full_name} ({self.get_role_display()})'
