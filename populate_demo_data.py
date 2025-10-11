#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de peuplement de la base de données avec des données de démonstration
Pour l'application Ma Garde-Robe
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_vetements.settings')
django.setup()

from django.contrib.auth.models import User
from vetements.models import (
    Categorie, Couleur, Taille, Vetement, Tenue, Valise,
    Message, Amitie, AnnonceVente, ParametresSite
)

def clear_data():
    """Nettoyer toutes les données existantes (sauf superusers)"""
    print("🧹 Nettoyage des données existantes...")

    # Supprimer les données dans l'ordre (respecter les dépendances)
    Valise.objects.all().delete()
    Tenue.objects.all().delete()
    AnnonceVente.objects.all().delete()
    Message.objects.all().delete()
    Amitie.objects.all().delete()
    Vetement.objects.all().delete()

    # Supprimer les utilisateurs non-superusers
    User.objects.filter(is_superuser=False).delete()

    print("✅ Données nettoyées")


def create_users():
    """Créer des utilisateurs de démonstration"""
    print("\n👥 Création des utilisateurs...")

    users = []

    # Utilisateur principal de démonstration
    user1, created = User.objects.get_or_create(
        username='marie',
        defaults={
            'email': 'marie@example.com',
            'first_name': 'Marie',
            'last_name': 'Dupont',
            'is_active': True
        }
    )
    if created:
        user1.set_password('demo123')
        user1.save()
    users.append(user1)

    # Autres utilisateurs
    user2, created = User.objects.get_or_create(
        username='sophie',
        defaults={
            'email': 'sophie@example.com',
            'first_name': 'Sophie',
            'last_name': 'Martin',
            'is_active': True
        }
    )
    if created:
        user2.set_password('demo123')
        user2.save()
    users.append(user2)

    user3, created = User.objects.get_or_create(
        username='julie',
        defaults={
            'email': 'julie@example.com',
            'first_name': 'Julie',
            'last_name': 'Petit',
            'is_active': True
        }
    )
    if created:
        user3.set_password('demo123')
        user3.save()
    users.append(user3)

    print(f"✅ {len(users)} utilisateurs créés")
    return users


def create_categories():
    """Créer les catégories de vêtements"""
    print("\n📂 Création des catégories...")

    categories_data = [
        ('T-shirt', 'T-shirts et tops à manches courtes'),
        ('Chemise', 'Chemises et chemisiers'),
        ('Pull', 'Pulls et sweaters'),
        ('Sweat', 'Sweats et hoodies'),
        ('Veste', 'Vestes légères et blazers'),
        ('Manteau', 'Manteaux et parkas'),
        ('Pantalon', 'Pantalons classiques et chinos'),
        ('Jean', 'Jeans et denims'),
        ('Short', 'Shorts et bermudas'),
        ('Jupe', 'Jupes'),
        ('Robe', 'Robes'),
        ('Basket', 'Baskets et sneakers'),
        ('Chaussure', 'Chaussures habillées'),
        ('Botte', 'Bottes et bottines'),
        ('Sandale', 'Sandales'),
        ('Accessoire', 'Accessoires divers'),
    ]

    categories = []
    for nom, desc in categories_data:
        cat, created = Categorie.objects.get_or_create(
            nom=nom,
            defaults={'description': desc}
        )
        categories.append(cat)

    print(f"✅ {len(categories)} catégories créées")
    return categories


def create_couleurs():
    """Créer les couleurs"""
    print("\n🎨 Création des couleurs...")

    couleurs_data = [
        ('Noir', '#000000'),
        ('Blanc', '#FFFFFF'),
        ('Gris', '#808080'),
        ('Bleu marine', '#000080'),
        ('Bleu ciel', '#87CEEB'),
        ('Rouge', '#FF0000'),
        ('Rose', '#FFC0CB'),
        ('Vert', '#008000'),
        ('Jaune', '#FFFF00'),
        ('Orange', '#FFA500'),
        ('Violet', '#800080'),
        ('Marron', '#8B4513'),
        ('Beige', '#F5F5DC'),
        ('Kaki', '#C3B091'),
    ]

    couleurs = []
    for nom, code in couleurs_data:
        couleur, created = Couleur.objects.get_or_create(
            nom=nom,
            defaults={'code_hex': code}
        )
        couleurs.append(couleur)

    print(f"✅ {len(couleurs)} couleurs créées")
    return couleurs


def create_tailles():
    """Créer les tailles"""
    print("\n📏 Création des tailles...")

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
        ('44', 'numerique', 14),
        ('46', 'numerique', 15),
    ]

    tailles = []
    for nom, type_t, ordre in tailles_data:
        taille, created = Taille.objects.get_or_create(
            nom=nom,
            defaults={'type_taille': type_t, 'ordre': ordre}
        )
        tailles.append(taille)

    print(f"✅ {len(tailles)} tailles créées")
    return tailles


def create_vetements(users, categories, couleurs, tailles):
    """Créer des vêtements de démonstration"""
    print("\n👕 Création des vêtements...")

    marie = users[0]

    vetements_data = [
        # T-shirts
        {
            'nom': 'T-shirt blanc basique',
            'categorie': 'T-shirt',
            'couleur': 'Blanc',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'H&M',
            'prix_achat': 9.99,
            'etat': 'bon',
            'nombre_portage': 15,
            'favori': True,
        },
        {
            'nom': 'T-shirt rayé marine et blanc',
            'categorie': 'T-shirt',
            'couleur': 'Bleu marine',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'printemps',
            'marque': 'Petit Bateau',
            'prix_achat': 29.99,
            'etat': 'excellent',
            'nombre_portage': 8,
            'favori': True,
        },
        {
            'nom': 'T-shirt noir col V',
            'categorie': 'T-shirt',
            'couleur': 'Noir',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Zara',
            'prix_achat': 12.99,
            'etat': 'bon',
            'nombre_portage': 12,
        },
        # Chemises
        {
            'nom': 'Chemise blanche Oxford',
            'categorie': 'Chemise',
            'couleur': 'Blanc',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Uniqlo',
            'prix_achat': 39.90,
            'etat': 'excellent',
            'nombre_portage': 6,
        },
        {
            'nom': 'Chemise en jean',
            'categorie': 'Chemise',
            'couleur': 'Bleu ciel',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'printemps',
            'marque': 'Levi\'s',
            'prix_achat': 59.90,
            'etat': 'bon',
            'nombre_portage': 10,
            'favori': True,
        },
        # Pulls
        {
            'nom': 'Pull en laine gris',
            'categorie': 'Pull',
            'couleur': 'Gris',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'hiver',
            'marque': 'COS',
            'prix_achat': 79.00,
            'etat': 'excellent',
            'nombre_portage': 20,
            'favori': True,
        },
        {
            'nom': 'Pull cachemire rose',
            'categorie': 'Pull',
            'couleur': 'Rose',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'hiver',
            'marque': 'Eric Bompard',
            'prix_achat': 149.00,
            'etat': 'excellent',
            'nombre_portage': 18,
            'favori': True,
        },
        # Vestes et Manteaux
        {
            'nom': 'Veste en jean vintage',
            'categorie': 'Veste',
            'couleur': 'Bleu ciel',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'printemps',
            'marque': 'Levi\'s',
            'prix_achat': 89.90,
            'etat': 'bon',
            'nombre_portage': 25,
            'favori': True,
        },
        {
            'nom': 'Blazer noir classique',
            'categorie': 'Veste',
            'couleur': 'Noir',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Mango',
            'prix_achat': 79.99,
            'etat': 'excellent',
            'nombre_portage': 15,
            'favori': True,
        },
        {
            'nom': 'Manteau en laine beige',
            'categorie': 'Manteau',
            'couleur': 'Beige',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'hiver',
            'marque': 'Comptoir des Cotonniers',
            'prix_achat': 249.00,
            'etat': 'excellent',
            'nombre_portage': 30,
            'favori': True,
        },
        # Pantalons et Jeans
        {
            'nom': 'Jean slim brut',
            'categorie': 'Jean',
            'couleur': 'Bleu marine',
            'taille': '38',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Levi\'s 721',
            'prix_achat': 99.90,
            'etat': 'bon',
            'nombre_portage': 40,
            'favori': True,
        },
        {
            'nom': 'Jean mom fit noir',
            'categorie': 'Jean',
            'couleur': 'Noir',
            'taille': '38',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Monki',
            'prix_achat': 49.99,
            'etat': 'excellent',
            'nombre_portage': 22,
            'favori': True,
        },
        {
            'nom': 'Pantalon tailleur noir',
            'categorie': 'Pantalon',
            'couleur': 'Noir',
            'taille': '38',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Zara',
            'prix_achat': 39.99,
            'etat': 'excellent',
            'nombre_portage': 18,
        },
        {
            'nom': 'Pantalon chino beige',
            'categorie': 'Pantalon',
            'couleur': 'Beige',
            'taille': '38',
            'genre': 'femme',
            'saison': 'printemps',
            'marque': 'Uniqlo',
            'prix_achat': 29.90,
            'etat': 'bon',
            'nombre_portage': 12,
        },
        # Shorts et Jupes
        {
            'nom': 'Short en jean délavé',
            'categorie': 'Short',
            'couleur': 'Bleu ciel',
            'taille': '38',
            'genre': 'femme',
            'saison': 'ete',
            'marque': 'Levi\'s',
            'prix_achat': 49.90,
            'etat': 'bon',
            'nombre_portage': 8,
        },
        {
            'nom': 'Jupe midi plissée noire',
            'categorie': 'Jupe',
            'couleur': 'Noir',
            'taille': '38',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Mango',
            'prix_achat': 35.99,
            'etat': 'excellent',
            'nombre_portage': 10,
        },
        # Robes
        {
            'nom': 'Robe d\'été fleurie',
            'categorie': 'Robe',
            'couleur': 'Rose',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'ete',
            'marque': '& Other Stories',
            'prix_achat': 79.00,
            'etat': 'excellent',
            'nombre_portage': 5,
        },
        {
            'nom': 'Robe noire cocktail',
            'categorie': 'Robe',
            'couleur': 'Noir',
            'taille': 'M',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Sandro',
            'prix_achat': 195.00,
            'etat': 'neuf',
            'nombre_portage': 2,
        },
        # Chaussures
        {
            'nom': 'Baskets blanches en cuir',
            'categorie': 'Basket',
            'couleur': 'Blanc',
            'taille': '38',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Stan Smith',
            'prix_achat': 99.99,
            'etat': 'bon',
            'nombre_portage': 50,
            'favori': True,
        },
        {
            'nom': 'Baskets running noires',
            'categorie': 'Basket',
            'couleur': 'Noir',
            'taille': '38',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Nike Air',
            'prix_achat': 129.99,
            'etat': 'bon',
            'nombre_portage': 30,
        },
        {
            'nom': 'Bottines en cuir marron',
            'categorie': 'Botte',
            'couleur': 'Marron',
            'taille': '38',
            'genre': 'femme',
            'saison': 'hiver',
            'marque': 'Minelli',
            'prix_achat': 139.00,
            'etat': 'excellent',
            'nombre_portage': 20,
            'favori': True,
        },
        {
            'nom': 'Sandales plates beiges',
            'categorie': 'Sandale',
            'couleur': 'Beige',
            'taille': '38',
            'genre': 'femme',
            'saison': 'ete',
            'marque': 'Birkenstock',
            'prix_achat': 89.90,
            'etat': 'bon',
            'nombre_portage': 25,
        },
        {
            'nom': 'Escarpins noirs en cuir',
            'categorie': 'Chaussure',
            'couleur': 'Noir',
            'taille': '38',
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Jonak',
            'prix_achat': 119.00,
            'etat': 'excellent',
            'nombre_portage': 8,
        },
    ]

    vetements = []
    cat_dict = {c.nom: c for c in categories}
    couleur_dict = {c.nom: c for c in couleurs}
    taille_dict = {t.nom: t for t in tailles}

    today = date.today()

    for v_data in vetements_data:
        cat = cat_dict.get(v_data['categorie'])
        couleur = couleur_dict.get(v_data['couleur'])
        taille = taille_dict.get(v_data['taille'])

        if cat and couleur and taille:
            vetement = Vetement.objects.create(
                proprietaire=marie,
                nom=v_data['nom'],
                categorie=cat,
                couleur=couleur,
                taille=taille,
                genre=v_data['genre'],
                saison=v_data['saison'],
                marque=v_data.get('marque', ''),
                prix_achat=Decimal(str(v_data.get('prix_achat', 0))),
                date_achat=today - timedelta(days=v_data.get('nombre_portage', 0) * 7),
                etat=v_data['etat'],
                nombre_portage=v_data.get('nombre_portage', 0),
                derniere_utilisation=today - timedelta(days=5) if v_data.get('nombre_portage', 0) > 0 else None,
                favori=v_data.get('favori', False),
                a_laver=v_data.get('nombre_portage', 0) >= 3 and v_data.get('nombre_portage', 0) % 3 == 0,
            )
            vetements.append(vetement)

    print(f"✅ {len(vetements)} vêtements créés pour {marie.username}")
    return vetements


def create_tenues(marie, vetements):
    """Créer des tenues de démonstration"""
    print("\n👗 Création des tenues...")

    tenues_data = [
        {
            'nom': 'Tenue bureau classique',
            'occasion': 'travail',
            'saison': 'toute_saison',
            'vetements': ['Chemise blanche Oxford', 'Pantalon tailleur noir', 'Escarpins noirs en cuir'],
            'favori': True,
            'nombre_fois_portee': 15,
        },
        {
            'nom': 'Look casual weekend',
            'occasion': 'decontracte',
            'saison': 'printemps',
            'vetements': ['T-shirt blanc basique', 'Jean slim brut', 'Baskets blanches en cuir', 'Veste en jean vintage'],
            'favori': True,
            'nombre_fois_portee': 20,
        },
        {
            'nom': 'Tenue soirée chic',
            'occasion': 'soiree',
            'saison': 'toute_saison',
            'vetements': ['Robe noire cocktail', 'Escarpins noirs en cuir'],
            'favori': True,
            'nombre_fois_portee': 3,
        },
        {
            'nom': 'Look hiver confortable',
            'occasion': 'decontracte',
            'saison': 'hiver',
            'vetements': ['Pull en laine gris', 'Jean mom fit noir', 'Bottines en cuir marron', 'Manteau en laine beige'],
            'favori': True,
            'nombre_fois_portee': 25,
        },
        {
            'nom': 'Tenue été décontractée',
            'occasion': 'decontracte',
            'saison': 'ete',
            'vetements': ['Robe d\'été fleurie', 'Sandales plates beiges'],
            'favori': False,
            'nombre_fois_portee': 5,
        },
        {
            'nom': 'Smart casual bureau',
            'occasion': 'travail',
            'saison': 'toute_saison',
            'vetements': ['Chemise en jean', 'Pantalon chino beige', 'Baskets blanches en cuir', 'Blazer noir classique'],
            'favori': True,
            'nombre_fois_portee': 12,
        },
    ]

    vetements_dict = {v.nom: v for v in vetements}
    tenues = []
    today = date.today()

    for t_data in tenues_data:
        tenue = Tenue.objects.create(
            proprietaire=marie,
            nom=t_data['nom'],
            occasion=t_data['occasion'],
            saison=t_data['saison'],
            favori=t_data.get('favori', False),
            nombre_fois_portee=t_data.get('nombre_fois_portee', 0),
            derniere_fois_portee=today - timedelta(days=10) if t_data.get('nombre_fois_portee', 0) > 0 else None,
        )

        # Ajouter les vêtements à la tenue
        for v_nom in t_data['vetements']:
            vetement = vetements_dict.get(v_nom)
            if vetement:
                tenue.vetements.add(vetement)

        tenues.append(tenue)

    print(f"✅ {len(tenues)} tenues créées")
    return tenues


def create_valises(marie, vetements, tenues):
    """Créer des valises de démonstration"""
    print("\n🧳 Création des valises...")

    today = date.today()

    valises_data = [
        {
            'nom': 'Week-end Normandie',
            'destination': 'Deauville',
            'type_voyage': 'weekend',
            'date_depart': today + timedelta(days=15),
            'date_retour': today + timedelta(days=17),
            'meteo_prevue': 'Nuageux 18°C',
            'climat': 'tempere',
            'statut': 'preparation',
            'vetements': [
                'T-shirt blanc basique',
                'T-shirt rayé marine et blanc',
                'Jean slim brut',
                'Pull en laine gris',
                'Veste en jean vintage',
                'Baskets blanches en cuir',
            ],
            'tenues': ['Look casual weekend'],
            'liste_articles_supplementaires': 'Trousse de toilette\nChargeur téléphone\nLivre\nParapluie',
            'notes': 'Réserver restaurant pour samedi soir',
        },
        {
            'nom': 'Vacances Barcelone',
            'destination': 'Barcelone, Espagne',
            'type_voyage': 'vacances',
            'date_depart': today + timedelta(days=45),
            'date_retour': today + timedelta(days=52),
            'meteo_prevue': 'Ensoleillé 28°C',
            'climat': 'chaud',
            'statut': 'preparation',
            'vetements': [
                'T-shirt blanc basique',
                'T-shirt rayé marine et blanc',
                'T-shirt noir col V',
                'Short en jean délavé',
                'Jean slim brut',
                'Robe d\'été fleurie',
                'Sandales plates beiges',
                'Baskets blanches en cuir',
            ],
            'tenues': ['Tenue été décontractée'],
            'liste_articles_supplementaires': 'Crème solaire SPF50\nLunettes de soleil\nMaillot de bain\nServiette de plage\nGourde\nGuide touristique',
            'notes': 'Prévoir tickets Sagrada Familia\nRéserver tapas tour',
        },
        {
            'nom': 'Déplacement pro Paris',
            'destination': 'Paris',
            'type_voyage': 'professionnel',
            'date_depart': today + timedelta(days=7),
            'date_retour': today + timedelta(days=9),
            'meteo_prevue': 'Variable 15°C',
            'climat': 'tempere',
            'statut': 'prete',
            'vetements': [
                'Chemise blanche Oxford',
                'Blazer noir classique',
                'Pantalon tailleur noir',
                'Escarpins noirs en cuir',
                'Pull cachemire rose',
                'Jean mom fit noir',
                'Baskets blanches en cuir',
            ],
            'tenues': ['Tenue bureau classique', 'Smart casual bureau'],
            'liste_articles_supplementaires': 'Ordinateur portable\nChargeurs\nDocuments de présentation\nCartes de visite',
            'notes': 'Réunion mardi 9h - confirmer',
            'checklist_faite': True,
        },
        {
            'nom': 'Ski Alpes - Janvier dernier',
            'destination': 'Courchevel',
            'type_voyage': 'vacances',
            'date_depart': today - timedelta(days=60),
            'date_retour': today - timedelta(days=53),
            'meteo_prevue': 'Neige -5°C',
            'climat': 'montagne',
            'statut': 'terminee',
            'vetements': [
                'Pull en laine gris',
                'Pull cachemire rose',
                'Jean mom fit noir',
                'Manteau en laine beige',
                'Bottines en cuir marron',
            ],
            'tenues': ['Look hiver confortable'],
            'liste_articles_supplementaires': 'Équipement de ski\nCrème solaire montagne\nLunettes de ski\nGants\nBonnet',
            'notes': 'Super séjour! À refaire l\'année prochaine',
            'checklist_faite': True,
        },
    ]

    vetements_dict = {v.nom: v for v in vetements}
    tenues_dict = {t.nom: t for t in tenues}
    valises = []

    for v_data in valises_data:
        valise = Valise.objects.create(
            proprietaire=marie,
            nom=v_data['nom'],
            destination=v_data['destination'],
            type_voyage=v_data['type_voyage'],
            date_depart=v_data['date_depart'],
            date_retour=v_data['date_retour'],
            meteo_prevue=v_data.get('meteo_prevue', ''),
            climat=v_data.get('climat', ''),
            statut=v_data['statut'],
            liste_articles_supplementaires=v_data.get('liste_articles_supplementaires', ''),
            notes=v_data.get('notes', ''),
            checklist_faite=v_data.get('checklist_faite', False),
        )

        # Ajouter les vêtements
        for v_nom in v_data.get('vetements', []):
            vetement = vetements_dict.get(v_nom)
            if vetement:
                valise.vetements.add(vetement)

        # Ajouter les tenues
        for t_nom in v_data.get('tenues', []):
            tenue = tenues_dict.get(t_nom)
            if tenue:
                valise.tenues.add(tenue)

        valises.append(valise)

    print(f"✅ {len(valises)} valises créées")
    return valises


def create_friendships(users):
    """Créer des relations d'amitié"""
    print("\n🤝 Création des amitiés...")

    marie, sophie, julie = users[0], users[1], users[2]

    # Marie et Sophie sont amies
    Amitie.objects.get_or_create(
        demandeur=marie,
        destinataire=sophie,
        defaults={
            'statut': 'acceptee',
            'date_reponse': date.today() - timedelta(days=30)
        }
    )

    # Marie a une demande en attente avec Julie
    Amitie.objects.get_or_create(
        demandeur=marie,
        destinataire=julie,
        defaults={'statut': 'en_attente'}
    )

    print("✅ Amitiés créées")


def create_messages(users):
    """Créer des messages de démonstration"""
    print("\n💬 Création des messages...")

    marie, sophie, julie = users[0], users[1], users[2]
    today = date.today()

    # Message de Sophie à Marie
    Message.objects.create(
        expediteur=sophie,
        destinataire=marie,
        sujet='Re: Ta robe noire',
        contenu='Coucou ! J\'ai adoré ta robe hier soir, elle te va super bien ! Tu l\'as achetée où ?',
        lu=False,
        date_envoi=today - timedelta(days=1)
    )

    # Message de Marie à Sophie
    Message.objects.create(
        expediteur=marie,
        destinataire=sophie,
        sujet='Tenue pour samedi ?',
        contenu='Salut ! On se voit toujours samedi ? Tu comptes mettre quoi ? Je sais pas encore si je mets une robe ou un jean...',
        lu=True,
        date_envoi=today - timedelta(days=3),
        date_lecture=today - timedelta(days=2)
    )

    print("✅ Messages créés")


def create_marketplace(users, vetements):
    """Créer des annonces marketplace"""
    print("\n🛒 Création des annonces marketplace...")

    sophie = users[1]

    # Sophie vend quelques vêtements
    vetements_sophie = [
        {
            'nom': 'Veste en cuir noire',
            'categorie': Categorie.objects.get(nom='Veste'),
            'couleur': Couleur.objects.get(nom='Noir'),
            'taille': Taille.objects.get(nom='M'),
            'genre': 'femme',
            'saison': 'toute_saison',
            'marque': 'Mango',
            'etat': 'bon',
        },
        {
            'nom': 'Jupe plissée rose poudré',
            'categorie': Categorie.objects.get(nom='Jupe'),
            'couleur': Couleur.objects.get(nom='Rose'),
            'taille': Taille.objects.get(nom='38'),
            'genre': 'femme',
            'saison': 'printemps',
            'marque': 'Zara',
            'etat': 'excellent',
        },
    ]

    for v_data in vetements_sophie:
        vetement = Vetement.objects.create(
            proprietaire=sophie,
            **v_data
        )

        AnnonceVente.objects.create(
            vetement=vetement,
            vendeur=sophie,
            prix_vente=Decimal('35.00'),
            description_vente='En très bon état, porté quelques fois seulement',
            statut='en_vente',
            negociable=True,
            livraison_possible=True,
        )

    print("✅ Annonces marketplace créées")


def create_site_params():
    """Créer ou mettre à jour les paramètres du site"""
    print("\n⚙️ Configuration des paramètres du site...")

    params, created = ParametresSite.objects.get_or_create(
        pk=1,
        defaults={
            'nom_site': 'Ma Garde-Robe',
            'description_site': 'Gérez votre garde-robe personnelle',
            'inscription_ouverte': True,
            'messages_actifs': True,
            'annonces_actives': True,
            'amitie_active': True,
        }
    )

    print("✅ Paramètres du site configurés")


def main():
    """Fonction principale"""
    print("=" * 60)
    print("  PEUPLEMENT DE LA BASE DE DONNÉES - MA GARDE-ROBE")
    print("=" * 60)

    # Demander confirmation
    response = input("\n⚠️  Cela va supprimer toutes les données existantes. Continuer ? (oui/non): ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        return

    # Nettoyer les données existantes
    clear_data()

    # Créer les données
    users = create_users()
    categories = create_categories()
    couleurs = create_couleurs()
    tailles = create_tailles()
    vetements = create_vetements(users, categories, couleurs, tailles)
    tenues = create_tenues(users[0], vetements)
    valises = create_valises(users[0], vetements, tenues)
    create_friendships(users)
    create_messages(users)
    create_marketplace(users, vetements)
    create_site_params()

    print("\n" + "=" * 60)
    print("  ✅ PEUPLEMENT TERMINÉ AVEC SUCCÈS!")
    print("=" * 60)
    print("\n📊 Récapitulatif:")
    print(f"  - {User.objects.filter(is_superuser=False).count()} utilisateurs créés")
    print(f"  - {Categorie.objects.count()} catégories")
    print(f"  - {Couleur.objects.count()} couleurs")
    print(f"  - {Taille.objects.count()} tailles")
    print(f"  - {Vetement.objects.count()} vêtements")
    print(f"  - {Tenue.objects.count()} tenues")
    print(f"  - {Valise.objects.count()} valises")
    print(f"  - {Message.objects.count()} messages")
    print(f"  - {Amitie.objects.count()} relations d'amitié")
    print(f"  - {AnnonceVente.objects.count()} annonces marketplace")

    print("\n👤 Comptes de démonstration:")
    print("  - Username: marie | Password: demo123")
    print("  - Username: sophie | Password: demo123")
    print("  - Username: julie | Password: demo123")

    print("\n🚀 Vous pouvez maintenant vous connecter et explorer l'application!")
    print("=" * 60)


if __name__ == '__main__':
    main()
