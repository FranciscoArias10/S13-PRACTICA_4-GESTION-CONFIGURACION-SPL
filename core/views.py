from datetime import date
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.db.models import Avg
from django.shortcuts import redirect, render
from accounts.models import UserProfile
from file_manager.models import Attachment
from .models import AcademicProject


def dashboard_view(request):
    """Vista principal del sistema con control condicional de funcionalidades SPL."""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'SPL').strip()
        leader = request.POST.get('leader', '').strip()
        status = request.POST.get('status', 'EN_CURSO').strip()
        progress_raw = request.POST.get('progress', '25').strip()
        budget_raw = request.POST.get('budget_usd', '1500').strip()
        delivery_raw = request.POST.get('delivery_date', '').strip()
        description = request.POST.get('description', '').strip()

        if code and title and leader:
            try:
                progress = max(0, min(100, int(progress_raw)))
            except ValueError:
                progress = 25
            try:
                budget_usd = float(budget_raw)
            except ValueError:
                budget_usd = 1500.00
            delivery_date = date.fromisoformat(delivery_raw) if delivery_raw else date(2026, 12, 15)

            _, created = AcademicProject.objects.get_or_create(
                code=code,
                defaults={
                    'title': title,
                    'category': category,
                    'leader': leader,
                    'status': status,
                    'progress': progress,
                    'budget_usd': budget_usd,
                    'delivery_date': delivery_date,
                    'description': description,
                },
            )
            if created:
                messages.success(request, f'Proyecto "{code}" registrado correctamente en el núcleo.')
            else:
                messages.warning(request, f'El código "{code}" ya se encuentra registrado.')
        else:
            messages.error(request, 'Complete código, título y responsable del proyecto.')
        return redirect('core:dashboard')

    status_filter = request.GET.get('status', '').strip()
    projects = AcademicProject.objects.all()
    if status_filter:
        projects = projects.filter(status=status_filter)

    avg_progress = round(AcademicProject.objects.aggregate(avg=Avg('progress'))['avg'] or 0)

    context = {
        'projects': projects,
        'total_projects': AcademicProject.objects.count(),
        'completed_projects': AcademicProject.objects.filter(status='COMPLETADO').count(),
        'avg_progress': avg_progress,
        'total_users': UserProfile.objects.count(),
        'total_files': Attachment.objects.count(),
        'status_filter': status_filter,
        'status_choices': AcademicProject.STATUS_CHOICES,
        'category_choices': AcademicProject.CATEGORY_CHOICES,
        'reports_panel_enabled': False,
        'recent_notifications': [],
    }

    # Patrón explícito de la Sesión 2: bandera de configuración en views.py
    if settings.ENABLE_REPORTS:
        # Mostrar opción de exportar reportes en PDF y CSV
        context['reports_panel_enabled'] = True
        context['export_formats'] = ['PDF (ReportLab)', 'CSV (Excel)']

    # Patrón explícito de la Sesión 3: módulo opcional de notificaciones
    if settings.ENABLE_NOTIFICATIONS and apps.is_installed('notifications'):
        from notifications.models import SystemNotification
        context['recent_notifications'] = SystemNotification.objects.all()[:3]

    return render(request, 'core/dashboard.html', context)


def spl_architecture_view(request):
    """Vista informativa que documenta en vivo la arquitectura SPL y módulos activos."""
    module_matrix = [
        {
            'app': 'core',
            'tipo': 'Núcleo de Dominio (Core Asset)',
            'reutilizable': 'Base específica del producto',
            'activo': True,
            'flag': 'Siempre activo',
            'descripcion': 'Gestión central de proyectos académicos, métricas y tablero principal.',
        },
        {
            'app': 'accounts',
            'tipo': 'Componente Reutilizable',
            'reutilizable': 'Sí (Portabilidad 100%)',
            'activo': True,
            'flag': 'Siempre activo',
            'descripcion': 'Autenticación, perfiles institucionales y control de roles.',
        },
        {
            'app': 'file_manager',
            'tipo': 'Componente Reutilizable',
            'reutilizable': 'Sí (Portabilidad 100%)',
            'activo': True,
            'flag': 'Siempre activo',
            'descripcion': 'Carga y catálogo documental desacoplado mediante reference_tag.',
        },
        {
            'app': 'reports',
            'tipo': 'Funcionalidad Opcional (Sesión 2)',
            'reutilizable': 'Sí (Módulo plug-and-play)',
            'activo': settings.ENABLE_REPORTS,
            'flag': f'ENABLE_REPORTS = {settings.ENABLE_REPORTS}',
            'descripcion': 'Panel analítico y exportación a PDF/CSV activable por configuración.',
        },
        {
            'app': 'notifications',
            'tipo': 'Funcionalidad Opcional (Sesión 3)',
            'reutilizable': 'Sí (Módulo plug-and-play)',
            'activo': settings.ENABLE_NOTIFICATIONS,
            'flag': f'ENABLE_NOTIFICATIONS = {settings.ENABLE_NOTIFICATIONS}',
            'descripcion': 'Centro de alertas y avisos del sistema con ruteo condicional.',
        },
    ]

    return render(request, 'core/architecture.html', {'module_matrix': module_matrix})
