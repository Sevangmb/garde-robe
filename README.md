# 👔 Ma Garde-Robe

Une application web Django moderne et complète pour gérer sa garde-robe personnelle, créer des tenues, planifier ses voyages et partager avec ses amis.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.1+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Fonctionnalités

### 👕 Gestion de Garde-Robe
- **Catalogue complet** : Ajoutez vos vêtements avec photos, catégories, couleurs, tailles
- **Tracking intelligent** : Suivez le nombre de fois porté, calculez le coût par portage
- **Organisation pratique** : Marquez vos favoris, gérez l'entretien (à laver, à repasser, à réparer)
- **Statistiques détaillées** : Visualisez vos dépenses, vos habitudes de portage

### 👗 Création de Tenues
- **Tenues complètes** : Composez des looks avec plusieurs vêtements
- **Widget Fring** : Interface visuelle de création de tenues en 3 sections (haut/bas/chaussures)
- **Organisation** : Classez par occasion (travail, soirée, sport) et saison
- **Favoris et tracking** : Sauvegardez vos meilleures tenues et suivez leur utilisation

### 🧳 Valises de Voyage
- **Planification voyage** : Créez des valises pour vos déplacements
- **Gestion intelligente** : Ajoutez vêtements individuels ou tenues complètes
- **Informations contextuelles** : Destination, dates, météo prévue, climat
- **Statuts et organisation** : En préparation, prête, en cours, terminée
- **Réutilisation facile** : Copiez une valise pour un nouveau voyage similaire
- **Checklist** : Validez que tout est prêt avant le départ

### 💬 Fonctionnalités Sociales
- **Système d'amitié** : Ajoutez des amis, gérez les demandes
- **Messagerie** : Échangez des messages avec vos contacts
- **Partage** : Créez des tenues avec les vêtements de vos amis

### 🛒 Marketplace
- **Vente de vêtements** : Mettez en vente vos articles
- **Recherche avancée** : Filtres par catégorie, couleur, taille, prix, état
- **Système de favoris** : Sauvegardez les annonces qui vous intéressent
- **Transactions sécurisées** : Historique des achats/ventes
- **Évaluations** : Notez les vendeurs après transaction

### 📊 Dashboard et Analytics
- **KPIs personnalisés** : Total vêtements, favoris, dépenses, portages
- **Graphiques interactifs** : Distribution par catégorie, couleur, saison
- **Analyses intelligentes** : Identifiez les vêtements peu portés, optimisez votre garde-robe
- **Rentabilité** : Calculez le coût par portage de chaque vêtement

### 🛡️ Administration
- **Interface admin complète** : Gestion de tous les modèles
- **Accès restreint** : Réservé aux superutilisateurs
- **Actions personnalisées** : Incrémentation portage, gestion statuts, modération
- **Statistiques globales** : Vue d'ensemble de la plateforme

## 🛠️ Technologies

### Backend
- **Django 5.1+** - Framework web Python
- **SQLite** - Base de données (développement)
- **Python 3.11+** - Langage de programmation
- **Pillow** - Traitement d'images

### Frontend
- **HTML5/CSS3** - Structure et style
- **JavaScript** - Interactivité
- **Chart.js** - Graphiques et statistiques
- **Responsive Design** - Compatible mobile/tablette/desktop

## 📦 Installation

### Prérequis
- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)
- Git

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone <url-du-repo>
cd garde-robe
```

2. **Créer un environnement virtuel**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Appliquer les migrations**
```bash
python manage.py migrate
```

5. **Peupler avec des données de démonstration (optionnel)**
```bash
python populate_demo_data.py
```

6. **Créer un compte admin (optionnel)**
```bash
python create_admin.py
```

7. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

8. **Accéder à l'application**
- Interface utilisateur : http://localhost:8000/
- Interface admin : http://localhost:8000/admin/

## 👤 Comptes de démonstration

### Administrateur
- **Username** : `admin`
- **Password** : `admin123`
- **Accès** : Interface admin complète

### Utilisateurs
- **Username** : `marie` | **Password** : `demo123`
  - Garde-robe complète (23 vêtements)
  - 6 tenues créées
  - 4 valises (futures, en cours, passées)

- **Username** : `sophie` | **Password** : `demo123`
  - Amie de Marie
  - Annonces marketplace

- **Username** : `julie` | **Password** : `demo123`
  - Demande d'amitié en attente

## 📁 Structure du projet

```
garde-robe/
├── gestion_vetements/          # Configuration Django
│   ├── settings.py             # Paramètres du projet
│   ├── urls.py                 # URLs racine
│   └── wsgi.py                 # Configuration WSGI
│
├── vetements/                  # Application principale
│   ├── models.py               # 13 modèles (Vetement, Tenue, Valise, etc.)
│   ├── views.py                # 40+ vues
│   ├── urls.py                 # 60+ routes
│   ├── admin.py                # Admin personnalisé
│   ├── forms.py                # Formulaires (Valise, etc.)
│   ├── middleware.py           # Middleware sécurité
│   │
│   ├── templates/vetements/    # 35+ templates HTML
│   │   ├── base.html
│   │   ├── accueil.html
│   │   ├── liste_vetements.html
│   │   ├── tenues_list.html
│   │   ├── valises_list.html
│   │   ├── fring_widget.html
│   │   └── ...
│   │
│   └── migrations/             # 8 migrations
│
├── static/                     # Fichiers statiques (CSS, JS)
├── media/                      # Fichiers uploadés (photos)
│
├── create_admin.py             # Script création admin
├── populate_demo_data.py       # Script données de démo
├── manage.py                   # Utilitaire Django
├── requirements.txt            # Dépendances Python
└── README.md                   # Ce fichier
```

## 🔌 Endpoints principaux

### Authentification
- `POST /register/` - Inscription
- `POST /login/` - Connexion
- `GET /logout/` - Déconnexion

### Garde-Robe
- `GET /` - Dashboard
- `GET /vetements/` - Liste des vêtements
- `GET /vetements/<id>/` - Détail d'un vêtement
- `GET /entretien/` - Vêtements à entretenir

### Tenues
- `GET /tenues/` - Liste des tenues
- `GET /tenues/<id>/` - Détail d'une tenue
- `GET /fring/` - Widget Fring (créateur de tenues)

### Valises
- `GET /valises/` - Liste des valises
- `GET /valises/<id>/` - Détail d'une valise
- `POST /valises/creer/` - Créer une valise
- `POST /valises/<id>/modifier/` - Modifier une valise
- `POST /valises/<id>/copier/` - Copier une valise

### Social & Marketplace
- `GET /messages/` - Messagerie
- `GET /amis/` - Système d'amitié
- `GET /marketplace/` - Marketplace

## 🚀 Utilisation rapide

1. **Connexion** avec `marie/demo123`
2. **Ajouter un vêtement** : Menu Garde-Robe → Ajouter
3. **Créer une tenue** : Menu Tenues → Nouvelle tenue ou Widget Fring
4. **Préparer une valise** : Menu Valises → Nouvelle valise
5. **Explorer** : Dashboard, Statistiques, Marketplace

## 🙏 Remerciements

- Django Software Foundation
- Communauté open source
- Claude Code par Anthropic

---

**⭐ Ma Garde-Robe - Gérez votre style avec intelligence**
