# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based personal wardrobe management application (`gestion_vetements`) using SQLite as the database. The application helps manage a personal clothing collection with support for tracking wear frequency, maintenance needs, outfit creation, and spending analysis. It includes both a web interface for viewing statistics and a Django admin interface for data management.

**Purpose**: Personal wardrobe organization, not commercial inventory management.

## Development Setup

### Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### Running the Development Server
```bash
python manage.py runserver
```

Access the application at `http://localhost:8000/`
Admin interface at `http://localhost:8000/admin/`

## Common Django Commands

### Database Operations
```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test vetements

# Run with verbosity
python manage.py test --verbosity=2
```

### Django Shell
```bash
# Open Django shell for testing queries
python manage.py shell
```

## Project Architecture

### Directory Structure
```
gestion_vetements/     # Django project configuration
├── settings.py        # Project settings (language: fr-fr, timezone: Europe/Paris)
├── urls.py            # Root URL configuration
└── wsgi.py

vetements/             # Main Django app
├── models.py          # Data models (Categorie, Couleur, Taille, Vetement, Tenue)
├── views.py           # View functions and class-based views
├── urls.py            # App URL patterns
├── admin.py           # Admin interface configuration with custom actions
├── templates/         # HTML templates
│   └── vetements/
│       ├── base.html
│       ├── accueil.html
│       ├── liste_vetements.html
│       ├── detail_vetement.html
│       ├── categorie.html
│       ├── entretien.html
│       ├── tenues_list.html
│       ├── tenue_detail.html
│       └── statistiques.html
└── migrations/        # Database migrations

static/                # Static files (CSS, JS, images)
└── css/
    └── style.css

media/                 # User-uploaded files (clothing and outfit photos)
├── vetements/
└── tenues/
```

### Data Models

#### Categorie
Categories of clothing (e.g., Pantalon, T-shirt, Robe)
- Fields: nom, description, date_creation

#### Couleur
Available colors with optional hex codes for visual representation
- Fields: nom, code_hex

#### Taille
Available sizes (XS, S, M, L, XL, numeric sizes like 36, 38, 40)
- Fields: nom, type_taille, ordre
- Types: standard, numerique, autre

#### Vetement (Main Model)
Individual clothing items in the wardrobe
- **Basic Info**: nom, description
- **Classification**: categorie (FK), genre (homme/femme/unisexe/enfant), saison
- **Characteristics**: couleur (FK), taille (FK), marque, matiere
- **Purchase Info**: prix_achat, date_achat, lieu_achat (all optional)
- **Usage Tracking**: etat, favori, nombre_portage, derniere_utilisation
- **Maintenance**: a_laver, a_repasser, prete, prete_a
- **Organization**: emplacement, notes, image
- **Properties**:
  - `cout_par_portage`: Cost per wear calculation
  - `peu_porte`: Flag for rarely worn items (<3 times)
  - `besoin_entretien`: Needs washing, ironing, or repair

#### Tenue (Outfit Model)
Saved outfit combinations composed of multiple clothing items
- **Basic Info**: nom, description, image
- **Characteristics**: occasion, saison, favori
- **Composition**: vetements (M2M relationship)
- **Usage**: nombre_fois_portee, derniere_fois_portee

### URL Routes

Main routes in `vetements/urls.py`:
- `/` - Dashboard with wardrobe statistics (accueil)
- `/vetements/` - Wardrobe catalog with filters (liste_vetements)
- `/vetements/<id>/` - Detailed clothing view (detail_vetement)
- `/categorie/<id>/` - Category-specific view (categorie)
- `/entretien/` - Maintenance page (items to wash, iron, repair, lent items)
- `/tenues/` - Saved outfits list (tenues_list)
- `/tenues/<id>/` - Outfit detail view (tenue_detail)
- `/statistiques/` - Detailed analytics (spending, wear frequency, cost per wear)
- `/admin/` - Django admin interface

### Views

Mix of function-based and class-based views:
- **accueil**: Dashboard with personal stats (favorites, items to wash, spending)
- **VetementListView**: Paginated wardrobe with filters (category, season, state, favorites)
- **VetementDetailView**: Detailed item information with wear tracking
- **vetements_par_categorie**: Category-specific listings
- **entretien**: Maintenance tracking (washing, ironing, repairs, lent items)
- **tenues_list**: List of saved outfits with filters
- **tenue_detail**: Outfit composition and details
- **statistiques**: Analytics dashboard (spending, wear frequency, cost per wear)

## Development Guidelines

### Model Changes
When modifying models:
1. Make changes to the model class in `vetements/models.py`
2. Run `python manage.py makemigrations`
3. Review the generated migration file
4. Run `python manage.py migrate`
5. Test the changes in Django shell or through the application

### Static Files
After modifying CSS/JS files:
```bash
python manage.py collectstatic
```

### Code Organization
- Keep models focused and follow Django naming conventions
- Use Django's ORM for database queries instead of raw SQL
- Implement model methods for business logic related to that model
- Use class-based views (CBVs) for common patterns, function-based views (FBVs) for complex logic
- All field verbose names and interface text are in French

### Admin Interface

The admin interface (`/admin/`) is fully configured with:

**Vetement Admin:**
- List display with icons: ⭐ (favorite), 🧺 (to wash), 👔 (to iron), 🔧 (to repair), 👤 (lent)
- Filters: category, gender, season, state, maintenance flags
- Search: name, brand, location, notes
- Custom actions:
  - Marquer comme à laver / Marquer comme lavé
  - Incrémenter le nombre de portages (also updates last wear date)
- Organized fieldsets for better data entry

**Tenue Admin:**
- List display with favorites and wear count
- Horizontal filter for selecting clothing items
- Custom action to increment wear count

**Couleur Admin:**
- Visual color preview in list display

## Key Features

### Personal Wardrobe Management
- Track individual clothing items with photos
- Record purchase information (price, date, store) - optional
- Monitor item condition and state
- Mark favorites for frequently worn items
- Track wear frequency with cost-per-wear calculations

### Maintenance Tracking
- Flag items that need washing (🧺)
- Flag items that need ironing (👔)
- Track items in need of repair (🔧)
- Monitor lent items and who has them (👤)

### Outfit Creation
- Create and save outfit combinations
- Categorize by occasion (work, sport, evening, casual, ceremony)
- Track outfit wear frequency
- Mark favorite outfits

### Analytics & Insights
- Total wardrobe value and spending
- Wear frequency statistics
- Cost per wear analysis
- Identify rarely worn items (optimization opportunities)
- Distribution by category, color, and season
- Most and least worn items

### Practical Use Cases
1. **Morning routine**: Browse saved outfits by occasion/season
2. **Laundry day**: Check entretien page for items to wash
3. **Shopping decisions**: Review statistics to identify wardrobe gaps
4. **Decluttering**: Find rarely worn items to donate/sell
5. **Value tracking**: Monitor cost per wear to justify purchases
6. **Organization**: Track where items are stored in your home

## Interface Language

All user-facing text, admin labels, and help text are in French. The application is designed for French-speaking users.
