from pathlib import Path

# Ruta principal del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent


# CONFIGURACIÓN GENERAL

# Clave secreta utilizada por Django
SECRET_KEY = 'django-insecure-gaoej96w$!-h=k*9#o6mo)q916i13cb$%fe21ia$yt0j1r#8m='

# Durante el desarrollo permanece en True
DEBUG = True

# Equipos autorizados para acceder al proyecto
ALLOWED_HOSTS = []


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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bd_aurafit',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
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

# CLAVE PRIMARIA POR DEFECTO

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'