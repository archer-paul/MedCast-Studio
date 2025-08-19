# Script d'installation PowerShell pour le générateur de capsules
# Compatible Windows 10/11 avec PowerShell 5.1+
# Version corrigée sans caractères spéciaux

param(
    [switch]$SkipLatex,
    [switch]$SkipFFmpeg,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "Installation du Générateur de Capsules d'Apprentissage" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green

# Fonction pour vérifier si une commande existe
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Fonction pour vérifier les privilèges administrateur
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Fonction pour installer Python
function Install-Python {
    Write-Host "Verification de Python..." -ForegroundColor Yellow
    
    if (Test-Command python) {
        $version = python --version
        Write-Host "OK $version trouve" -ForegroundColor Green
        return
    }
    
    if (Test-Command py) {
        $version = py --version
        Write-Host "OK Python trouve via py launcher: $version" -ForegroundColor Green
        # Créer un alias python vers py pour la suite
        Set-Alias -Name python -Value py -Scope Global
        return
    }
    
    Write-Host "ERREUR Python non trouve" -ForegroundColor Red
    Write-Host "Installation de Python..." -ForegroundColor Yellow
    
    # Télécharger et installer Python via winget si disponible
    if (Test-Command winget) {
        try {
            winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
            Write-Host "OK Python installe via winget" -ForegroundColor Green
        }
        catch {
            Write-Host "ERREUR Echec installation via winget" -ForegroundColor Red
            Write-Host "INFO Veuillez installer Python manuellement depuis https://python.org" -ForegroundColor Cyan
            exit 1
        }
    }
    else {
        Write-Host "ERREUR winget non disponible" -ForegroundColor Red
        Write-Host "INFO Installez Python manuellement depuis https://python.org" -ForegroundColor Cyan
        Write-Host "INFO Ou installez winget depuis le Microsoft Store" -ForegroundColor Cyan
        exit 1
    }
}

# Fonction pour installer Chocolatey
function Install-Chocolatey {
    if (Test-Command choco) {
        Write-Host "OK Chocolatey deja installe" -ForegroundColor Green
        return $true
    }
    
    Write-Host "Installation de Chocolatey..." -ForegroundColor Yellow
    
    if (-not (Test-Administrator)) {
        Write-Host "ATTENTION Chocolatey necessite des privileges administrateur" -ForegroundColor Yellow
        return $false
    }
    
    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Recharger les variables d'environnement
        $env:ChocolateyInstall = "$env:ProgramData\chocolatey"
        $env:Path += ";$env:ChocolateyInstall\bin"
        
        Write-Host "OK Chocolatey installe" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "ERREUR Echec installation Chocolatey: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Fonction pour installer LaTeX
function Install-LaTeX {
    if ($SkipLatex) {
        Write-Host "SKIP Installation LaTeX ignoree" -ForegroundColor Yellow
        return
    }
    
    Write-Host "Verification de LaTeX..." -ForegroundColor Yellow
    
    if (Test-Command pdflatex) {
        Write-Host "OK LaTeX deja installe" -ForegroundColor Green
        return
    }
    
    $install = Read-Host "Installer LaTeX (MiKTeX) ? Cela peut prendre du temps. (y/N)"
    if ($install -notmatch '^[Yy]') {
        Write-Host "SKIP Installation LaTeX ignoree" -ForegroundColor Yellow
        return
    }
    
    # Essayer winget d'abord
    if (Test-Command winget) {
        try {
            Write-Host "Installation de MiKTeX via winget..." -ForegroundColor Yellow
            winget install MiKTeX.MiKTeX --accept-package-agreements --accept-source-agreements
            Write-Host "OK MiKTeX installe via winget" -ForegroundColor Green
            return
        }
        catch {
            Write-Host "ERREUR Echec installation MiKTeX via winget" -ForegroundColor Red
        }
    }
    
    # Essayer Chocolatey
    if (Test-Command choco) {
        try {
            Write-Host "Installation de MiKTeX via Chocolatey..." -ForegroundColor Yellow
            choco install miktex -y
            Write-Host "OK MiKTeX installe via Chocolatey" -ForegroundColor Green
            return
        }
        catch {
            Write-Host "ERREUR Echec installation MiKTeX via Chocolatey" -ForegroundColor Red
        }
    }
    
    Write-Host "INFO Installation manuelle requise:" -ForegroundColor Cyan
    Write-Host "   Telechargez MiKTeX depuis https://miktex.org/download" -ForegroundColor Cyan
}

# Fonction pour installer FFmpeg
function Install-FFmpeg {
    if ($SkipFFmpeg) {
        Write-Host "SKIP Installation FFmpeg ignoree" -ForegroundColor Yellow
        return
    }
    
    Write-Host "Verification de FFmpeg..." -ForegroundColor Yellow
    
    if (Test-Command ffmpeg) {
        Write-Host "OK FFmpeg deja installe" -ForegroundColor Green
        return
    }
    
    $install = Read-Host "Installer FFmpeg ? (y/N)"
    if ($install -notmatch '^[Yy]') {
        Write-Host "SKIP Installation FFmpeg ignoree" -ForegroundColor Yellow
        return
    }
    
    # Essayer winget d'abord
    if (Test-Command winget) {
        try {
            Write-Host "Installation de FFmpeg via winget..." -ForegroundColor Yellow
            winget install Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
            Write-Host "OK FFmpeg installe via winget" -ForegroundColor Green
            return
        }
        catch {
            Write-Host "ERREUR Echec installation FFmpeg via winget" -ForegroundColor Red
        }
    }
    
    # Essayer Chocolatey
    if (Test-Command choco) {
        try {
            Write-Host "Installation de FFmpeg via Chocolatey..." -ForegroundColor Yellow
            choco install ffmpeg -y
            Write-Host "OK FFmpeg installe via Chocolatey" -ForegroundColor Green
            return
        }
        catch {
            Write-Host "ERREUR Echec installation FFmpeg via Chocolatey" -ForegroundColor Red
        }
    }
    
    Write-Host "INFO Installation manuelle requise:" -ForegroundColor Cyan
    Write-Host "   Telechargez FFmpeg depuis https://ffmpeg.org/download.html" -ForegroundColor Cyan
    Write-Host "   Ajoutez le repertoire bin a votre PATH" -ForegroundColor Cyan
}

# Fonction pour créer l'environnement virtuel
function Setup-VirtualEnvironment {
    Write-Host "Configuration de l'environnement virtuel Python..." -ForegroundColor Yellow
    
    if (Test-Path "venv") {
        if ($Force) {
            Write-Host "Suppression de l'ancien environnement virtuel..." -ForegroundColor Yellow
            Remove-Item -Recurse -Force venv
        }
        else {
            Write-Host "OK Environnement virtuel existe deja" -ForegroundColor Green
            return
        }
    }
    
    # Créer l'environnement virtuel
    python -m venv venv
    if (-not $?) {
        Write-Host "ERREUR Echec creation environnement virtuel" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "OK Environnement virtuel cree" -ForegroundColor Green
}

# Fonction pour activer l'environnement virtuel
function Activate-VirtualEnvironment {
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & "venv\Scripts\Activate.ps1"
        Write-Host "OK Environnement virtuel active" -ForegroundColor Green
    }
    else {
        Write-Host "ERREUR Script d'activation non trouve" -ForegroundColor Red
        exit 1
    }
}

# Fonction pour installer les dépendances Python
function Install-PythonDependencies {
    Write-Host "Installation des dependances Python..." -ForegroundColor Yellow
    
    # Vérifier que requirements.txt existe
    if (-not (Test-Path "requirements.txt")) {
        Write-Host "ERREUR Fichier requirements.txt non trouve" -ForegroundColor Red
        exit 1
    }
    
    # Mettre à jour pip
    python -m pip install --upgrade pip
    
    # Installer les dépendances
    pip install -r requirements.txt
    
    if ($?) {
        Write-Host "OK Dependances Python installees" -ForegroundColor Green
    }
    else {
        Write-Host "ERREUR Echec installation dependances" -ForegroundColor Red
        exit 1
    }
}

# Fonction pour installer Google Cloud CLI
function Install-GoogleCloudCLI {
    Write-Host "Installation de Google Cloud CLI (optionnel)..." -ForegroundColor Yellow
    
    if (Test-Command gcloud) {
        Write-Host "OK gcloud CLI deja installe" -ForegroundColor Green
        return
    }
    
    $install = Read-Host "Voulez-vous installer Google Cloud CLI ? (y/N)"
    if ($install -notmatch '^[Yy]') {
        Write-Host "SKIP Installation gcloud CLI ignoree" -ForegroundColor Yellow
        Write-Host "INFO Vous pouvez utiliser un Service Account a la place" -ForegroundColor Cyan
        return
    }
    
    # Essayer winget
    if (Test-Command winget) {
        try {
            Write-Host "Installation de Google Cloud CLI via winget..." -ForegroundColor Yellow
            winget install Google.CloudSDK --accept-package-agreements --accept-source-agreements
            Write-Host "OK Google Cloud CLI installe" -ForegroundColor Green
            return
        }
        catch {
            Write-Host "ERREUR Echec installation via winget" -ForegroundColor Red
        }
    }
    
    # Essayer Chocolatey
    if (Test-Command choco) {
        try {
            Write-Host "Installation de Google Cloud CLI via Chocolatey..." -ForegroundColor Yellow
            choco install gcloudsdk -y
            Write-Host "OK Google Cloud CLI installe" -ForegroundColor Green
            return
        }
        catch {
            Write-Host "ERREUR Echec installation via Chocolatey" -ForegroundColor Red
        }
    }
    
    Write-Host "INFO Installation manuelle requise:" -ForegroundColor Cyan
    Write-Host "   https://cloud.google.com/sdk/docs/install" -ForegroundColor Cyan
}

# Fonction pour créer les fichiers de configuration
function Setup-ConfigFiles {
    Write-Host "Creation des fichiers de configuration..." -ForegroundColor Yellow
    
    # Créer le fichier .env s'il n'existe pas
    if (-not (Test-Path ".env")) {
        $envContent = @"
# Configuration pour le generateur de capsules

# Cle API Gemini (obligatoire)
GOOGLE_API_KEY=your_gemini_api_key_here

# Chemin vers le fichier de credentials GCP (optionnel si gcloud configure)
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\service-account-key.json

# Configuration du logging (optionnel)
LOG_LEVEL=INFO
"@
        
        Set-Content -Path ".env" -Value $envContent -Encoding UTF8
        Write-Host "OK Fichier .env cree" -ForegroundColor Green
    }
    else {
        Write-Host "OK Fichier .env existe deja" -ForegroundColor Green
    }
    
    # Créer un script d'activation PowerShell
    $activateContent = @"
# Script pour activer l'environnement du generateur de capsules

Write-Host "Activation de l'environnement Generateur de Capsules" -ForegroundColor Green

# Activer l'environnement virtuel
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "OK Environnement virtuel active" -ForegroundColor Green
} else {
    Write-Host "ERREUR Environnement virtuel non trouve" -ForegroundColor Red
    exit 1
}

# Charger les variables d'environnement depuis .env
if (Test-Path ".env") {
    Get-Content ".env" | Where-Object { `$_ -match '^[^#].*=' } | ForEach-Object {
        `$key, `$value = `$_ -split '=', 2
        [Environment]::SetEnvironmentVariable(`$key.Trim(), `$value.Trim(), "Process")
    }
    Write-Host "OK Variables d'environnement chargees" -ForegroundColor Green
}

Write-Host "INFO Utilisez 'python main.py votre_fichier.xlsx' pour commencer" -ForegroundColor Cyan
"@
    
    Set-Content -Path "activate.ps1" -Value $activateContent -Encoding UTF8
    Write-Host "OK Script d'activation cree (.\activate.ps1)" -ForegroundColor Green
    
    # Créer aussi un fichier batch pour compatibilité
    $batchContent = @"
@echo off
echo Activation de l'environnement Generateur de Capsules

REM Activer l'environnement virtuel
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
    echo OK Environnement virtuel active
) else (
    echo ERREUR Environnement virtuel non trouve
    pause
    exit /b 1
)

echo INFO Utilisez 'python main.py votre_fichier.xlsx' pour commencer
cmd /k
"@
    
    Set-Content -Path "activate.bat" -Value $batchContent -Encoding UTF8
    Write-Host "OK Script d'activation batch cree (activate.bat)" -ForegroundColor Green
}

# Fonction pour tester l'installation
function Test-Installation {
    Write-Host "Test de l'installation..." -ForegroundColor Yellow
    
    # Tester les imports Python
    $testScript = @"
import sys
try:
    import pandas
    import openpyxl
    import requests
    import bs4
    import google.generativeai
    import google.cloud.texttospeech
    print('OK Toutes les dependances Python sont disponibles')
except ImportError as e:
    print(f'ERREUR Import: {e}')
    sys.exit(1)
"@
    
    $testResult = python -c $testScript
    Write-Host $testResult
    
    # Tester LaTeX
    if (Test-Command pdflatex) {
        Write-Host "OK LaTeX disponible" -ForegroundColor Green
    }
    else {
        Write-Host "ATTENTION LaTeX non disponible - les PDF seront generes avec reportlab" -ForegroundColor Yellow
    }
    
    # Tester FFmpeg
    if (Test-Command ffmpeg) {
        Write-Host "OK FFmpeg disponible" -ForegroundColor Green
    }
    else {
        Write-Host "ATTENTION FFmpeg non disponible - assemblage audio limite" -ForegroundColor Yellow
    }
    
    Write-Host "OK Test d'installation termine" -ForegroundColor Green
}

# Fonction pour afficher le résumé final
function Show-Summary {
    Write-Host ""
    Write-Host "SUCCES Installation terminee !" -ForegroundColor Green
    Write-Host "============================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Fichiers crees:" -ForegroundColor Cyan
    Write-Host "   - venv\              (environnement Python)" -ForegroundColor White
    Write-Host "   - .env               (configuration)" -ForegroundColor White
    Write-Host "   - activate.ps1       (script d'activation PowerShell)" -ForegroundColor White
    Write-Host "   - activate.bat       (script d'activation Batch)" -ForegroundColor White
    Write-Host ""
    Write-Host "Configuration requise:" -ForegroundColor Cyan
    Write-Host "   1. Editez le fichier .env avec vos cles API" -ForegroundColor White
    Write-Host "   2. Configurez vos credentials GCP" -ForegroundColor White
    Write-Host ""
    Write-Host "Pour commencer:" -ForegroundColor Cyan
    Write-Host "   .\activate.ps1" -ForegroundColor White
    Write-Host "   python setup_config.py    # Configuration guidee" -ForegroundColor White
    Write-Host "   python main.py votre_fichier.xlsx" -ForegroundColor White
    Write-Host ""
    Write-Host "Documentation complete dans README.md" -ForegroundColor Cyan
}

# Fonction principale
function Main {
    Write-Host "Debut de l'installation..." -ForegroundColor Yellow
    
    # Vérifier PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-Host "ERREUR PowerShell 5.0+ requis" -ForegroundColor Red
        exit 1
    }
    
    # Installer les gestionnaires de paquets si nécessaire
    if (Test-Administrator) {
        Install-Chocolatey | Out-Null
    }
    else {
        Write-Host "ATTENTION Execution sans privileges administrateur" -ForegroundColor Yellow
        Write-Host "   Certaines installations automatiques peuvent echouer" -ForegroundColor Yellow
    }
    
    # Installer Python
    Install-Python
    
    # Créer l'environnement virtuel
    Setup-VirtualEnvironment
    
    # Activer l'environnement virtuel
    Activate-VirtualEnvironment
    
    # Installer les dépendances Python
    Install-PythonDependencies
    
    # Installer les dépendances optionnelles
    Install-LaTeX
    Install-FFmpeg
    Install-GoogleCloudCLI
    
    # Créer les fichiers de configuration
    Setup-ConfigFiles
    
    # Tester l'installation
    Test-Installation
    
    # Afficher le résumé
    Show-Summary
}

# Vérifications préliminaires
if ([Security.Principal.WindowsIdentity]::GetCurrent().Name -eq "NT AUTHORITY\SYSTEM") {
    Write-Host "ERREUR Ne pas executer en tant que SYSTEM" -ForegroundColor Red
    exit 1
}

# Lancer l'installation
try {
    Main
}
catch {
    Write-Host "ERREUR Erreur lors de l'installation: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "INFO Consultez les logs pour plus de details" -ForegroundColor Yellow
    exit 1
}
