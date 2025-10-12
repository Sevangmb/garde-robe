# Configuration de la base de données

## PostgreSQL (Production - Recommandé)

### Prérequis
- PostgreSQL 17+ installé (serveur Unraid ou local)
- Driver Python installé : `pip install psycopg2-binary`

### Configuration dans settings.py

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'garde_robe_db',
        'USER': 'postgres',
        'PASSWORD': 'VOTRE_MOT_DE_PASSE',
        'HOST': '192.168.1.30',  # Remplacer par votre IP
        'PORT': '5432',
    }
}
```

### Création de la base de données

```bash
# Se connecter à PostgreSQL
psql -U postgres -h 192.168.1.30

# Créer la base
CREATE DATABASE garde_robe_db ENCODING 'UTF8';

# Quitter
\q
```

### Migrations

```bash
# Créer les tables
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

## SQLite (Développement)

Pour le développement local, SQLite est utilisé par défaut :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Aucune configuration supplémentaire requise.

## Variables d'environnement (Recommandé pour production)

Créer un fichier `.env` :

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=garde_robe_db
DB_USER=postgres
DB_PASSWORD=VOTRE_MOT_DE_PASSE
DB_HOST=192.168.1.30
DB_PORT=5432
SECRET_KEY=votre-clé-secrète
DEBUG=False
```

Puis dans `settings.py` :

```python
import os
from pathlib import Path

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
    }
}

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
```
