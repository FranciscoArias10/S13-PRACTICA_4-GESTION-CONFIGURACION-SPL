"""Inicializa migraciones y carga datos semilla institucionales para el proyecto SPL."""

import os
import sys
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Garantiza que todas las apps (incluidas las opcionales) ejecuten sus migraciones.
os.environ['SPL_VARIANT'] = 'PRODUCT_B'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spl_project.settings')

import django

django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command
from accounts.models import UserProfile
from core.models import AcademicProject
from file_manager.models import Attachment
from notifications.models import SystemNotification


def seed_database():
    print('>> Ejecutando makemigrations y migrate...')
    call_command('makemigrations', 'accounts', 'file_manager', 'core', 'notifications', verbosity=1)
    call_command('migrate', verbosity=1)

    print('>> Limpiando registros semilla previos...')
    User.objects.filter(username__in=['oangulo', 'ejaramillo']).delete()

    print('>> Sembrando usuarios institucionales en app reutilizable [accounts]...')
    users_data = [
        ('farias', 'Francisco Steven', 'Arias Pérez', 'fariasp2@unemi.edu.ec', 'ADMIN', 'UNEMI-2026-01'),
        ('dfarias', 'Darly Douglas', 'Farías Mendoza', 'dfarias@unemi.edu.ec', 'ESTUDIANTE', 'UNEMI-2026-02'),
        ('ooviedoa', 'Omar Andrés', 'Oviedo Armijos', 'ooviedoa@unemi.edu.ec', 'DOCENTE', 'UNEMI-DOC-01'),
    ]
    for username, first, last, email, role, inst_id in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'first_name': first, 'last_name': last, 'email': email, 'is_staff': role == 'ADMIN', 'is_superuser': role == 'ADMIN'},
        )
        if created:
            user.set_password('Unemi2026*')
            user.save()
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'role': role,
                'department': 'Facultad Ciencias e Ingenierías — Software',
                'institutional_id': inst_id,
            },
        )

    print('>> Sembrando proyectos académicos en núcleo [core]...')
    projects_data = [
        ('SPL-2026-01', 'Plataforma Modular de Gestión Académica', 'SPL', 'Francisco Steven Arias Pérez', 'COMPLETADO', 100, 2400.00, date(2026, 11, 18), 'Núcleo base con arquitectura de apps reutilizables.'),
        ('SPL-2026-02', 'Módulo Exportador de Reportes Ejecutivos PDF', 'WEB', 'Darly Douglas Farías Mendoza', 'COMPLETADO', 100, 1350.00, date(2026, 11, 20), 'App aislada controlada mediante bandera ENABLE_REPORTS.'),
        ('SPL-2026-03', 'Centro de Notificaciones y Alertas en Tiempo Real', 'SPL', 'Francisco Steven Arias Pérez', 'EN_CURSO', 85, 1600.00, date(2026, 11, 25), 'Componente opcional activado en Variante B.'),
        ('SPL-2026-04', 'Gestor Documental Portátil entre Proyectos Django', 'WEB', 'Darly Douglas Farías Mendoza', 'REVISION', 90, 1100.00, date(2026, 11, 28), 'Componente reutilizable file_manager desacoplado.'),
        ('SPL-2026-05', 'Tablero Analítico de Variabilidad y Métricas RiSE', 'DATOS', 'Francisco Steven Arias Pérez', 'EN_CURSO', 70, 1850.00, date(2026, 12, 4), 'Seguimiento de adopción de reutilización según modelo RiSE.'),
        ('SPL-2026-06', 'Cliente Móvil Institucional UNEMI-SPL', 'MOVIL', 'Darly Douglas Farías Mendoza', 'PLANIFICADO', 35, 2900.00, date(2026, 12, 18), 'Extensión multicanal conectada al núcleo core.'),
    ]
    for code, title, cat, leader, status, prog, budget, ddate, desc in projects_data:
        AcademicProject.objects.update_or_create(
            code=code,
            defaults={
                'title': title,
                'category': cat,
                'leader': leader,
                'status': status,
                'progress': prog,
                'budget_usd': budget,
                'delivery_date': ddate,
                'description': desc,
            },
        )

    print('>> Sembrando documentos técnicos en app reutilizable [file_manager]...')
    files_data = [
        ('Hoja de Análisis de Funcionalidades — Sesión 1', 'SESION-01', 'SPEC', 'Francisco Steven Arias Pérez', 184),
        ('Diagrama de Arquitectura Funcional SPL', 'SESION-01', 'DIAGRAM', 'Francisco Steven Arias Pérez', 420),
        ('Especificación de Banderas en settings.py y urls.py', 'SESION-02', 'SPEC', 'Darly Douglas Farías Mendoza', 142),
        ('Matriz de Variantes PRODUCT_A vs PRODUCT_B', 'SESION-03', 'REPORT', 'Darly Douglas Farías Mendoza', 216),
    ]
    for title, tag, cat, author, size in files_data:
        Attachment.objects.update_or_create(
            title=title,
            defaults={
                'reference_tag': tag,
                'category': cat,
                'uploaded_by': author,
                'size_kb': size,
            },
        )

    print('>> Sembrando alertas en app opcional [notifications]...')
    notifs_data = [
        ('Variante B activada correctamente', 'Las características ENABLE_REPORTS y ENABLE_NOTIFICATIONS están habilitadas en config_product.py.', 'SUCCESS', 'Todos', False),
        ('Validación de aislamiento completada', 'El módulo de reportes opera como app independiente sin acoplamiento rígido en urls.py.', 'INFO', 'Administrador SPL', False),
        ('Pendiente revisión de documentación final', 'Recuerde adjuntar las capturas de Variante A y Variante B en el informe de la Sesión 4.', 'WARNING', 'Estudiantes', False),
        ('Migraciones de base de datos sincronizadas', 'Tablas de accounts, file_manager, core y notifications creadas en db.sqlite3.', 'INFO', 'Equipo Dev', True),
    ]
    for title, msg, level, role, is_read in notifs_data:
        SystemNotification.objects.get_or_create(
            title=title,
            defaults={
                'message': msg,
                'level': level,
                'target_role': role,
                'is_read': is_read,
            },
        )

    print('>> Base de datos inicializada con éxito.')


if __name__ == '__main__':
    seed_database()

