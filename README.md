# Práctica 4 — Línea de Productos de Software (SPL) en Django

**Asignatura:** Gestión de la Configuración de Software `[GESCONSOF]`  
**Guía:** `G004-S13-SOFTWARE2019-PRESENCIAL-GESTIÓN DE LA CONFIGURACIÓN DE SOFTWARE-B1`  
**Docente de Asignatura:** Ing. Lissett Margarita Arévalo Gamboa  
**Docente de Práctica:** Ing. Omar Andrés Oviedo Armijos  

## Integrantes del Grupo
- Francisco Steven Arias Pérez
- Darly Douglas Farías Mendoza

## Estructura SPL del Proyecto
- `config_product.py`: Define las variantes `PRODUCT_A` (sistema básico) y `PRODUCT_B` (sistema completo).
- `core/`: Núcleo obligatorio del sistema académico (`AcademicProject`, tablero principal, matriz SPL).
- `accounts/`: **App reutilizable** para gestión de usuarios y roles institucionales.
- `file_manager/`: **App reutilizable** para gestión documental desacoplada por etiquetas.
- `reports/`: **App opcional aislada** (Sesión 2) para analítica y exportación PDF (ReportLab) y CSV, controlada por `ENABLE_REPORTS`.
- `notifications/`: **App opcional aislada** (Sesión 3) para centro de notificaciones, controlada por `ENABLE_NOTIFICATIONS`.
- `entregables_documentacion/`: Contiene el Manual PDF requerido, el informe maestro listo para copiar a Word/PDF, diagramas (`.png` y `.drawio`) y capturas reales de ambas variantes.

## Cómo ejecutar cada variante

### Variante A (Sistema Básico — `ENABLE_REPORTS=False`, `ENABLE_NOTIFICATIONS=False`)
```bat
run_variante_a.bat
```
O desde terminal:
```powershell
$env:SPL_VARIANT="PRODUCT_A"
.\venv\Scripts\python.exe manage.py runserver 8001
```

### Variante B (Sistema Completo — `ENABLE_REPORTS=True`, `ENABLE_NOTIFICATIONS=True`)
```bat
run_variante_b.bat
```
O desde terminal:
```powershell
$env:SPL_VARIANT="PRODUCT_B"
.\venv\Scripts\python.exe manage.py runserver 8002
```

## Verificación automatizada
```powershell
.\venv\Scripts\python.exe manage.py test
.\venv\Scripts\python.exe scripts\verify_spl.py
```

