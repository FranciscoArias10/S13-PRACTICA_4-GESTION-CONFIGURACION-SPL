"""Verifica en procesos independientes las variantes PRODUCT_A, PRODUCT_B y bandera Sesión 2."""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PYTHON = sys.executable

CHECK_SNIPPET = """
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spl_project.settings')
django.setup()
from django.conf import settings
from django.test import Client

client = Client()
variant = settings.ACTIVE_VARIANT
reports = settings.ENABLE_REPORTS
notifs = settings.ENABLE_NOTIFICATIONS

dash = client.get('/')
assert dash.status_code == 200, f'Dashboard falló: {dash.status_code}'
html = dash.content.decode('utf-8')

acc = client.get('/accounts/')
files = client.get('/files/')
arch = client.get('/spl-architecture/')
assert acc.status_code == 200 and files.status_code == 200 and arch.status_code == 200

rep = client.get('/reports/')
rep_pdf = client.get('/reports/export/pdf/')
rep_csv = client.get('/reports/export/csv/')
notif = client.get('/notifications/')

if reports:
    assert 'Exportar Reporte PDF' in html, 'Debe mostrar opción Exportar PDF'
    assert rep.status_code == 200, f'/reports/ esperado 200, obtenido {rep.status_code}'
    assert rep_pdf.status_code == 200 and rep_pdf['Content-Type'] == 'application/pdf'
    assert rep_pdf.content.startswith(b'%PDF'), 'El PDF generado no tiene cabecera válida %PDF'
    assert rep_csv.status_code == 200 and 'text/csv' in rep_csv['Content-Type']
else:
    assert 'Exportar Reporte PDF' not in html, 'No debe mostrar Exportar PDF cuando ENABLE_REPORTS=False'
    assert rep.status_code == 404, f'/reports/ esperado 404, obtenido {rep.status_code}'

if notifs:
    assert 'Ir al Centro de Notificaciones' in html, 'Debe mostrar bloque de notificaciones'
    assert notif.status_code == 200, f'/notifications/ esperado 200, obtenido {notif.status_code}'
else:
    assert 'Ir al Centro de Notificaciones' not in html, 'No debe mostrar notificaciones cuando ENABLE_NOTIFICATIONS=False'
    assert notif.status_code == 404, f'/notifications/ esperado 404, obtenido {notif.status_code}'

print(
    f'OK [{variant}] ENABLE_REPORTS={reports} ENABLE_NOTIFICATIONS={notifs} | '
    f'dashboard={dash.status_code} reports={rep.status_code} pdf={rep_pdf.status_code} notifications={notif.status_code}'
)
"""


def run_case(label, extra_env):
    env = os.environ.copy()
    env.pop('SPL_VARIANT', None)
    env.pop('SPL_ENABLE_REPORTS', None)
    env.pop('SPL_ENABLE_NOTIFICATIONS', None)
    env.update(extra_env)

    result = subprocess.run(
        [PYTHON, '-c', CHECK_SNIPPET],
        cwd=str(BASE_DIR),
        env=env,
        capture_output=True,
        text=True,
    )
    print(f'=== {label} ===')
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)


if __name__ == '__main__':
    run_case('SESIÓN 3 — VARIANTE A (Sistema Básico)', {'SPL_VARIANT': 'PRODUCT_A'})
    run_case('SESIÓN 2 — AISLAMIENTO (Solo ENABLE_REPORTS=True)', {'SPL_VARIANT': 'PRODUCT_A', 'SPL_ENABLE_REPORTS': 'True'})
    run_case('SESIÓN 3 — VARIANTE B (Sistema Completo)', {'SPL_VARIANT': 'PRODUCT_B'})
    print('TODAS LAS VERIFICACIONES SPL PASARON CORRECTAMENTE.')

