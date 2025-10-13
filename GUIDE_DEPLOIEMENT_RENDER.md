# Guide de Déploiement sur Render.com

Ce guide vous explique comment déployer votre application Django "Ma Garde-Robe" sur Render.com avec une base de données PostgreSQL gratuite.

## Prérequis

- Un compte GitHub avec le dépôt https://github.com/Sevangmb/garde-robe.git
- Un compte Render.com (gratuit) : https://render.com

## Étapes de Déploiement

### 1. Connexion à Render

1. Allez sur https://render.com
2. Connectez-vous avec votre compte GitHub
3. Autorisez Render à accéder à vos dépôts GitHub

### 2. Créer un Blueprint depuis render.yaml

Votre projet contient déjà un fichier `render.yaml` configuré. Render va l'utiliser pour créer automatiquement :
- Une base de données PostgreSQL (`garde-robe-db`)
- Un service web Python (`garde-robe`)

**Option A : Déploiement via Blueprint (Recommandé)**

1. Depuis le Dashboard Render, cliquez sur "New +"
2. Sélectionnez "Blueprint"
3. Connectez votre dépôt GitHub : `Sevangmb/garde-robe`
4. Render détectera automatiquement le fichier `render.yaml`
5. Cliquez sur "Apply" pour créer les ressources

**Option B : Déploiement Manuel**

Si le Blueprint ne fonctionne pas, vous pouvez créer les ressources manuellement :

#### Créer la Base de Données PostgreSQL

1. Cliquez sur "New +" → "PostgreSQL"
2. Configurez :
   - **Name** : `garde-robe-db`
   - **Database** : `garde_robe_db`
   - **User** : `garde_robe_user`
   - **Region** : Choisir la plus proche (Europe)
   - **Plan** : Free
3. Cliquez sur "Create Database"
4. Attendez que la base soit créée (1-2 minutes)

#### Créer le Service Web

1. Cliquez sur "New +" → "Web Service"
2. Connectez votre dépôt : `Sevangmb/garde-robe`
3. Configurez :
   - **Name** : `garde-robe`
   - **Region** : Même région que la base de données
   - **Branch** : `main`
   - **Root Directory** : (laisser vide)
   - **Runtime** : Python
   - **Build Command** : `./build.sh`
   - **Start Command** : `gunicorn gestion_vetements.wsgi:application`
   - **Plan** : Free

4. Variables d'environnement (section "Environment") :

   **Variables Obligatoires** :
   - `SECRET_KEY` : Cliquez sur "Generate Value" pour créer une clé secrète
   - `DEBUG` : `False`
   - `ALLOWED_HOSTS` : `.onrender.com,garde-robe.onrender.com` (remplacez par votre URL)
   - `DATABASE_URL` : Sélectionnez votre base `garde-robe-db` depuis le menu déroulant
   - `CSRF_TRUSTED_ORIGINS` : `https://garde-robe.onrender.com` (remplacez par votre URL)

5. Cliquez sur "Create Web Service"

### 3. Configuration Automatique

Le script `build.sh` va automatiquement :
- Installer les dépendances Python (`pip install -r requirements.txt`)
- Collecter les fichiers statiques (`collectstatic`)
- Appliquer les migrations de base de données (`migrate`)

### 4. Vérification du Déploiement

1. Attendez que le build soit terminé (5-10 minutes pour le premier déploiement)
2. Consultez les logs en temps réel dans le dashboard
3. Une fois déployé, cliquez sur l'URL de votre application (ex: `https://garde-robe.onrender.com`)

### 5. Créer un Superutilisateur

Pour accéder à l'interface d'administration Django :

1. Dans le dashboard Render, allez dans votre service web
2. Cliquez sur l'onglet "Shell"
3. Exécutez la commande :
   ```bash
   python manage.py createsuperuser
   ```
4. Suivez les instructions pour créer votre compte admin
5. Accédez à l'admin : `https://votre-app.onrender.com/admin/`

## Configuration Avancée

### Variables d'Environnement

Toutes les variables sont configurables via l'interface Render (Settings → Environment) :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SECRET_KEY` | Clé secrète Django | Généré automatiquement |
| `DEBUG` | Mode debug | `False` (production) |
| `ALLOWED_HOSTS` | Domaines autorisés | `.onrender.com,votredomaine.com` |
| `DATABASE_URL` | URL PostgreSQL | Fourni par Render |
| `CSRF_TRUSTED_ORIGINS` | Origines CSRF | `https://votreapp.onrender.com` |

### Domaine Personnalisé

1. Dans le dashboard Render → Settings → Custom Domain
2. Ajoutez votre domaine personnalisé
3. Configurez les DNS selon les instructions Render
4. Mettez à jour `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS`

### Fichiers Médias (Images)

**Note importante** : Sur le plan gratuit de Render, les fichiers uploadés (photos de vêtements) sont **éphémères** et seront supprimés à chaque redémarrage.

**Solutions** :
1. Utiliser un service de stockage externe (AWS S3, Cloudinary)
2. Passer à un plan payant avec persistent disk
3. Pour le développement, accepter la perte des images

## Surveillance et Maintenance

### Logs
- Consultez les logs en temps réel dans Dashboard → Logs
- Filtrez par type : Build, Deploy, Runtime

### Auto-Deploy
- Par défaut, Render redéploie automatiquement à chaque push sur `main`
- Désactivable dans Settings → Auto-Deploy

### Mises à Jour
Pour mettre à jour l'application :
```bash
git add .
git commit -m "Mise à jour"
git push origin main
```
Render redéploiera automatiquement.

## Dépannage

### Erreur de Build
- Vérifiez `requirements.txt` est à jour
- Consultez les logs de build pour identifier l'erreur
- Vérifiez que `build.sh` est exécutable

### Erreur de Migration
- Vérifiez la connexion à la base de données
- Essayez de relancer manuellement : Shell → `python manage.py migrate`

### Erreur 502 Bad Gateway
- Attendez quelques minutes (démarrage à froid sur plan gratuit)
- Vérifiez les logs pour identifier l'erreur

### Fichiers Statiques Non Chargés
- Vérifiez que `collectstatic` s'exécute dans `build.sh`
- Vérifiez la configuration WhiteNoise dans `settings.py`

## Limitations du Plan Gratuit

- **Démarrage à froid** : 50s de délai après 15 min d'inactivité
- **Bande passante** : 100 GB/mois
- **Build minutes** : 500 min/mois
- **Base de données** : 90 jours d'expiration (prolongeable gratuitement)
- **Fichiers uploadés** : Éphémères (supprimés au redémarrage)

## Migration des Données

### Depuis PostgreSQL Local

Si vous avez des données existantes sur votre serveur PostgreSQL local (192.168.1.30) :

1. **Dump de la base locale** :
   ```bash
   pg_dump -h 192.168.1.30 -U postgres -d garde_robe_db -F c -f backup.dump
   ```

2. **Restauration sur Render** :
   - Téléchargez les credentials de la base Render (Connection String)
   - Utilisez `pg_restore` avec l'URL fournie par Render :
   ```bash
   pg_restore -d <DATABASE_URL_RENDER> --clean --no-owner backup.dump
   ```

### Depuis SQLite

Si vous utilisiez SQLite :
1. Utilisez Django pour exporter/importer via fixtures
2. Ou utilisez un outil comme `pgloader`

## Support

- Documentation Render : https://render.com/docs
- Documentation Django : https://docs.djangoproject.com
- Dépôt GitHub : https://github.com/Sevangmb/garde-robe

## Checklist de Déploiement

- [ ] Code poussé sur GitHub
- [ ] Compte Render créé et connecté à GitHub
- [ ] Base de données PostgreSQL créée sur Render
- [ ] Service web créé et configuré
- [ ] Variables d'environnement configurées
- [ ] Build terminé avec succès
- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Application accessible via URL Render
- [ ] Interface admin fonctionnelle

🎉 Votre application est maintenant déployée sur Render !
