from datetime import date
from importlib import reload
from django.conf import settings
from django.test import Client, TestCase, override_settings
import spl_project.urls as root_urls
from core.models import AcademicProject


class SPLCoreTests(TestCase):
    """Pruebas unitarias y de integración del comportamiento SPL."""

    def setUp(self):
        self.client = Client()
        AcademicProject.objects.create(
            code='TEST-001',
            title='Proyecto Prueba Variabilidad',
            category='SPL',
            leader='Francisco Arias',
            status='EN_CURSO',
            progress=80,
            budget_usd=1000.00,
            delivery_date=date(2026, 12, 10),
        )

    def test_dashboard_loads_and_reusable_apps_work(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/accounts/').status_code, 200)
        self.assertEqual(self.client.get('/files/').status_code, 200)
        self.assertEqual(self.client.get('/spl-architecture/').status_code, 200)

    def test_conditional_reports_toggle_with_url_reload(self):
        with override_settings(ENABLE_REPORTS=False, ENABLE_NOTIFICATIONS=False):
            reload(root_urls)
            resp = self.client.get('/')
            self.assertEqual(resp.status_code, 200)
            self.assertNotContains(resp, 'Exportar Reporte PDF')
            self.assertEqual(self.client.get('/reports/').status_code, 404)
            self.assertEqual(self.client.get('/notifications/').status_code, 404)

        with override_settings(ENABLE_REPORTS=True):
            reload(root_urls)
            resp = self.client.get('/')
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, 'Exportar Reporte PDF')
            if 'reports' in settings.INSTALLED_APPS:
                self.assertEqual(self.client.get('/reports/').status_code, 200)
                pdf_resp = self.client.get('/reports/export/pdf/')
                self.assertEqual(pdf_resp.status_code, 200)
                self.assertEqual(pdf_resp['Content-Type'], 'application/pdf')

        # Restaurar estado original de urlpatterns para no contaminar otras pruebas
        reload(root_urls)

