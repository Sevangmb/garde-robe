"""
Production settings for Ma Garde-Robe
Architecture hybride : Render (Django) + Unraid (PostgreSQL + Media)
"""

from .settings import *
from decouple import config, Csv

# SECURITY
DEBUG = False
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='garde-robe-rryt.onrender.com', cast=Csv())

# CSRF
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://garde-robe-rryt.onrender.com', cast=Csv())

# Database PostgreSQL sur Unraid (via tunnel Cloudflare ou DynDNS)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='garde_robe_db'),
        'USER': config('DB_USER', default='garde_robe_user'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),  # Ex: db.votredomaine.com
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# Stockage des médias sur nginx Unraid via SFTP
MEDIA_URL = config('MEDIA_URL', default='https://media.votredomaine.com/media/')
MEDIA_ROOT = '/tmp/media'  # Non utilisé en production, uploads gérés via SFTP

# Activer le backend SFTP pour les uploads
DEFAULT_FILE_STORAGE = 'vetements.storage.UnraidSFTPStorage'

# Configuration SFTP (à définir dans variables d'environnement Render)
# UNRAID_SFTP_HOST = '192.168.1.47' (ou via tunnel Cloudflare)
# UNRAID_SFTP_PORT = 22
# UNRAID_SFTP_USER = 'root'
# UNRAID_SFTP_PASSWORD = 'votre_mot_de_passe' (ou utiliser clé SSH)
# UNRAID_SFTP_KEY_PATH = '/path/to/ssh/key' (optionnel, préférable au mot de passe)
# UNRAID_MEDIA_PATH = '/mnt/user/appdata/garde-robe/media/'

# Security Headers
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'  # Override le ALLOWALL du dev

# CORS pour production (plus restrictif)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://votre-app.onrender.com',
    cast=Csv()
)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
