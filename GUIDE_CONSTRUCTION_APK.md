# 📱 Guide Complet : Construction de l'APK Ma Garde-Robe

## ✅ Statut Actuel

- ✅ Projet Capacitor configuré
- ✅ Android Command Line Tools téléchargés et installés
- ✅ Script de construction créé (`build-apk.bat`)
- ⏳ **Il manque uniquement Java JDK**

## 🔧 Étape 1 : Installer Java JDK

### Option A : Java JDK 17 (Recommandé)

1. **Téléchargez Java JDK 17** :
   - Lien direct : https://adoptium.net/temurin/releases/?version=17
   - Sélectionnez : Windows x64, JDK, .msi installer
   - Cliquez sur le bouton de téléchargement (~180 Mo)

2. **Installez Java** :
   - Lancez le fichier `.msi` téléchargé
   - Cliquez sur "Next" → "Next" → "Install"
   - **IMPORTANT** : Cochez "Set JAVA_HOME variable" si proposé
   - Cliquez sur "Finish"

3. **Vérifiez l'installation** :
   - Ouvrez un **nouveau** terminal (Command Prompt)
   - Tapez :
     ```bash
     java -version
     ```
   - Vous devriez voir :
     ```
     openjdk version "17.x.x" ...
     ```

### Option B : Java JDK via Chocolatey (Plus Rapide)

Si vous avez Chocolatey installé :

```bash
choco install openjdk17
```

## 🚀 Étape 2 : Construire l'APK

Une fois Java installé, c'est **très simple** :

### Méthode Automatique (Recommandée)

1. **Double-cliquez** sur le fichier :
   ```
   C:\Users\sevans\Desktop\ma garde robe\mobile-app\build-apk.bat
   ```

2. **Attendez** (5-10 minutes la première fois) :
   - ✅ Installation des composants SDK Android
   - ✅ Synchronisation de Capacitor
   - ✅ Construction de l'APK avec Gradle
   - ✅ Ouverture du dossier contenant l'APK

3. **Récupérez votre APK** :
   Le fichier sera ouvert automatiquement dans l'explorateur :
   ```
   C:\Users\sevans\Desktop\ma garde robe\mobile-app\android\app\build\outputs\apk\debug\app-debug.apk
   ```

### Méthode Manuelle (Si le script ne fonctionne pas)

Ouvrez un terminal dans le dossier du projet :

```bash
cd "C:\Users\sevans\Desktop\ma garde robe\mobile-app"

# Définir ANDROID_HOME
set ANDROID_HOME=C:\Users\sevans\Android\Sdk
set PATH=%ANDROID_HOME%\cmdline-tools\latest\bin;%ANDROID_HOME%\platform-tools;%PATH%

# Accepter les licences
echo y | "%ANDROID_HOME%\cmdline-tools\latest\bin\sdkmanager.bat" --licenses

# Installer les composants
"%ANDROID_HOME%\cmdline-tools\latest\bin\sdkmanager.bat" "platform-tools" "build-tools;33.0.0" "platforms;android-33"

# Synchroniser et construire
npx cap sync android
cd android
gradlew.bat assembleDebug
```

## 📦 Étape 3 : Votre APK est Prêt !

Vous trouverez l'APK ici :
```
C:\Users\sevans\Desktop\ma garde robe\mobile-app\android\app\build\outputs\apk\debug\app-debug.apk
```

**Taille approximative** : 5-15 Mo

## 📱 Étape 4 : Installer l'APK sur votre Téléphone

### Méthode 1 : Via Câble USB

1. **Connectez votre téléphone** en USB à votre PC
2. **Activez le débogage USB** :
   - Paramètres → À propos du téléphone
   - Appuyez 7 fois sur "Numéro de build" (mode développeur activé)
   - Retour → Options pour les développeurs → Débogage USB (activez)
3. **Copiez l'APK** sur votre téléphone (glisser-déposer dans l'explorateur)
4. **Sur le téléphone**, ouvrez l'Explorateur de fichiers
5. **Trouvez et ouvrez** `app-debug.apk`
6. **Autorisez** l'installation depuis des sources inconnues (si demandé)
7. **Installez** l'application

### Méthode 2 : Via Email

1. **Envoyez l'APK par email** à vous-même
2. **Sur votre téléphone**, ouvrez l'email
3. **Téléchargez l'APK**
4. **Ouvrez le fichier** et installez

### Méthode 3 : Via Google Drive / OneDrive

1. **Uploadez l'APK** sur votre cloud préféré
2. **Sur votre téléphone**, téléchargez depuis le cloud
3. **Ouvrez et installez**

## 🌐 Étape 5 : Configurer l'Accès au Serveur

L'application a besoin d'accéder au serveur Django.

### Pour Test sur Émulateur Android

L'URL est déjà configurée : `http://10.0.2.2:8000`

Démarrez simplement Django :
```bash
cd "C:\Users\sevans\Desktop\ma garde robe\garde-robe"
python manage.py runserver 0.0.0.0:8000
```

### Pour Test sur Téléphone Physique

**1. Trouvez votre IP locale** :

```bash
ipconfig
```

Cherchez "Adresse IPv4" dans la section WiFi (ex : `192.168.1.145`)

**2. Modifiez l'URL dans l'app** :

Éditez `mobile-app/www/index.html`, ligne 120 :

```javascript
const SERVER_URL = 'http://192.168.1.145:8000';  // Mettez VOTRE IP
```

**3. Ajoutez votre IP dans Django** :

Éditez `garde-robe/gestion_vetements/settings.py` :

```python
CSRF_TRUSTED_ORIGINS = [
    'http://10.0.2.2:8000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://192.168.1.145:8000',  # Ajoutez VOTRE IP
]
```

**4. Reconstruisez l'APK** :

Double-cliquez sur `build-apk.bat` (ça sera rapide, 1-2 minutes)

**5. Démarrez Django sur le réseau** :

```bash
cd "C:\Users\sevans\Desktop\ma garde robe\garde-robe"
python manage.py runserver 0.0.0.0:8000
```

**6. Assurez-vous** que PC et téléphone sont sur le **même WiFi**

## ✅ Vous Avez Fini !

Vous avez maintenant :
- 📱 Un fichier APK installable (`app-debug.apk`)
- 🚀 Une application mobile native Android
- 👔 Accès à toute votre garde-robe depuis votre téléphone

## 🎯 Temps Total Estimé

- ⏰ Téléchargement + Installation Java : 5-10 minutes
- ⏰ Première construction APK : 5-10 minutes
- ⏰ Configurations suivantes : 1-2 minutes
- **TOTAL : ~20 minutes**

## 🆘 Problèmes Courants

### "Java was started but returned exit code 1"

**Solution** : Java n'est pas correctement installé ou JAVA_HOME n'est pas défini.

1. Réinstallez Java JDK 17
2. Définissez JAVA_HOME manuellement :
   - Panneau de configuration → Système → Paramètres système avancés
   - Variables d'environnement
   - Nouvelle variable système :
     - Nom : `JAVA_HOME`
     - Valeur : `C:\Program Files\Eclipse Adoptium\jdk-17.x.x-hotspot`
   - Ajoutez à PATH : `%JAVA_HOME%\bin`

### "sdkmanager: command not found"

**Solution** : Vérifiez que cmdline-tools est au bon endroit :
```
C:\Users\sevans\Android\Sdk\cmdline-tools\latest\
```

### "Gradle sync failed"

**Solution** :
1. Supprimez le dossier `.gradle` dans `mobile-app/android/`
2. Relancez `build-apk.bat`

### "Cannot connect to server" (sur l'app)

**Solutions** :
- Vérifiez que Django tourne : `python manage.py runserver 0.0.0.0:8000`
- Vérifiez que PC et téléphone sont sur le même WiFi
- Vérifiez que l'IP dans `index.html` est correcte
- Vérifiez que l'IP est dans `CSRF_TRUSTED_ORIGINS`
- Désactivez temporairement le pare-feu Windows pour tester

### "APK won't install" (sur le téléphone)

**Solutions** :
- Paramètres → Sécurité → Autoriser l'installation depuis des sources inconnues
- Paramètres → Applications → Menu (⋮) → Accès spécial → Installer des applications inconnues → [Votre navigateur/explorateur] → Autoriser

## 📚 Fichiers Importants

| Fichier | Description |
|---------|-------------|
| `build-apk.bat` | Script automatique de construction |
| `www/index.html` | Configuration de l'URL du serveur (ligne 120) |
| `android/app/build/outputs/apk/debug/app-debug.apk` | **Votre APK final** |
| `GUIDE_APK.md` | Documentation complète du projet mobile |

## 🎉 Prochaines Étapes

Une fois l'APK installé et fonctionnel :

1. **Testez toutes les fonctionnalités** de l'application
2. **Partagez l'APK** avec d'autres utilisateurs si nécessaire
3. **Créez une version Release signée** pour le Google Play Store (voir `GUIDE_APK.md`)

---

**Besoin d'aide ?** Relisez ce guide ou consultez `GUIDE_APK.md` pour plus de détails.

**Bon développement ! 👔📱**
