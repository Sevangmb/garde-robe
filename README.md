# Ma Garde-Robe 👕👗

Application Django de gestion personnelle de garde-robe avec suivi des vêtements, création de tenues et analyses statistiques.

## Fonctionnalités

### 📦 Gestion des vêtements
- Cataloguez vos vêtements avec photos
- Enregistrez les informations d'achat (prix, date, magasin)
- Suivez l'état et la condition de chaque article
- Marquez vos favoris
- Suivez la fréquence de port avec calcul du coût par portage

### 🧺 Suivi d'entretien
- Vêtements à laver
- Vêtements à repasser
- Articles nécessitant réparation
- Suivi des vêtements prêtés

### 👔 Création de tenues
- Créez et sauvegardez des combinaisons de vêtements
- Catégorisez par occasion (travail, sport, soirée, etc.)
- Suivez la fréquence de port des tenues
- Marquez vos tenues favorites

### 📊 Analyses et statistiques
- Valeur totale de la garde-robe
- Statistiques de dépenses
- Analyse coût par portage
- Identification des articles peu portés
- Répartition par catégorie, couleur, saison

## Installation rapide

```bash
# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer les données de démonstration
python setup_demo_data.py

# Lancer le serveur
python manage.py runserver
```

## Accès à l'application

- **Interface web**: http://localhost:8000/
- **Interface admin**: http://localhost:8000/admin/
  - Utilisateur: `admin`
  - Mot de passe: `admin123`

## Pages principales

- `/` - Tableau de bord avec statistiques
- `/vetements/` - Catalogue de vêtements
- `/tenues/` - Liste des tenues
- `/entretien/` - Suivi d'entretien
- `/statistiques/` - Analyses détaillées
- `/admin/` - Interface d'administration

## Structure du projet

```
gestion_vetements/     # Configuration Django
vetements/             # Application principale
├── models.py          # Modèles (Vetement, Tenue, etc.)
├── views.py           # Vues et logique
├── admin.py           # Interface admin personnalisée
├── urls.py            # Routes
└── templates/         # Templates HTML
static/                # Fichiers CSS
media/                 # Photos uploadées
```

## Modèles de données

- **Categorie**: Types de vêtements (T-shirt, Pantalon, etc.)
- **Couleur**: Couleurs avec codes hexadécimaux
- **Taille**: Tailles standard ou numériques
- **Vetement**: Articles individuels avec suivi complet
- **Tenue**: Combinaisons de vêtements sauvegardées

## Actions admin utiles

Dans l'interface admin (`/admin/`), vous pouvez:
- Marquer plusieurs vêtements à laver en masse
- Incrémenter le nombre de portages automatiquement
- Filtrer par état, catégorie, saison, etc.
- Voir les indicateurs visuels (⭐🧺👔🔧👤)

## Technologies

- **Django 4.2+** - Framework web
- **SQLite** - Base de données
- **Pillow** - Gestion des images
- **Python 3.11+** - Langage

## Licence

Application personnelle pour usage privé.
