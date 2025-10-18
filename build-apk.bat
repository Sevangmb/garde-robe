@echo off
REM Script pour construire l'APK de Ma Garde-Robe
echo ========================================
echo Construction APK - Ma Garde-Robe
echo ========================================
echo.

REM Configuration des variables d'environnement
set ANDROID_HOME=C:\Users\sevans\Android\Sdk
set PATH=%ANDROID_HOME%\cmdline-tools\latest\bin;%ANDROID_HOME%\platform-tools;%PATH%

echo [1/5] Configuration de l'environnement...
echo ANDROID_HOME: %ANDROID_HOME%
echo.

echo [2/5] Installation des composants SDK necessaires...
echo Cela peut prendre 5-10 minutes la premiere fois...
echo.

REM Accepter les licences
echo y | "%ANDROID_HOME%\cmdline-tools\latest\bin\sdkmanager.bat" --licenses

REM Installer les composants nécessaires
echo Installation de platform-tools...
"%ANDROID_HOME%\cmdline-tools\latest\bin\sdkmanager.bat" "platform-tools"

echo Installation de build-tools 33.0.0...
"%ANDROID_HOME%\cmdline-tools\latest\bin\sdkmanager.bat" "build-tools;33.0.0"

echo Installation de Android SDK Platform 33...
"%ANDROID_HOME%\cmdline-tools\latest\bin\sdkmanager.bat" "platforms;android-33"

echo.
echo [3/5] Synchronisation de Capacitor...
call npx cap sync android

echo.
echo [4/5] Construction de l'APK...
cd android
call gradlew.bat assembleDebug

echo.
echo [5/5] APK construit avec succes !
echo.
echo ========================================
echo Votre APK est ici :
echo %cd%\app\build\outputs\apk\debug\app-debug.apk
echo ========================================
echo.

REM Ouvrir le dossier contenant l'APK
explorer "%cd%\app\build\outputs\apk\debug"

pause
