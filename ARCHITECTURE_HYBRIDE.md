# Architecture Hybride : Render + Unraid

Configuration pour héberger Django sur Render avec PostgreSQL et stockage images sur Unraid.

## 🏗️ Architecture

```
┌─────────────────┐
│   Render.com    │ ← Django Web App (gratuit)
│   (Public)      │
└────────┬────────┘
         │
         ├─────→ PostgreSQL (Unraid 192.168.1.30:5432)
         │       ↓ Données persistantes
         │
         └─────→ Nginx Media Server (Unraid 192.168.1.47:80)
                 ↓ Images vêtements/tenues
```

## ✅ Avantages

- **Render** : Interface web accessible partout, SSL gratuit, auto-deploy
- **PostgreSQL Unraid** : Données 100% persistantes, backup local, contrôle total
- **Images Unraid** : Stockage illimité, persistant, backup inclus

## 📋 Installation

### 1️⃣ Configuration nginx sur Unraid

#### A. Ajouter un Path Mapping au container nginx

Dans l'interface Unraid du container nginx :
1. Cliquez sur "Add another Path"
2. Configurez :
   - **Config Type** : Path
   - **Name** : `media-garderobe`
   - **Container Path** : `/media/garde-robe`
   - **Host Path** : `/mnt/user/appdata/garde-robe/media`
   - **Access Mode** : Read Only
3. Cliquez "Apply"

#### B. Créer le dossier de stockage des images

Via SSH ou console Unraid :
```bash
mkdir -p /mnt/user/appdata/garde-robe/media/vetements
mkdir -p /mnt/user/appdata/garde-robe/media/tenues
chmod -R 755 /mnt/user/appdata/garde-robe/media
```

#### C. Installer la configuration nginx

1. Copiez le fichier `nginx-media-server.conf` vers Unraid :
   ```bash
   # Depuis votre PC Windows (PowerShell)
   scp nginx-media-server.conf root@192.168.1.47:/mnt/user/appdata/nginx/nginx/site-confs/media.conf
   ```

2. Ou créez directement sur Unraid :
   ```bash
   nano /mnt/user/appdata/nginx/nginx/site-confs/media.conf
   # Collez le contenu du fichier nginx-media-server.conf
   ```

#### D. Redémarrer nginx

Dans l'interface Unraid Docker :
1. Cliquez sur nginx → Stop
2. Attendez l'arrêt complet
3. Cliquez Start

#### E. Tester nginx

Depuis votre PC :
```bash
curl http://192.168.1.47/health
# Devrait retourner : OK

curl http://192.168.1.47/media/
# Devrait lister le contenu (ou 403 si vide)
```

### 2️⃣ Exposer PostgreSQL et nginx depuis Internet

Vous avez **2 options** pour rendre vos services accessibles depuis Render :

#### Option A : Cloudflare Tunnel (Recommandé - Gratuit et Sécurisé)

**Avantages** :
- ✅ Gratuit
- ✅ Pas besoin d'ouvrir de ports sur votre routeur
- ✅ Chiffrement automatique
- ✅ Protection DDoS incluse

**Installation** :
1. Créez un compte Cloudflare (gratuit)
2. Ajoutez votre domaine (ou utilisez un sous-domaine gratuit)
3. Installez cloudflared sur Unraid via Docker :

```bash
docker run -d \
  --name cloudflared \
  --network host \
  cloudflare/cloudflared:latest \
  tunnel --no-autoupdate run --token <VOTRE_TOKEN>
```

4. Créez 2 tunnels :
   - `db.votredomaine.com` → `192.168.1.30:5432`
   - `media.votredomaine.com` → `192.168.1.47:80`

**Configuration Cloudflare** :
- Dashboard → Zero Trust → Tunnels → Create Tunnel
- Suivez l'assistant pour obtenir votre token
- Configurez les routes publiques

#### Option B : Port Forwarding + DynDNS (Alternative)

**Si vous avez une IP publique fixe ou DynDNS** :

1. **Configurez DynDNS** (ex: No-IP, DuckDNS)
2. **Ouvrez les ports sur votre routeur** :
   - Port 5432 → 192.168.1.30:5432 (PostgreSQL)
   - Port 8080 → 192.168.1.47:80 (nginx media)

3. **Sécurisez PostgreSQL** :
   ```bash
   # Éditez pg_hba.conf pour autoriser uniquement Render
   # /mnt/user/appdata/postgres/data/pg_hba.conf
   host    garde_robe_db    garde_robe_user    <IP_RENDER>/32    scram-sha-256
   ```

⚠️ **Moins sécurisé que Cloudflare Tunnel**

#### Option C : VPN Tailscale/Wireguard (Pour les experts)

- Installez Tailscale sur Unraid et sur Render (via Docker sidecar)
- Connexion sécurisée point-à-point
- Complexe mais très sécurisé

### 3️⃣ Configuration Django (settings.py)

Créez un nouveau fichier de configuration pour la production :

```python
# gestion_vetements/settings_prod.py
from .settings import *

# Mode production
DEBUG = False
ALLOWED_HOSTS = ['.onrender.com', 'votre-app.onrender.com']

# Database PostgreSQL sur Unraid
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'garde_robe_db',
        'USER': 'garde_robe_user',
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),  # db.votredomaine.com ou IP publique
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',  # Si vous utilisez SSL
        },
    }
}

# Stockage des médias sur nginx Unraid
MEDIA_URL = 'https://media.votredomaine.com/media/'
MEDIA_ROOT = '/tmp/media'  # Non utilisé, juste pour compatibilité

# Utiliser un backend de stockage custom pour upload vers Unraid
# (nécessite configuration supplémentaire avec rsync/sftp)
```

### 4️⃣ Configuration Render

#### Variables d'environnement à configurer sur Render :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `DJANGO_SETTINGS_MODULE` | `gestion_vetements.settings_prod` | Utiliser settings prod |
| `SECRET_KEY` | `<généré>` | Clé secrète Django |
| `DEBUG` | `False` | Mode production |
| `DB_HOST` | `db.votredomaine.com` | PostgreSQL Unraid |
| `DB_PORT` | `5432` | Port PostgreSQL |
| `DB_NAME` | `garde_robe_db` | Nom base |
| `DB_USER` | `garde_robe_user` | Utilisateur |
| `DB_PASSWORD` | `Oketos2727!` | ⚠️ À changer ! |
| `MEDIA_URL` | `https://media.votredomaine.com/media/` | URL nginx |
| `ALLOWED_HOSTS` | `.onrender.com` | Domaines autorisés |
| `CSRF_TRUSTED_ORIGINS` | `https://votre-app.onrender.com` | CSRF origins |

#### Modifier build.sh pour production :

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input --settings=gestion_vetements.settings_prod
python manage.py migrate --settings=gestion_vetements.settings_prod
```

### 5️⃣ Upload des Images vers Unraid

Plusieurs méthodes pour uploader les images depuis l'app Django :

#### Méthode 1 : SFTP/SSH (Simple)

Installez `paramiko` et créez un backend de stockage Django custom :

```python
# vetements/storage.py
from django.core.files.storage import Storage
import paramiko

class UnraidSFTPStorage(Storage):
    def __init__(self):
        self.host = '192.168.1.47'  # ou via tunnel
        self.username = 'root'
        self.key_path = '/path/to/ssh/key'
        self.remote_path = '/mnt/user/appdata/garde-robe/media/'

    def _save(self, name, content):
        # Upload via SFTP
        ssh = paramiko.SSHClient()
        ssh.connect(self.host, username=self.username, key_filename=self.key_path)
        sftp = ssh.open_sftp()
        sftp.putfo(content, f'{self.remote_path}{name}')
        sftp.close()
        ssh.close()
        return name

    def url(self, name):
        return f'https://media.votredomaine.com/media/{name}'
```

#### Méthode 2 : API REST Upload (Avancé)

Créez une API sur Unraid qui accepte les uploads :
- Container Flask/FastAPI dédié
- Endpoint POST /upload
- Authentification par token

#### Méthode 3 : Rsync post-upload (Batch)

Script cron qui rsync les fichiers depuis Render vers Unraid périodiquement.

### 6️⃣ Test de l'Architecture

#### Test PostgreSQL

Depuis votre PC :
```bash
psql -h db.votredomaine.com -U garde_robe_user -d garde_robe_db
```

#### Test nginx media

```bash
curl https://media.votredomaine.com/health
# Devrait retourner : OK
```

#### Test Django sur Render

Une fois déployé :
```bash
curl https://votre-app.onrender.com/
# Devrait afficher la page d'accueil
```

## 🔒 Sécurité

### Checklist Sécurité

- [ ] Changer le mot de passe PostgreSQL par défaut
- [ ] Activer SSL sur PostgreSQL
- [ ] Configurer `pg_hba.conf` pour limiter les IPs autorisées
- [ ] Utiliser Cloudflare Tunnel ou VPN (pas de port forwarding direct)
- [ ] Configurer fail2ban sur Unraid (optionnel)
- [ ] Activer les logs nginx et surveillance
- [ ] Utiliser des clés SSH au lieu de mots de passe

### Bonnes Pratiques

1. **Backup régulier** : Utilisez Unraid CA Backup pour PostgreSQL et media
2. **Monitoring** : Installez Uptime Kuma sur Unraid pour surveiller les services
3. **Logs** : Consultez régulièrement les logs nginx et PostgreSQL
4. **Updates** : Gardez les containers Docker à jour

## 📊 Performances Attendues

- **Latence DB** : ~50-100ms (Render → Unraid via tunnel)
- **Chargement images** : ~200-500ms selon taille
- **Disponibilité** : 99.9% avec Cloudflare Tunnel

## 🚨 Dépannage

### PostgreSQL inaccessible depuis Render

```bash
# Vérifier que PostgreSQL écoute sur 0.0.0.0
docker exec postgres-container cat /var/lib/postgresql/data/postgresql.conf | grep listen_addresses
# Devrait être : listen_addresses = '*'

# Vérifier pg_hba.conf
docker exec postgres-container cat /var/lib/postgresql/data/pg_hba.conf
```

### Images ne se chargent pas

```bash
# Vérifier nginx
curl -I http://192.168.1.47/media/
# Devrait retourner 200 ou 403

# Vérifier permissions
ls -la /mnt/user/appdata/garde-robe/media/
```

### Erreur 502 sur Render

- Vérifiez les logs Render
- Testez la connexion DB depuis un autre client
- Vérifiez les variables d'environnement

## 📚 Ressources

- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Django Custom Storage](https://docs.djangoproject.com/en/stable/howto/custom-file-storage/)
- [PostgreSQL SSL](https://www.postgresql.org/docs/current/ssl-tcp.html)
- [Nginx CORS](https://enable-cors.org/server_nginx.html)

## ✅ Checklist Déploiement

- [ ] nginx configuré sur Unraid avec path mapping
- [ ] Dossiers media créés avec bonnes permissions
- [ ] Configuration nginx installée et service redémarré
- [ ] nginx accessible en local (http://192.168.1.47/health)
- [ ] PostgreSQL accessible en local
- [ ] Cloudflare Tunnel ou DynDNS configuré
- [ ] Tunnels créés pour db et media
- [ ] Variables d'environnement Render configurées
- [ ] settings_prod.py créé avec bons paramètres
- [ ] Application déployée sur Render
- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Test upload image fonctionnel

🎉 Architecture hybride opérationnelle !
