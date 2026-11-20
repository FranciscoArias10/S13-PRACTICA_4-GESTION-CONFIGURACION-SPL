from django.db import models


class Attachment(models.Model):
    """Repositorio de archivos reutilizable sin acoplamiento rígido al dominio."""

    CATEGORY_CHOICES = [
        ('SPEC', 'Especificación Técnica'),
        ('DIAGRAM', 'Diagrama de Arquitectura'),
        ('REPORT', 'Informe / Acta'),
        ('OTHER', 'Otro Documento'),
    ]

    title = models.CharField(max_length=150)
    reference_tag = models.CharField(max_length=60, default='CORE-GENERAL')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='SPEC')
    file = models.FileField(upload_to='attachments/%Y/%m/', blank=True, null=True)
    external_url = models.CharField(max_length=255, blank=True)
    uploaded_by = models.CharField(max_length=100, default='Administrador SPL')
    size_kb = models.PositiveIntegerField(default=128)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Archivo Adjunto'
        verbose_name_plural = 'Archivos Adjuntos'

    def __str__(self):
        return f'{self.title} [{self.reference_tag}]'
