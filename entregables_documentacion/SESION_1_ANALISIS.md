# SESIÓN 1 – Identificación de componentes reutilizables

**Responsable:** Francisco Steven Arias Pérez  

## 1. Proyecto Django Seleccionado
- **Nombre:** Sistema Académico Modular de Proyectos (`spl_project`)
- **Ubicación:** `C:\Users\admin\Desktop\practica gestion`
- **Apps instaladas:** `accounts`, `file_manager`, `core`, `reports`, `notifications`

## 2. Hoja de Análisis de Funcionalidades
1. **Componentes reutilizables en otros proyectos:**
   - `accounts/`: Gestión de usuarios, perfiles y roles institucionales (`UserProfile`).
   - `file_manager/`: Carga, categorización y consulta de documentos (`Attachment`) mediante `reference_tag` genérico.
2. **Núcleo específico del sistema:**
   - `core/`: Gestión de proyectos académicos (`AcademicProject`), dashboard de métricas y procesador de contexto SPL.
3. **Funcionalidades opcionales (puntos de variabilidad):**
   - `reports/`: Panel de analítica y exportación en PDF (`ReportLab`) y CSV.
   - `notifications/`: Centro de notificaciones y alertas del sistema (`SystemNotification`).

## 3. Productos Entregables de la Sesión 1
- **Tabla comparativa:** Incluida en `INFORME_COMPLETO_LISTO_PARA_COPIAR.md`.
- **Diagrama de arquitectura de carpetas:** `diagramas/01_arquitectura_carpetas.png` y `.drawio`
- **Diagrama de arquitectura funcional:** `diagramas/02_arquitectura_funcional.png` y `.drawio`
- **Captura de matriz en vivo:** `capturas/07_sesion1_arquitectura_en_vivo.png`

