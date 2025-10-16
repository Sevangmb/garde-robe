#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input --settings=gestion_vetements.settings_prod

# Run migrations
python manage.py migrate --settings=gestion_vetements.settings_prod

# Create superuser automatically (only if it doesn't exist)
python create_admin.py
