from django.db import models


class SystemNotification(models.Model):
    """Notificaciones opcionales habilitadas en la Variante B (Sesión 3)."""

    LEVEL_CHOICES = [
        ('INFO', 'Informativa'),
        ('SUCCESS', 'Éxito'),
        ('WARNING', 'Alerta'),
    ]

    title = models.CharField(max_length=140)
    message = models.TextField()
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='INFO')
    target_role = models.CharField(max_length=40, default='Todos')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_read', '-created_at']
        verbose_name = 'Notificación del Sistema'
        verbose_name_plural = 'Notificaciones del Sistema'

    def __str__(self):
        return f'[{self.level}] {self.title}'
