# Guide de Création et Déploiement de l'APK Android

Ce guide explique comment créer, tester et déployer l'application mobile Android "Ma Garde-Robe" à partir du projet Django.

## Table des Matières

1. [Prérequis](#prérequis)
2. [Configuration Initiale](#configuration-initiale)
3. [Construction de l'APK](#construction-de-lapk)
4. [Test sur Émulateur](#test-sur-émulateur)
5. [Test sur Appareil Physique](#test-sur-appareil-physique)
6. [Installation de l'APK](#installation-de-lapk)
7. [Déploiement en Production](#déploiement-en-production)
8. [Dépannage](#dépannage)

---

## Prérequis

### Logiciels Requis

1. **Android Studio**
   - Télécharger depuis https://developer.android.com/studio
   - Installer les composants SDK Android (API 33 ou supérieur recommandé)
   - Configurer les variables d'environnement ANDROID_HOME et JAVA_HOME

2. **Java JDK**
   - Version 11 ou supérieure
   - Inclus avec Android Studio ou téléchargeable séparément

3. **Node.js et npm**
   - ✅ Déjà installé (Node.js v22.16.0, npm 10.9.2)

4. **Python et Django**
   - ✅ Déjà installé (Python 3.13, Django 4.2.25)

### Vérification des Prérequis

```bash
# Vérifier Node.js
node --version  # Doit afficher v22.16.0 ou supérieur

# Vérifier npm
npm --version   # Doit afficher 10.9.2 ou supérieur

# Vérifier Python
python --version  # Doit afficher 3.13 ou supérieur

# Vérifier Java (après installation Android Studio)
java -version    # Doit afficher version 11 ou supérieur
```

---

## Configuration Initiale

### 1. Structure du Projet

Votre projet a maintenant deux composants :

```
ma garde robe/
├── garde-robe/          # Application Django (serveur backend)
│   ├── manage.py
│   ├── gestion_vetements/
│   ├── vetements/
│   └── ...
│
└── mobile-app/          # Application mobile Capacitor
    ├── www/
    │   └── index.html   # Point d'entrée WebView
    ├── android/         # Projet Android natif
    ├── capacitor.config.json
    └── package.json
```

### 2. Configuration Réseau

L'application mobile charge le serveur Django via une URL. Vous devez choisir selon votre cas :

#### Option A : Test sur Émulateur Android
```javascript
// Dans mobile-app/www/index.html (ligne 120)
const SERVER_URL = 'http://10.0.2.2:8000';  // ✅ Déjà configuré
```
`10.0.2.2` est l'adresse spéciale de l'émulateur pour accéder à localhost de votre PC.

#### Option B : Test sur Appareil Physique

1. **Trouver votre adresse IP locale** :
   ```bash
   # Windows
   ipconfig
   # Chercher "Adresse IPv4" (ex : 192.168.1.145)

   # Linux/Mac
   ifconfig
   # Chercher "inet" (ex : 192.168.1.145)
   ```

2. **Modifier l'URL dans index.html** :
   ```javascript
   // Remplacer ligne 120 dans mobile-app/www/index.html
   const SERVER_URL = 'http://192.168.1.145:8000';  // Votre IP
   ```

3. **Ajouter l'IP aux origines CSRF de Django** :
   ```python
   # Dans garde-robe/gestion_vetements/settings.py
   CSRF_TRUSTED_ORIGINS = [
       'http://10.0.2.2:8000',
       'http://localhost:8000',
       'http://127.0.0.1:8000',
       'http://192.168.1.145:8000',  # ← Ajouter votre IP
   ]
   ```

---

## Construction de l'APK

### Étape 1 : Démarrer le Serveur Django

Le serveur Django doit être en cours d'exécution pour que l'application mobile fonctionne.

```bash
# Dans le répertoire garde-robe/
cd "C:\Users\sevans\Desktop\ma garde robe\garde-robe"

# Démarrer le serveur accessible depuis le réseau
python manage.py runserver 0.0.0.0:8000
```

**Important** : Utilisez `0.0.0.0:8000` au lieu de `localhost:8000` pour que le serveur soit accessible depuis votre téléphone ou émulateur.

### Étape 2 : Synchroniser les Modifications

```bash
# Dans le répertoire mobile-app/
cd "C:\Users\sevans\Desktop\ma garde robe\mobile-app"

# Synchroniser les modifications www/ vers Android
npx cap sync android
```

### Étape 3 : Ouvrir le Projet dans Android Studio

```bash
# Ouvrir Android Studio avec le projet Android
npx cap open android
```

Cette commande ouvrira Android Studio automatiquement. Attendez que Gradle termine la synchronisation (barre de progression en bas).

### Étape 4 : Construire l'APK

Dans Android Studio :

1. **Menu Build → Build Bundle(s) / APK(s) → Build APK(s)**
2. Attendez la fin de la compilation (notification en bas à droite)
3. Cliquez sur **"locate"** dans la notification pour trouver l'APK

L'APK sera situé dans :
```
mobile-app/android/app/build/outputs/apk/debug/app-debug.apk
```

---

## Test sur Émulateur

### Créer un Émulateur Android (première fois)

1. Dans Android Studio : **Tools → Device Manager**
2. Cliquez sur **"Create Device"**
3. Choisissez un appareil (ex : Pixel 5)
4. Sélectionnez une image système (ex : Android 13 "Tiramisu" API 33)
5. Téléchargez l'image si nécessaire
6. Nommez l'émulateur et cliquez sur **"Finish"**

### Lancer l'Application sur Émulateur

**Méthode 1 : Depuis Android Studio**
1. Sélectionnez l'émulateur dans la liste déroulante (en haut)
2. Cliquez sur le bouton **"Run"** ▶️
3. L'application s'installera et se lancera automatiquement

**Méthode 2 : Depuis la ligne de commande**
```bash
# Dans mobile-app/
npx cap run android
```

### Vérification

1. L'application affiche l'écran de chargement avec le logo 👔
2. Le serveur Django se charge dans l'iframe
3. Vous pouvez naviguer normalement dans l'application

---

## Test sur Appareil Physique

### Étape 1 : Activer le Mode Développeur

Sur votre téléphone Android :

1. **Paramètres → À propos du téléphone**
2. Appuyez 7 fois sur **"Numéro de build"**
3. Le mode développeur est activé

### Étape 2 : Activer le Débogage USB

1. **Paramètres → Options pour les développeurs**
2. Activez **"Débogage USB"**

### Étape 3 : Connecter le Téléphone

1. Branchez votre téléphone en USB
2. Autorisez le débogage USB sur le téléphone (popup)
3. Vérifiez la connexion :
   ```bash
   # Liste les appareils connectés
   adb devices
   ```
   Vous devriez voir votre appareil listé.

### Étape 4 : Configuration Réseau

**IMPORTANT** : Assurez-vous que :
- Votre PC et votre téléphone sont sur le **même réseau WiFi**
- Vous avez modifié `SERVER_URL` avec votre IP locale (voir Configuration Initiale)
- Le serveur Django écoute sur `0.0.0.0:8000`

### Étape 5 : Lancer sur l'Appareil

**Méthode 1 : Depuis Android Studio**
1. Sélectionnez votre appareil dans la liste déroulante
2. Cliquez sur **"Run"** ▶️

**Méthode 2 : Installer l'APK manuellement**
```bash
# Installer l'APK via ADB
adb install "mobile-app/android/app/build/outputs/apk/debug/app-debug.apk"
```

---

## Installation de l'APK

### Partager l'APK

Pour installer l'application sur d'autres appareils :

1. **Copiez l'APK** :
   ```
   mobile-app/android/app/build/outputs/apk/debug/app-debug.apk
   ```

2. **Transférez sur le téléphone** (email, USB, cloud, etc.)

3. **Sur le téléphone Android** :
   - Ouvrez le fichier APK
   - Autorisez l'installation depuis des sources inconnues si demandé
   - Appuyez sur **"Installer"**

### ⚠️ Limitations Version Debug

L'APK de debug (`app-debug.apk`) :
- ✅ Fonctionne pour les tests
- ❌ Ne peut pas être publié sur Google Play Store
- ❌ Plus volumineux qu'une version release
- ❌ Inclut des symboles de débogage

Pour une version release signée, voir section [Déploiement en Production](#déploiement-en-production).

---

## Déploiement en Production

### Option 1 : APK Release Signé

Pour créer un APK optimisé et signé :

#### 1. Créer une Clé de Signature

```bash
# Créer un keystore (une seule fois)
keytool -genkey -v -keystore ma-garde-robe.keystore -alias magarderobe -keyalg RSA -keysize 2048 -validity 10000
```

Conservez précieusement ce fichier `.keystore` et le mot de passe !

#### 2. Configurer Gradle

Créez `mobile-app/android/key.properties` :
```properties
storePassword=VOTRE_MOT_DE_PASSE
keyPassword=VOTRE_MOT_DE_PASSE
keyAlias=magarderobe
storeFile=C:/chemin/vers/ma-garde-robe.keystore
```

⚠️ **Ne jamais commiter ce fichier sur Git !**

#### 3. Modifier build.gradle

Dans `mobile-app/android/app/build.gradle`, ajoutez avant `android {` :

```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}
```

Et dans `android { ... }`, ajoutez `signingConfigs` :

```gradle
android {
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

#### 4. Construire l'APK Release

```bash
# Dans mobile-app/
cd android
./gradlew assembleRelease
```

L'APK signé sera dans :
```
mobile-app/android/app/build/outputs/apk/release/app-release.apk
```

### Option 2 : Serveur Django Déployé

Pour une application en production, déployez Django sur un serveur :

1. **Déployer Django** (Heroku, DigitalOcean, AWS, etc.)
2. **Obtenir l'URL** (ex : https://magarderobe.herokuapp.com)
3. **Modifier SERVER_URL** dans `www/index.html` :
   ```javascript
   const SERVER_URL = 'https://magarderobe.herokuapp.com';
   ```
4. **Mettre à jour settings.py** :
   ```python
   ALLOWED_HOSTS = ['magarderobe.herokuapp.com']
   CSRF_TRUSTED_ORIGINS = ['https://magarderobe.herokuapp.com']
   CORS_ALLOW_ALL_ORIGINS = False  # Plus sécurisé
   CORS_ALLOWED_ORIGINS = ['https://magarderobe.herokuapp.com']
   ```
5. **Reconstruire l'APK** avec la nouvelle URL

### Option 3 : Progressive Web App (PWA)

Alternative à l'APK : transformer en PWA installable directement depuis le navigateur.

---

## Dépannage

### Problème : "Impossible de se connecter au serveur"

**Causes possibles** :
- Le serveur Django n'est pas démarré
- L'adresse IP est incorrecte
- Le firewall bloque le port 8000
- PC et téléphone sur des réseaux différents

**Solutions** :
```bash
# Vérifier que le serveur écoute sur toutes les interfaces
python manage.py runserver 0.0.0.0:8000

# Windows : Autoriser le port 8000 dans le pare-feu
# Paramètres → Pare-feu → Autoriser une application

# Vérifier l'IP locale
ipconfig  # Windows
```

### Problème : "CSRF token missing"

**Solution** : Ajoutez votre IP dans `CSRF_TRUSTED_ORIGINS` :
```python
# settings.py
CSRF_TRUSTED_ORIGINS = [
    'http://10.0.2.2:8000',
    'http://192.168.1.X:8000',  # Votre IP
]
```

### Problème : L'APK ne s'installe pas

**Causes possibles** :
- Sources inconnues non autorisées
- Version Android trop ancienne
- APK corrompu

**Solutions** :
- Autorisez l'installation depuis des sources inconnues
- Vérifiez la version Android (minimum API 22 / Android 5.1)
- Reconstruisez l'APK

### Problème : Gradle Build Failed

**Solution** : Nettoyez et reconstruisez :
```bash
cd mobile-app/android
./gradlew clean
./gradlew assembleDebug
```

### Problème : Permission Denied sur Camera/Storage

**Solution** : Les permissions sont déjà dans AndroidManifest.xml. Si l'utilisateur refuse, l'app doit gérer gracieusement :
- Vérifier les permissions dans Paramètres → Applications → Ma Garde-Robe → Autorisations

---

## Résumé des Commandes

```bash
# Démarrer Django (dans garde-robe/)
python manage.py runserver 0.0.0.0:8000

# Synchroniser modifications (dans mobile-app/)
npx cap sync android

# Ouvrir Android Studio
npx cap open android

# Construire et lancer sur appareil
npx cap run android

# Lister appareils connectés
adb devices

# Installer APK manuellement
adb install app-debug.apk
```

---

## Ressources

- **Documentation Capacitor** : https://capacitorjs.com/docs
- **Documentation Android Studio** : https://developer.android.com/studio/intro
- **Django CORS Headers** : https://pypi.org/project/django-cors-headers/
- **ADB Commands** : https://developer.android.com/studio/command-line/adb

---

## Support

Pour toute question ou problème :
1. Vérifiez la section [Dépannage](#dépannage)
2. Consultez les logs Django : `python manage.py runserver` affiche les erreurs
3. Consultez les logs Android : Android Studio → Logcat
4. Vérifiez la connexion réseau entre PC et téléphone

---

**Bon développement ! 👔📱**
