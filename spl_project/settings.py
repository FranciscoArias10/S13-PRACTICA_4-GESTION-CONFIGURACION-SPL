"""Configuración de Django para la Línea de Productos de Software (SPL)."""

import os
from pathlib import Path
from config_product import get_active_variant_name, get_product_config

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(env_name, default):
    """Permite sobrescribir una bandera booleana mediante variable de entorno."""
    raw = os.environ.get(env_name)
    if raw is None:
        return default
    return raw.strip().lower() in ('1', 'true', 'yes', 'on', 'si')


# ==============================================================================
# CONFIGURACIÓN DE VARIABILIDAD (SESIÓN 2 Y SESIÓN 3)
# ==============================================================================
ACTIVE_VARIANT = get_active_variant_name()
ACTIVE_CONFIG = get_product_config(ACTIVE_VARIANT)

ENABLE_REPORTS = _env_bool('SPL_ENABLE_REPORTS', ACTIVE_CONFIG['ENABLE_REPORTS'])
ENABLE_NOTIFICATIONS = _env_bool('SPL_ENABLE_NOTIFICATIONS', ACTIVE_CONFIG['ENABLE_NOTIFICATIONS'])

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-unemi-gesconsof-practica4-spl-clave-desarrollo-2026',
)

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

# ==============================================================================
# SEPARACIÓN MODULAR DE APPS (CORE ASSETS VS COMPONENTES OPCIONALES)
# ==============================================================================
REUSABLE_APPS = [
    'accounts',      # Componente reutilizable: gestión de usuarios y roles
    'file_manager',  # Componente reutilizable: carga y administración de archivos
]

CORE_APPS = [
    'core',          # Núcleo del sistema académico
]

OPTIONAL_APPS = []
if ENABLE_REPORTS:
    OPTIONAL_APPS.append('reports')        # Módulo opcional aislado (Sesión 2)
if ENABLE_NOTIFICATIONS:
    OPTIONAL_APPS.append('notifications')  # Módulo opcional aislado (Sesión 3)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    *REUSABLE_APPS,
    *CORE_APPS,
    *OPTIONAL_APPS,
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'spl_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.spl_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'spl_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
