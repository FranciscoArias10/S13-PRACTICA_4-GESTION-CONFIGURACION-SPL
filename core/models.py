from django.db import models


class AcademicProject(models.Model):
    """Entidad principal del dominio: proyectos gestionados por el núcleo del sistema."""

    STATUS_CHOICES = [
        ('PLANIFICADO', 'Planificado'),
        ('EN_CURSO', 'En Curso'),
        ('REVISION', 'En Revisión'),
        ('COMPLETADO', 'Completado'),
    ]

    CATEGORY_CHOICES = [
        ('WEB', 'Sistema Web'),
        ('SPL', 'Línea de Productos'),
        ('MOVIL', 'Aplicación Móvil'),
        ('DATOS', 'Analítica / Datos'),
    ]

    code = models.CharField(max_length=25, unique=True)
    title = models.CharField(max_length=180)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='SPL')
    leader = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EN_CURSO')
    progress = models.PositiveSmallIntegerField(default=50)
    budget_usd = models.DecimalField(max_digits=10, decimal_places=2, default=1200.00)
    delivery_date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', 'code']
        verbose_name = 'Proyecto Académico'
        verbose_name_plural = 'Proyectos Académicos'

    def __str__(self):
        return f'{self.code} - {self.title}'
