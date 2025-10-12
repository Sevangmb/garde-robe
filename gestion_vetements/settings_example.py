# EXAMPLE SETTINGS FILE
# Copy this file to settings.py and configure with your values

# Database Configuration Examples

# SQLite (Development - Default)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PostgreSQL (Production)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'your_database_name',
#         'USER': 'your_database_user',
#         'PASSWORD': 'your_database_password',
#         'HOST': 'your_database_host',  # e.g., '192.168.1.30' or 'localhost'
#         'PORT': '5432',
#     }
# }

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-secret-key-here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  # Change this in production

# CSRF trusted origins (for mobile app)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    # Add your local network IPs or production domains here
]
