"""Configuración de variabilidad para la Línea de Productos de Software (SPL).

Define los perfiles de producto (variantes) según la Guía de Práctica 4:
- PRODUCT_A: Variante básica sin funcionalidades opcionales extendidas.
- PRODUCT_B: Variante completa con reportes y notificaciones habilitadas.
"""

import os

PRODUCT_A = {
    'NAME': 'Variante A — Sistema Básico',
    'CODE': 'PRODUCT_A',
    'DESCRIPTION': 'Núcleo académico y componentes reutilizables esenciales sin módulos extendidos.',
    'ENABLE_REPORTS': False,
    'ENABLE_NOTIFICATIONS': False,
}

PRODUCT_B = {
    'NAME': 'Variante B — Sistema Completo',
    'CODE': 'PRODUCT_B',
    'DESCRIPTION': 'Sistema completo con exportación de reportes PDF/CSV y centro de notificaciones.',
    'ENABLE_REPORTS': True,
    'ENABLE_NOTIFICATIONS': True,
}

VARIANTS = {
    'PRODUCT_A': PRODUCT_A,
    'PRODUCT_B': PRODUCT_B,
}

# Variante predeterminada si no se especifica la variable de entorno SPL_VARIANT.
# Puede cambiarse manualmente aquí entre 'PRODUCT_A' y 'PRODUCT_B'.
DEFAULT_VARIANT = 'PRODUCT_B'


def get_active_variant_name(variant_name=None):
    """Obtiene el código de la variante activa validado contra VARIANTS."""
    selected = (variant_name or os.environ.get('SPL_VARIANT') or DEFAULT_VARIANT).strip().upper()
    if selected not in VARIANTS:
        valid = ', '.join(sorted(VARIANTS.keys()))
        raise ValueError(f"Variante SPL desconocida '{selected}'. Opciones válidas: {valid}")
    return selected


def get_product_config(variant_name=None):
    """Retorna el diccionario de configuración de características para la variante activa."""
    selected = get_active_variant_name(variant_name)
    return VARIANTS[selected].copy()
