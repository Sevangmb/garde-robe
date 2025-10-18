# Guide d'Installation pour Créer l'APK

## Étape 1 : Télécharger Android Studio

1. **Ouvrez votre navigateur** et allez sur : https://developer.android.com/studio
2. **Cliquez sur "Download Android Studio"**
3. **Acceptez les conditions** et téléchargez (environ 1 Go)
4. **Attendez la fin du téléchargement** (~5-10 minutes selon votre connexion)

## Étape 2 : Installer Android Studio

1. **Lancez le fichier téléchargé** (android-studio-xxx.exe)
2. **Suivez l'assistant d'installation** :
   - Cliquez sur "Next"
   - Sélectionnez "Standard Installation"
   - Acceptez les paramètres par défaut
   - Cliquez sur "Finish"
3. **Première ouverture** : Android Studio va télécharger les composants SDK (~2-3 Go)
4. **Attendez la fin** de l'installation des composants (10-15 minutes)

## Étape 3 : Vérifier l'Installation

Ouvrez un nouveau terminal (Command Prompt) et tapez :

```bash
java -version
```

Vous devriez voir quelque chose comme :
```
java version "17.x.x" ...
```

## Étape 4 : Ouvrir le Projet Android

1. **Ouvrez un terminal** dans le dossier du projet :
   ```bash
   cd "C:\Users\sevans\Desktop\ma garde robe\mobile-app"
   ```

2. **Synchronisez Capacitor** :
   ```bash
   npx cap sync android
   ```

3. **Ouvrez le projet dans Android Studio** :
   ```bash
   npx cap open android
   ```

   Android Studio va s'ouvrir avec votre projet.

## Étape 5 : Construire l'APK

Dans Android Studio :

1. **Attendez** que Gradle termine la synchronisation (barre de progression en bas)
2. **Menu** → Build → Build Bundle(s) / APK(s) → **Build APK(s)**
3. **Attendez** la compilation (2-5 minutes la première fois)
4. Une notification apparaît en bas à droite : "APK(s) generated successfully"
5. **Cliquez sur "locate"** dans la notification

## Étape 6 : Récupérer l'APK

L'APK sera dans ce dossier :

```
C:\Users\sevans\Desktop\ma garde robe\mobile-app\android\app\build\outputs\apk\debug\app-debug.apk
```

**Taille approximative** : 5-15 Mo

## Étape 7 : Installer l'APK sur votre Téléphone

### Méthode A : Via Câble USB

1. **Connectez votre téléphone** en USB
2. **Activez le débogage USB** sur votre téléphone :
   - Paramètres → À propos du téléphone
   - Appuyez 7 fois sur "Numéro de build"
   - Retour → Options pour les développeurs → Débogage USB (ON)
3. **Copiez l'APK** sur votre téléphone
4. **Ouvrez le fichier APK** sur votre téléphone
5. **Autorisez** l'installation depuis des sources inconnues
6. **Installez** l'application

### Méthode B : Via Email/Cloud

1. **Envoyez l'APK par email** ou uploadez sur Google Drive/OneDrive
2. **Sur votre téléphone**, téléchargez l'APK
3. **Ouvrez le fichier** et installez

## Étape 8 : Démarrer le Serveur Django

**IMPORTANT** : L'application a besoin que le serveur Django soit accessible.

### Pour Tester sur Émulateur Android :

```bash
cd "C:\Users\sevans\Desktop\ma garde robe\garde-robe"
python manage.py runserver 0.0.0.0:8000
```

L'app utilisera automatiquement `http://10.0.2.2:8000`

### Pour Tester sur Téléphone Physique :

1. **Trouvez votre IP locale** :
   ```bash
   ipconfig
   ```
   Cherchez "Adresse IPv4" (ex : 192.168.1.145)

2. **Modifiez le fichier** `mobile-app/www/index.html` :
   - Ligne 120, remplacez par votre IP :
   ```javascript
   const SERVER_URL = 'http://192.168.1.145:8000';  // Votre IP
   ```

3. **Ajoutez votre IP dans Django** `garde-robe/gestion_vetements/settings.py` :
   ```python
   CSRF_TRUSTED_ORIGINS = [
       'http://10.0.2.2:8000',
       'http://localhost:8000',
       'http://127.0.0.1:8000',
       'http://192.168.1.145:8000',  # Votre IP
   ]
   ```

4. **Reconstruisez l'APK** (étapes 4-6)

5. **Démarrez le serveur** sur le réseau :
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

6. **Assurez-vous** que votre PC et téléphone sont sur le même WiFi

## 🎉 Terminé !

Vous avez maintenant :
- ✅ Un fichier APK installable
- ✅ Une application mobile native
- ✅ Accès à toute votre garde-robe depuis votre téléphone

## 🆘 Problèmes Courants

### "Gradle build failed"
- Solution : Dans Android Studio, File → Invalidate Caches / Restart

### "APK won't install"
- Solution : Paramètres → Sécurité → Autoriser sources inconnues

### "Cannot connect to server"
- Vérifiez que Django tourne sur 0.0.0.0:8000
- Vérifiez que PC et téléphone sont sur le même WiFi
- Vérifiez l'IP dans index.html

### "Gradle sync taking forever"
- Normal la première fois (peut prendre 10-15 minutes)
- Attendez patiemment

---

## 🚀 Alternative Rapide (si Android Studio ne marche pas)

Si vous avez des problèmes avec Android Studio, vous pouvez utiliser la construction en ligne de commande :

```bash
cd "C:\Users\sevans\Desktop\ma garde robe\mobile-app"
npx cap sync android
cd android
gradlew.bat assembleDebug
```

L'APK sera dans : `android\app\build\outputs\apk\debug\app-debug.apk`

---

**Temps total estimé** :
- Téléchargement + Installation Android Studio : 30-45 minutes
- Première construction APK : 5-10 minutes
- Constructions suivantes : 2-3 minutes
