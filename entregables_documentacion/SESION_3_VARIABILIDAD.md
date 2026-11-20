# SESIÓN 3 – Configuración de variabilidad

**Responsable:** Francisco Steven Arias Pérez  

## 1. Simulación de Variantes en `config_product.py`
- **Variante A (`PRODUCT_A`):** Sistema básico (`ENABLE_REPORTS: False`, `ENABLE_NOTIFICATIONS: False`).
- **Variante B (`PRODUCT_B`):** Sistema completo (`ENABLE_REPORTS: True`, `ENABLE_NOTIFICATIONS: True`).

## 2. Integración en `settings.py` y `urls.py`
- `spl_project/settings.py` consulta `get_product_config()` desde `config_product.py` usando la variable `SPL_VARIANT`.
- `spl_project/urls.py` usa `include()` condicional:
  ```python
  if settings.ENABLE_REPORTS:
      urlpatterns.append(path('reports/', include('reports.urls')))
  if settings.ENABLE_NOTIFICATIONS:
      urlpatterns.append(path('notifications/', include('notifications.urls')))
  ```

## 3. Productos Entregables de la Sesión 3
- **Captura Variante A (Sistema Básico):** `capturas/03_sesion3_variante_A_sistema_basico.png`
- **Captura Variante B (Sistema Completo):** `capturas/04_sesion3_variante_B_sistema_completo.png`
- **Capturas de módulos extendidos en B:** `capturas/05_sesion3_vista_reportes_y_pdf.png` y `capturas/06_sesion3_vista_notificaciones.png`
- **Anexos exportados reales:** `anexos/reporte_proyectos_spl_ejemplo.pdf` y `anexos/reporte_proyectos_spl_ejemplo.csv`
- **Verificación automatizada (`scripts/verify_spl.py`):** Variante A retorna `404` en rutas opcionales; Variante B retorna `200 OK` y descarga PDF/CSV válidos.

