# SESIÓN 4 – Documentación y línea de productos

**Responsable:** Darly Douglas Farías Mendoza  

## 1. Preguntas de Análisis de la Línea de Productos
- **¿Qué tienen en común todas las variantes?** El núcleo `core/`, las apps reutilizables `accounts/` y `file_manager/`, la base de datos SQLite y la estructura visual base.
- **¿Qué cambia entre ellas?** La activación de `reports/` (`ENABLE_REPORTS`) y `notifications/` (`ENABLE_NOTIFICATIONS`) definidas en `config_product.py`.
- **¿Qué patrón de reutilización usaron?** Arquitectura modular basada en componentes desacoplados (apps Django portables / Modelo RiSE) + *Feature Toggles* y configuración centralizada de variantes con `include()` condicional.

## 2. Productos Entregables de la Sesión 4
- **Manual PDF Oficial:** `Manual_Linea_de_Productos_basada_en_Django.pdf`
- **Diagramas de Variabilidad SPL:**
  - Modelo de Características (FODA): `diagramas/03_modelo_caracteristicas_spl.png` y `.drawio`
  - Árbol de Decisiones: `diagramas/04_arbol_decisiones_variantes.png` y `.drawio`
- **Tabla de Variantes, Conclusiones y Recomendaciones Individuales:** Ver `INFORME_COMPLETO_LISTO_PARA_COPIAR.md`.

