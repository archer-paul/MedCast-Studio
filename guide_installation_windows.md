# Installation sur Windows

Ce guide décrit l'installation du Générateur de Capsules d'Apprentissage sur Windows 10/11.

## Prérequis

- **Windows 10/11** avec PowerShell 5.1+
- **Connexion Internet** pour téléchargements
- **Privilèges administrateur** (recommandé pour installation automatique)

## Installation automatique (Recommandée)

### Méthode 1: PowerShell (Recommandée)

```powershell
# 1. Ouvrir PowerShell en tant qu'administrateur
# 2. Autoriser l'exécution de scripts (si nécessaire)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Naviguer vers le dossier du projet
cd "C:\chemin\vers\votre\projet"

# 4. Lancer l'installation
.\install.ps1
```

### Options du script d'installation

```powershell
# Installation complète (par défaut)
.\install.ps1

# Ignorer LaTeX (PDF avec reportlab uniquement)
.\install.ps1 -SkipLatex

# Ignorer FFmpeg (assemblage audio limité)
.\install.ps1 -SkipFFmpeg

# Forcer la recréation de l'environnement virtuel
.\install.ps1 -Force

# Ignorer LaTeX et FFmpeg
.\install.ps1 -SkipLatex -SkipFFmpeg
```

## Installation manuelle

Si l'installation automatique échoue, suivez ces étapes :

### 1. Installer Python

**Option A: Via winget (Windows 11)**
```powershell
winget install Python.Python.3.11
```

**Option B: Téléchargement direct**
1. Aller sur [python.org](https://python.org/downloads/)
2. Télécharger Python 3.11+
3. **Important** : Cocher "Add Python to PATH" lors de l'installation

### 2. Créer l'environnement virtuel

```powershell
# Dans le dossier du projet
python -m venv venv

# Activer l'environnement
venv\Scripts\Activate.ps1

# Si erreur d'exécution de scripts :
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Installer les dépendances Python

```powershell
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt
```

### 4. Installer LaTeX (optionnel, pour PDF de qualité)

**Option A: Via winget**
```powershell
winget install MiKTeX.MiKTeX
```

**Option B: Via Chocolatey**
```powershell
# Installer Chocolatey d'abord (en tant qu'admin)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Installer MiKTeX
choco install miktex -y
```

**Option C: Installation manuelle**
1. Télécharger MiKTeX depuis [miktex.org](https://miktex.org/download)
2. Installer avec les options par défaut
3. Redémarrer PowerShell

### 5. Installer FFmpeg (optionnel, pour traitement audio)

**Option A: Via winget**
```powershell
winget install Gyan.FFmpeg
```

**Option B: Via Chocolatey**
```powershell
choco install ffmpeg -y
```

**Option C: Installation manuelle**
1. Télécharger depuis [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extraire dans `C:\ffmpeg`
3. Ajouter `C:\ffmpeg\bin` au PATH

### 6. Google Cloud CLI (optionnel)

**Pour l'authentification simplifiée**
```powershell
winget install Google.CloudSDK
```

## Configuration

### 1. Configuration automatique
```powershell
# Activer l'environnement
.\activate.ps1

# Configuration guidée
python setup_config.py
```

### 2. Configuration manuelle

**Éditez le fichier `.env`** :
```env
# Clé API Gemini (obligatoire)
GOOGLE_API_KEY=your_gemini_api_key_here

# Credentials GCP (optionnel si gcloud configuré)
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\service-account-key.json

LOG_LEVEL=INFO
```

**Obtenez vos clés API** :
1. **Gemini API** : [AI Studio](https://aistudio.google.com/app/apikey)
2. **GCP Service Account** : [Console GCP](https://console.cloud.google.com/iam-admin/serviceaccounts)

## Utilisation

### Démarrage rapide

```powershell
# 1. Activer l'environnement (à faire à chaque session)
.\activate.ps1

# 2. Traiter votre fichier Excel
python main.py "Compétences Santé Publique pour scenario QCM et capsule.xlsx"

# 3. Test sur une seule ligne
python main.py "votre_fichier.xlsx" --single 1
```

### Scripts de démarrage

Le script d'installation crée plusieurs fichiers :

- **`activate.ps1`** : Script PowerShell d'activation
- **`activate.bat`** : Script Batch d'activation
- **`.env`** : Configuration des variables d'environnement

**Double-clic sur `activate.bat`** pour démarrer rapidement !

## 🔧 Résolution de problèmes Windows

### Problème : Execution Policy

```powershell
# Erreur : execution of scripts is disabled
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problème : Python non trouvé

```powershell
# Vérifier l'installation
python --version
py --version

# Si échec, réinstaller Python avec "Add to PATH"
```

### Problème : Privileges administrateur

Si vous n'avez pas les droits admin :
1. Installer Python avec l'installateur utilisateur
2. Utiliser `pip install --user` pour les dépendances
3. Installer LaTeX/FFmpeg manuellement

### Problème : Antivirus bloquant

Certains antivirus bloquent les téléchargements :
1. Ajouter le dossier projet aux exceptions
2. Désactiver temporairement la protection temps réel
3. Télécharger manuellement les composants

### Problème : Proxy d'entreprise

Si vous êtes derrière un proxy :
```powershell
# Configurer pip pour le proxy
pip install --proxy http://user:pass@proxy.server:port package

# Configurer les variables d'environnement
$env:HTTP_PROXY = "http://proxy.server:port"
$env:HTTPS_PROXY = "http://proxy.server:port"
```

### Problème : Encodage des caractères

Si problèmes d'accents dans les fichiers :
```powershell
# Définir l'encodage UTF-8
$env:PYTHONIOENCODING = "utf-8"
chcp 65001
```

## Structure Windows

```
C:\votre\projet\
├── venv\                    # Environnement virtuel Python
│   ├── Scripts\
│   │   ├── activate.bat     # Activation Batch
│   │   ├── Activate.ps1     # Activation PowerShell
│   │   └── python.exe       # Python isolé
│   └── Lib\                 # Bibliothèques Python
├── capsules_output\         # Dossier de sortie
├── .env                     # Configuration
├── activate.ps1             # Script d'activation personnalisé
├── activate.bat             # Script d'activation Batch
├── main.py                  # Programme principal
└── requirements.txt         # Dépendances
```

## Optimisations Windows

### Performance

Pour de meilleures performances :
1. **SSD recommandé** pour le stockage des capsules
2. **16 GB RAM minimum** pour traiter de gros fichiers
3. **Antivirus exception** pour le dossier du projet

### Raccourcis utiles

Créer des raccourcis sur le bureau :
```powershell
# Raccourci pour activation
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Home\Desktop\Capsules Generator.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$PWD\activate.ps1`""
$Shortcut.WorkingDirectory = "$PWD"
$Shortcut.Save()
```

## Support Windows

En cas de problème persistant :

1. **Vérifier les logs** : `capsules_generation.log`
2. **Tester les composants** individuellement
3. **Vérifier l'environnement** : `python setup_config.py`
4. **Redémarrer PowerShell** après installations
5. **Consulter la documentation** complète dans README.md

### Commandes de diagnostic

```powershell
# Vérifier Python et dépendances
python --version
pip list

# Vérifier LaTeX
pdflatex --version

# Vérifier FFmpeg
ffmpeg -version

# Vérifier variables d'environnement
Get-ChildItem Env: | Where-Object {$_.Name -match "GOOGLE|PATH"}

# Test rapide du générateur
python -c "import google.generativeai; print('Gemini OK')"
python -c "import google.cloud.texttospeech; print('TTS OK')"
```

### Logs et debug

```powershell
# Activer les logs détaillés
$env:LOG_LEVEL = "DEBUG"

# Vérifier les logs
Get-Content capsules_generation.log -Tail 20

# Test avec une seule capsule
python main.py votre_fichier.xlsx --single 1
```

## Conseils Windows

1. **Utilisez Windows Terminal** pour une meilleure expérience
2. **Configurez VS Code** pour éditer facilement les fichiers
3. **Planifiez les tâches** avec le Planificateur de tâches Windows
4. **Sauvegardez régulièrement** vos clés API et configurations

## Prêt à générer !

Une fois l'installation terminée, vous devriez pouvoir :

```powershell
# Activer l'environnement
.\activate.ps1

# Générer vos capsules
python main.py "Compétences Santé Publique pour scenario QCM et capsule.xlsx"
```

Le programme va créer un dossier `capsules_output\` avec toutes vos capsules générées automatiquement !

---

** Liens utiles pour Windows :**
- [Python for Windows](https://python.org/downloads/windows/)
- [MiKTeX](https://miktex.org/download)
- [FFmpeg for Windows](https://ffmpeg.org/download.html#build-windows)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install-sdk#windows)
- [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701)