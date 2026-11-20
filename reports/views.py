import csv
from io import BytesIO
from django.conf import settings
from django.db.models import Avg, Count, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import render
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from core.models import AcademicProject


def _ensure_reports_enabled():
    """Resguardo adicional por si las rutas se invocan con la bandera desactivada."""
    if not settings.ENABLE_REPORTS:
        raise Http404('El módulo opcional de reportes está desactivado en esta variante.')


def reports_dashboard(request):
    """Panel ejecutivo de reportes (funcionalidad aislada de la Sesión 2)."""
    _ensure_reports_enabled()
    projects = AcademicProject.objects.all()
    by_category = (
        projects.values('category')
        .annotate(total=Count('id'), avg_progress=Avg('progress'), total_budget=Sum('budget_usd'))
        .order_by('category')
    )
    by_status = (
        projects.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )
    total_budget = projects.aggregate(total=Sum('budget_usd'))['total'] or 0

    return render(
        request,
        'reports/dashboard.html',
        {
            'projects': projects,
            'by_category': by_category,
            'by_status': by_status,
            'total_budget': total_budget,
        },
    )


def export_projects_pdf(request):
    """Genera un reporte PDF profesional de los proyectos registrados usando ReportLab."""
    _ensure_reports_enabled()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title='Reporte Ejecutivo de Proyectos SPL')
    styles = getSampleStyleSheet()

    elements = [
        Paragraph('UNEMI — Facultad de Ciencias e Ingeniería', styles['Heading3']),
        Paragraph('Reporte Consolidado de Proyectos (Módulo Opcional SPL)', styles['Title']),
        Paragraph(
            f'Variante activa: {settings.ACTIVE_VARIANT} ({settings.ACTIVE_CONFIG.get("NAME", "")}) | '
            f'ENABLE_REPORTS = {settings.ENABLE_REPORTS}',
            styles['Normal'],
        ),
        Spacer(1, 16),
    ]

    data = [['Código', 'Proyecto', 'Categoría', 'Responsable', 'Estado', 'Avance', 'Presupuesto']]
    for p in AcademicProject.objects.all():
        data.append([
            p.code,
            p.title[:34] + ('...' if len(p.title) > 34 else ''),
            p.get_category_display(),
            p.leader[:20],
            p.get_status_display(),
            f'{p.progress}%',
            f'${p.budget_usd:,.2f}',
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B2545')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_proyectos_spl.pdf"'
    return response


def export_projects_csv(request):
    """Exporta los proyectos a formato CSV compatible con Excel."""
    _ensure_reports_enabled()
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reporte_proyectos_spl.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Código', 'Título', 'Categoría', 'Responsable', 'Estado', 'Avance (%)', 'Presupuesto (USD)', 'Fecha Entrega'])
    for p in AcademicProject.objects.all():
        writer.writerow([
            p.code,
            p.title,
            p.get_category_display(),
            p.leader,
            p.get_status_display(),
            p.progress,
            f'{p.budget_usd:.2f}',
            p.delivery_date.isoformat(),
        ])
    return response
