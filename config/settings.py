from pathlib import Path
import os

# Ruta principal del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent


# CONFIGURACIÓN GENERAL

# Clave secreta utilizada por Django
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-gaoej96w$!-h=k*9#o6mo)q916i13cb$%fe21ia$yt0j1r#8m='
)

# Durante el desarrollo permanece en True (configurable vía DJANGO_DEBUG)
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('true', '1', 't')

# Equipos autorizados para acceder al proyecto (permitir localhost y 127.0.0.1 para pruebas Locust)
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]


# APLICACIONES INSTALADAS

INSTALLED_APPS = [

    # Aplicaciones propias de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones del proyecto AuraFit
    'apps.clientes',
    'apps.entrenadores',
    'apps.membresias',
    'apps.pagos',
    'apps.asistencias',
    'apps.evaluaciones',
]


# MIDDLEWARE

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# URLS PRINCIPALES

ROOT_URLCONF = 'config.urls'


# TEMPLATES

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        #carpeta templates
        'DIRS': [],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# WSGI

WSGI_APPLICATION = 'config.wsgi.application'

# BASE DE DATOS
# Por defecto usa PostgreSQL (bd_aurafit). Si no tienes PostgreSQL iniciado o deseas probar de inmediato,
# puedes activar SQLite definiendo la variable de entorno USE_SQLITE=True.

USE_SQLITE = os.getenv('USE_SQLITE', 'False').lower() in ('true', '1', 't')

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'CONN_MAX_AGE': 60,
            'OPTIONS': {
                'timeout': 60,  # Tiempo de espera extendido para evitar bloqueos bajo concurrencia
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'bd_aurafit'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', '123456'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': 60,
        }
    }


# VALIDADORES DE CONTRASEÑA

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Idioma del proyecto
LANGUAGE_CODE = 'es-pe'

# Zona horaria del Perú
TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_TZ = True

# ARCHIVOS ESTÁTICOS

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

try:
    import whitenoise  # noqa: F401
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
except ImportError:
    pass

# CLAVE PRIMARIA POR DEFECTO

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'