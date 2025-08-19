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
