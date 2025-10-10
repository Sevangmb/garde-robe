#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour créer des données de démonstration pour l'application garde-robe
À exécuter avec: python setup_demo_data.py
"""

import os
import sys
import django

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vetements.settings')
django.setup()

from django.contrib.auth.models import User
from vetements.models import Categorie, Couleur, Taille, Vetement, Tenue
from datetime import date, timedelta

print("Creation des donnees de demonstration...")

# Créer un superutilisateur si n'existe pas
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("OK Superutilisateur cree: admin / admin123")
else:
    print("INFO: Superutilisateur 'admin' existe deja")

# Créer les catégories
categories_data = [
    ('T-shirt', 'T-shirts et hauts à manches courtes'),
    ('Pantalon', 'Pantalons et jeans'),
    ('Pull', 'Pulls et sweats'),
    ('Chemise', 'Chemises et blouses'),
    ('Robe', 'Robes'),
    ('Veste', 'Vestes et manteaux'),
    ('Short', 'Shorts et bermudas'),
    ('Chaussures', 'Chaussures et baskets'),
]

categories = {}
for nom, desc in categories_data:
    cat, created = Categorie.objects.get_or_create(nom=nom, defaults={'description': desc})
    categories[nom] = cat
    if created:
        print(f"OK Categorie creee: {nom}")

# Créer les couleurs
couleurs_data = [
    ('Noir', '#000000'),
    ('Blanc', '#FFFFFF'),
    ('Bleu', '#0066CC'),
    ('Rouge', '#CC0000'),
    ('Vert', '#00CC00'),
    ('Gris', '#808080'),
    ('Beige', '#D2B48C'),
    ('Rose', '#FF69B4'),
    ('Jaune', '#FFFF00'),
    ('Marron', '#8B4513'),
]

couleurs = {}
for nom, code in couleurs_data:
    couleur, created = Couleur.objects.get_or_create(nom=nom, defaults={'code_hex': code})
    couleurs[nom] = couleur
    if created:
        print(f"OK Couleur creee: {nom}")

# Créer les tailles
tailles_data = [
    ('XS', 'standard', 1),
    ('S', 'standard', 2),
    ('M', 'standard', 3),
    ('L', 'standard', 4),
    ('XL', 'standard', 5),
    ('XXL', 'standard', 6),
    ('36', 'numerique', 10),
    ('38', 'numerique', 11),
    ('40', 'numerique', 12),
    ('42', 'numerique', 13),
]

tailles = {}
for nom, type_t, ordre in tailles_data:
    taille, created = Taille.objects.get_or_create(
        nom=nom,
        defaults={'type_taille': type_t, 'ordre': ordre}
    )
    tailles[nom] = taille
    if created:
        print(f"OK Taille creee: {nom}")

# Créer quelques vêtements
vetements_data = [
    {
        'nom': 'T-shirt blanc basique',
        'categorie': categories['T-shirt'],
        'genre': 'unisexe',
        'saison': 'toute_saison',
        'couleur': couleurs['Blanc'],
        'taille': tailles['M'],
        'marque': 'H&M',
        'prix_achat': 9.99,
        'date_achat': date.today() - timedelta(days=180),
        'lieu_achat': 'H&M Centre Commercial',
        'etat': 'bon',
        'favori': True,
        'nombre_portage': 25,
        'derniere_utilisation': date.today() - timedelta(days=3),
        'emplacement': 'Armoire chambre',
    },
    {
        'nom': 'Jean bleu slim',
        'categorie': categories['Pantalon'],
        'genre': 'homme',
        'saison': 'toute_saison',
        'couleur': couleurs['Bleu'],
        'taille': tailles['42'],
        'marque': "Levi's",
        'prix_achat': 79.90,
        'date_achat': date.today() - timedelta(days=365),
        'lieu_achat': "Levi's Store",
        'etat': 'excellent',
        'favori': True,
        'nombre_portage': 45,
        'derniere_utilisation': date.today() - timedelta(days=1),
        'emplacement': 'Armoire chambre',
    },
    {
        'nom': 'Pull noir col rond',
        'categorie': categories['Pull'],
        'genre': 'homme',
        'saison': 'hiver',
        'couleur': couleurs['Noir'],
        'taille': tailles['L'],
        'marque': 'Uniqlo',
        'prix_achat': 29.90,
        'date_achat': date.today() - timedelta(days=90),
        'lieu_achat': 'Uniqlo en ligne',
        'etat': 'neuf',
        'favori': False,
        'nombre_portage': 8,
        'derniere_utilisation': date.today() - timedelta(days=10),
        'emplacement': 'Armoire chambre',
    },
    {
        'nom': 'Chemise blanche Oxford',
        'categorie': categories['Chemise'],
        'genre': 'homme',
        'saison': 'toute_saison',
        'couleur': couleurs['Blanc'],
        'taille': tailles['M'],
        'marque': 'Zara',
        'prix_achat': 35.00,
        'etat': 'bon',
        'favori': False,
        'nombre_portage': 12,
        'a_repasser': True,
        'emplacement': 'Penderie',
    },
    {
        'nom': 'Veste en jean',
        'categorie': categories['Veste'],
        'genre': 'unisexe',
        'saison': 'printemps',
        'couleur': couleurs['Bleu'],
        'taille': tailles['L'],
        'marque': "Levi's",
        'prix_achat': 89.00,
        'date_achat': date.today() - timedelta(days=200),
        'etat': 'excellent',
        'favori': True,
        'nombre_portage': 15,
        'emplacement': 'Entrée',
    },
    {
        'nom': 'Short beige chino',
        'categorie': categories['Short'],
        'genre': 'homme',
        'saison': 'ete',
        'couleur': couleurs['Beige'],
        'taille': tailles['40'],
        'marque': 'Gap',
        'prix_achat': 39.90,
        'etat': 'bon',
        'favori': False,
        'nombre_portage': 2,
        'emplacement': 'Tiroir',
    },
    {
        'nom': 'Robe rouge été',
        'categorie': categories['Robe'],
        'genre': 'femme',
        'saison': 'ete',
        'couleur': couleurs['Rouge'],
        'taille': tailles['38'],
        'marque': 'Mango',
        'prix_achat': 45.00,
        'etat': 'excellent',
        'favori': True,
        'nombre_portage': 5,
        'a_laver': True,
        'emplacement': 'Armoire',
    },
    {
        'nom': 'Pull gris chiné',
        'categorie': categories['Pull'],
        'genre': 'unisexe',
        'saison': 'automne',
        'couleur': couleurs['Gris'],
        'taille': tailles['M'],
        'marque': 'Celio',
        'prix_achat': 25.00,
        'etat': 'usage',
        'favori': False,
        'nombre_portage': 30,
        'derniere_utilisation': date.today() - timedelta(days=15),
        'emplacement': 'Armoire',
    },
]

vetements_crees = []
for data in vetements_data:
    vet, created = Vetement.objects.get_or_create(
        nom=data['nom'],
        defaults=data
    )
    vetements_crees.append(vet)
    if created:
        print(f"OK Vetement cree: {data['nom']}")

# Créer quelques tenues
if len(vetements_crees) >= 3:
    tenue1, created = Tenue.objects.get_or_create(
        nom='Decontracte weekend',
        defaults={
            'description': 'Tenue confortable pour le weekend',
            'occasion': 'decontracte',
            'saison': 'toute_saison',
            'favori': True,
            'nombre_fois_portee': 8,
        }
    )
    if created:
        # T-shirt blanc + jean + veste
        tenue1.vetements.add(vetements_crees[0], vetements_crees[1], vetements_crees[4])
        print(f"OK Tenue creee: {tenue1.nom}")

    tenue2, created = Tenue.objects.get_or_create(
        nom='Bureau formel',
        defaults={
            'description': 'Tenue professionnelle pour le bureau',
            'occasion': 'travail',
            'saison': 'toute_saison',
            'favori': False,
            'nombre_fois_portee': 3,
        }
    )
    if created:
        # Chemise + pantalon
        tenue2.vetements.add(vetements_crees[3], vetements_crees[1])
        print(f"OK Tenue creee: {tenue2.nom}")

print("\nDonnees de demonstration creees avec succes!")
print("\nInformations de connexion:")
print("   URL: http://localhost:8000/admin/")
print("   Utilisateur: admin")
print("   Mot de passe: admin123")
print("\nVous pouvez maintenant lancer le serveur avec: python manage.py runserver")
