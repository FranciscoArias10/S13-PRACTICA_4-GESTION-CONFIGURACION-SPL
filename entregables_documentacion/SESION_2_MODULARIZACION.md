# SESIÓN 2 – Modularización y separación de variantes

**Responsable sugerido:** Ezequiel Cristobal Jaramillo Yepez  

## 1. Acciones Ejecutadas
1. Se aisló la funcionalidad opcional de exportación de reportes en una aplicación Django independiente llamada `reports/` (`apps.py`, `views.py`, `urls.py`, `templates/reports/dashboard.html`).
2. Se implementó la bandera `ENABLE_REPORTS` en `spl_project/settings.py`.
3. Se condicionó la vista `core/views.py` mediante `if settings.ENABLE_REPORTS:` y las plantillas HTML mediante `{% if ENABLE_REPORTS %}`.

## 2. Fragmentos Clave Implementados
- `spl_project/settings.py`: controla si `'reports'` forma parte de `INSTALLED_APPS` a través de `ENABLE_REPORTS`.
- `core/views.py`: evalúa `if settings.ENABLE_REPORTS:` para habilitar la sección y formatos de exportación.
- `templates/base.html` y `core/templates/core/dashboard.html`: muestran u ocultan los botones `Exportar Reporte PDF` y `Exportar CSV`.

## 3. Productos Entregables de la Sesión 2
- **App separada:** `C:\Users\admin\Desktop\practica gestion\reports\`
- **Captura sin funcionalidad activada (`ENABLE_REPORTS = False`):** `capturas/01_sesion2_vista_sin_reportes.png`
- **Captura con funcionalidad activada (`ENABLE_REPORTS = True`):** `capturas/02_sesion2_vista_con_reportes.png`

