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
    Get-Content ".env" | Where-Object { $_ -match '^[^#].*=' } | ForEach-Object {
        $key, $value = $_ -split '=', 2
        [Environment]::SetEnvironmentVariable($key.Trim(), $value.Trim(), "Process")
    }
    Write-Host "OK Variables d'environnement chargees" -ForegroundColor Green
}

Write-Host "INFO Utilisez 'python main.py votre_fichier.xlsx' pour commencer" -ForegroundColor Cyan
