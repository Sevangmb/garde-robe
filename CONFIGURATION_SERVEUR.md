# Configuration Serveur - Ma Garde-Robe Mobile

## 📱 Configuration actuelle

### Adresse IP locale
- **IP de votre ordinateur**: `192.168.1.133`
- **Port du serveur Django**: `8000`

### URL du serveur
L'application mobile se connecte à : `http://192.168.1.133:8000`

## 🚀 Démarrage du serveur Django

### 1. Ouvrir un terminal dans le dossier du backend
```bash
cd "C:\Users\sevans\Desktop\ma garde robe\garde-robe"
```

### 2. Démarrer le serveur sur toutes les interfaces réseau
```bash
python manage.py runserver 0.0.0.0:8000
```

**Important** : Utilisez `0.0.0.0:8000` et non `127.0.0.1:8000` pour permettre l'accès depuis d'autres appareils du réseau.

### 3. Vérifier que le serveur est accessible
Ouvrez un navigateur sur votre ordinateur et allez à :
- `http://localhost:8000` ✓
- `http://192.168.1.133:8000` ✓

## 📲 Configuration de l'application mobile

### Fichier configuré
`mobile-app/www/index.html` (ligne 121)

```javascript
const SERVER_URL = 'http://192.168.1.133:8000';
```

### Configuration Django
Le fichier `garde-robe/gestion_vetements/settings.py` inclut :
```python
ALLOWED_HOSTS = ['*']  # Accepte toutes les connexions
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = [
    'http://10.0.2.2:8000',      # Émulateur Android
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://192.168.1.133:8000',  # Appareil physique
]
```

## ⚠️ Prérequis

### 1. Même réseau WiFi
- Votre ordinateur ET votre téléphone doivent être sur le **même réseau WiFi**
- Pas de connexion possible si l'un est sur données mobiles

### 2. Pare-feu Windows
Le pare-feu Windows peut bloquer les connexions. Si l'app ne se connecte pas :

**Option 1 : Autoriser Python dans le pare-feu**
1. Ouvrir "Pare-feu Windows Defender"
2. Cliquer sur "Autoriser une application via le pare-feu"
3. Chercher "Python" dans la liste
4. Cocher les cases "Privé" et "Public"

**Option 2 : Créer une règle temporaire**
```powershell
# Ouvrir PowerShell en administrateur
New-NetFirewallRule -DisplayName "Django Dev Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### 3. IP dynamique
Si votre IP change (redémarrage de la box, reconnexion WiFi) :

1. Vérifier votre nouvelle IP :
```bash
ipconfig
```
Chercher "Adresse IPv4" dans la section "Carte réseau sans fil Wi-Fi"

2. Mettre à jour `mobile-app/www/index.html` ligne 121

3. Mettre à jour `garde-robe/gestion_vetements/settings.py` dans `CSRF_TRUSTED_ORIGINS`

4. Reconstruire l'APK :
```bash
cd "C:\Users\sevans\Desktop\ma garde robe\mobile-app"
npx cap sync android
cd android
./gradlew.bat assembleDebug
```

## 🔧 Résolution des problèmes

### L'app affiche "Impossible de se connecter au serveur"

**1. Vérifier que le serveur Django est démarré**
```bash
cd "C:\Users\sevans\Desktop\ma garde robe\garde-robe"
python manage.py runserver 0.0.0.0:8000
```

**2. Tester depuis un navigateur sur votre téléphone**
Ouvrir Chrome/Safari et aller à : `http://192.168.1.133:8000`
- Si ça fonctionne : Problème dans l'app mobile
- Si ça ne fonctionne pas : Problème de réseau/pare-feu

**3. Vérifier le réseau WiFi**
- Les deux appareils sont sur le même réseau ?
- Le téléphone n'est pas sur données mobiles ?

**4. Vérifier l'IP**
```bash
ipconfig
```
L'IP est toujours `192.168.1.133` ?

**5. Désactiver temporairement le pare-feu**
Pour tester si c'est le pare-feu qui bloque :
- Ouvrir "Paramètres Windows" > "Mise à jour et sécurité" > "Sécurité Windows" > "Pare-feu"
- Désactiver temporairement le pare-feu pour les réseaux privés

## 🌐 Configuration pour émulateur Android

Si vous testez sur un émulateur Android Studio au lieu d'un appareil physique :

**Modifier** `mobile-app/www/index.html` ligne 121 :
```javascript
const SERVER_URL = 'http://10.0.2.2:8000';  // Pour émulateur Android
```

**Démarrer le serveur normalement** :
```bash
python manage.py runserver
```

L'adresse `10.0.2.2` est l'adresse spéciale de l'émulateur pour accéder à localhost de l'ordinateur hôte.

## 📦 APK mis à jour

**Emplacement** : `mobile-app/android/app/build/outputs/apk/debug/app-debug.apk`
**Date de build** : 12 octobre 2025, 08:50
**Taille** : 3,9 MB

### Installation
1. Transférer l'APK sur votre téléphone Android
2. Ouvrir le fichier APK
3. Autoriser l'installation depuis des sources inconnues si demandé
4. Installer l'application

## 🔐 Production (futur)

Pour un déploiement en production :

1. Héberger le backend Django sur un serveur (Heroku, PythonAnywhere, VPS)
2. Obtenir un nom de domaine et HTTPS
3. Modifier `settings.py` :
```python
DEBUG = False
ALLOWED_HOSTS = ['votre-domaine.com']
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = ['https://votre-domaine.com']
```
4. Modifier `www/index.html` :
```javascript
const SERVER_URL = 'https://votre-domaine.com';
```
5. Construire une version release signée de l'APK

---

**Dernière mise à jour** : 12 octobre 2025, 08:50
