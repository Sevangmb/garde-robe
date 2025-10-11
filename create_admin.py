#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour créer ou mettre à jour le compte administrateur
"""

import os
import sys
import django

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vetements.settings')
django.setup()

from django.contrib.auth.models import User

def create_or_update_admin():
    """Créer ou mettre à jour le compte admin"""

    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123'

    try:
        # Essayer de récupérer l'utilisateur existant
        admin = User.objects.get(username=username)
        print(f"✓ Utilisateur '{username}' trouvé, mise à jour du mot de passe...")
        admin.set_password(password)
        admin.is_staff = True
        admin.is_superuser = True
        admin.email = email
        admin.save()
        print(f"✓ Mot de passe mis à jour pour '{username}'")
    except User.DoesNotExist:
        # Créer un nouveau superutilisateur
        admin = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✓ Superutilisateur '{username}' créé avec succès!")

    print("\n" + "=" * 50)
    print("  COMPTE ADMINISTRATEUR")
    print("=" * 50)
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"  Email: {email}")
    print("=" * 50)
    print("\nVous pouvez vous connecter à l'admin: http://localhost:8000/admin/")

if __name__ == '__main__':
    create_or_update_admin()
