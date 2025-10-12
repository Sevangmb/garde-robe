# Guide de déploiement sur Render.com

## Prérequis
- Compte Render.com : https://dashboard.render.com/
- Code poussé sur GitHub

## Étapes de déploiement

### Option 1 : Déploiement automatique avec render.yaml (Recommandé)

1. **Connectez-vous à Render** : https://dashboard.render.com/

2. **Créer un nouveau service depuis un Blueprint**
   - Cliquez sur "New +"
   - Sélectionnez "Blueprint"
   - Connectez votre repository GitHub `Sevangmb/garde-robe`
   - Render détectera automatiquement le fichier `render.yaml`

3. **Variables d'environnement**
   Les variables seront créées automatiquement par le fichier `render.yaml`, mais vous devrez définir :
   - `ALLOWED_HOSTS` : Ajoutez votre domaine Render (ex: `garde-robe.onrender.com`)
   - `CSRF_TRUSTED_ORIGINS` : Ajoutez `https://garde-robe.onrender.com`

4. **Déploiement**
   - Cliquez sur "Apply" pour créer les services
   - Render créera automatiquement :
     - Une base de données PostgreSQL gratuite
     - Un service web avec votre application Django
   - Le déploiement prend environ 5-10 minutes

### Option 2 : Déploiement manuel

1. **Créer une base de données PostgreSQL**
   - Dashboard Render → "New +" → "PostgreSQL"
   - Name: `garde-robe-db`
   - Plan: Free
   - Créer la base de données
   - Copiez l'URL de connexion (Internal Database URL)

2. **Créer un Web Service**
   - Dashboard Render → "New +" → "Web Service"
   - Connectez votre repository GitHub
   - Configuration :
     - **Name**: `garde-robe`
     - **Runtime**: Python
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn gestion_vetements.wsgi:application`
     - **Plan**: Free

3. **Variables d'environnement**
   Dans l'onglet "Environment" du service :
   ```
   SECRET_KEY=<générez-une-clé-secrète-forte>
   DEBUG=False
   DATABASE_URL=<URL-de-votre-base-PostgreSQL>
   ALLOWED_HOSTS=<votre-domaine>.onrender.com
   CSRF_TRUSTED_ORIGINS=https://<votre-domaine>.onrender.com
   ```

4. **Déployer**
   - Cliquez sur "Create Web Service"
   - Le déploiement démarre automatiquement

## Configuration de l'app mobile

Une fois déployé, mettez à jour l'URL du serveur dans votre app mobile :

**Fichier**: `mobile-app/www/index.html`
```javascript
// Remplacez l'URL locale par votre URL Render
const SERVER_URL = 'https://garde-robe.onrender.com';
```

N'oubliez pas de :
1. Reconstruire l'APK avec la nouvelle URL
2. Ajouter l'URL Render dans `CSRF_TRUSTED_ORIGINS` sur Render

## Important : Plan gratuit Render

### Limitations
- Le service s'endort après 15 minutes d'inactivité
- Premier accès après inactivité : 30-60 secondes de délai
- 750 heures/mois de temps d'exécution gratuit
- Base de données PostgreSQL : 1 Go de stockage

### Recommandation
- Pour garder le service actif 24/7, utilisez un service de "keep-alive" (ping toutes les 10 minutes)
- Ou passez au plan payant ($7/mois) pour éviter l'endormissement

## Maintenance

### Mises à jour
Render redéploie automatiquement à chaque push sur GitHub.

### Logs
Accédez aux logs depuis le dashboard Render → Votre service → "Logs"

### Base de données
Pour se connecter à la base PostgreSQL depuis votre machine locale :
```bash
psql <EXTERNAL_DATABASE_URL>
```

## Connexion PostgreSQL Unraid + Render

Vous avez actuellement deux bases de données :
1. **PostgreSQL Unraid** (192.168.1.30) - Pour développement local
2. **PostgreSQL Render** - Pour production en ligne

Pour continuer à utiliser votre base Unraid en local :
- Gardez votre fichier `.env` actuel
- L'application utilisera automatiquement la base locale

Pour la production Render :
- Render utilisera automatiquement sa propre base PostgreSQL
- Définie via la variable `DATABASE_URL`

## Support

- Documentation Render : https://render.com/docs
- Support Render : https://render.com/support
