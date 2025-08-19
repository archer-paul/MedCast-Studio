"""
Script de configuration pour l'environnement GCP et les API
"""

import os
import json
import logging
from pathlib import Path
from google.cloud import texttospeech
import google.generativeai as genai
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

logger = logging.getLogger(__name__)

def setup_gcp_credentials():
    """
    Configure les credentials GCP
    """
    print("=== CONFIGURATION DES CREDENTIALS GCP ===\n")
    
    # Vérifier si les credentials sont déjà configurés
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if credentials_path:
        # Convertir les chemins relatifs en chemins absolus
        if not os.path.isabs(credentials_path):
            credentials_path = os.path.abspath(credentials_path)
        
        if os.path.exists(credentials_path):
            # Mettre à jour la variable d'environnement avec le chemin absolu
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            print(f"✓ Credentials trouvés: {credentials_path}")
            return True
        else:
            print(f"✗ Fichier credentials introuvable: {credentials_path}")
    
    print("Credentials GCP non trouvés.")
    print("Vous devez configurer l'authentification GCP de l'une des façons suivantes:\n")
    
    print("OPTION 1: Service Account Key (Recommandé)")
    print("1. Aller sur https://console.cloud.google.com/")
    print("2. Sélectionner votre projet")
    print("3. IAM & Admin > Service Accounts")
    print("4. Créer un service account avec les rôles:")
    print("   - Cloud Text-to-Speech API User")
    print("   - Generative AI User")
    print("5. Télécharger la clé JSON")
    print("6. Définir la variable d'environnement:")
    print("   export GOOGLE_APPLICATION_CREDENTIALS='/path/to/your/key.json'")
    
    print("\nOPTION 2: Application Default Credentials")
    print("1. Installer gcloud CLI")
    print("2. Exécuter: gcloud auth application-default login")
    
    print("\nOPTION 3: Variables d'environnement")
    print("Définir GOOGLE_API_KEY pour Gemini")
    
    # Demander le chemin du fichier de credentials
    credentials_file = input("\nChemin vers votre fichier de credentials JSON (ou Enter pour passer): ").strip()
    
    if credentials_file and os.path.exists(credentials_file):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
        print(f"✓ Credentials configurés: {credentials_file}")
        return True
    
    return False

def setup_gemini_api():
    """
    Configure l'API Gemini
    """
    print("\n=== CONFIGURATION DE L'API GEMINI ===\n")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print("✓ GOOGLE_API_KEY trouvée")
        try:
            genai.configure(api_key=api_key)
            # Test simple
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content("Test de connexion")
            print("✓ Connexion Gemini réussie")
            return True
        except Exception as e:
            print(f"✗ Erreur de connexion Gemini: {e}")
            return False
    
    print("GOOGLE_API_KEY non trouvée.")
    print("Pour obtenir une clé API Gemini:")
    print("1. Aller sur https://aistudio.google.com/app/apikey")
    print("2. Créer une nouvelle clé API")
    print("3. Définir la variable d'environnement:")
    print("   export GOOGLE_API_KEY='your_api_key_here'")
    
    api_key = input("\nEntrez votre clé API Gemini (ou Enter pour passer): ").strip()
    if api_key:
        os.environ['GOOGLE_API_KEY'] = api_key
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content("Test de connexion")
            print("✓ Connexion Gemini réussie")
            return True
        except Exception as e:
            print(f"✗ Erreur de connexion Gemini: {e}")
            return False
    
    return False

def test_text_to_speech():
    """
    Teste l'API Text-to-Speech
    """
    print("\n=== TEST DE L'API TEXT-TO-SPEECH ===\n")
    
    try:
        client = texttospeech.TextToSpeechClient()
        
        # Test de liste des voix
        voices_request = texttospeech.ListVoicesRequest(language_code="fr-FR")
        voices = client.list_voices(request=voices_request)
        
        print(f"✓ API Text-to-Speech accessible")
        print(f"✓ {len(voices.voices)} voix françaises disponibles")
        
        # Afficher quelques voix
        for voice in voices.voices[:3]:
            gender_name = voice.ssml_gender.name if hasattr(voice.ssml_gender, 'name') else str(voice.ssml_gender)
            print(f"  - {voice.name} ({gender_name})")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur API Text-to-Speech: {e}")
        return False

def check_system_dependencies():
    """
    Vérifie les dépendances système
    """
    print("\n=== VÉRIFICATION DES DÉPENDANCES SYSTÈME ===\n")
    
    dependencies = {
        'LaTeX (pdflatex)': 'pdflatex --version',
        'FFmpeg (pour audio)': 'ffmpeg -version'
    }
    
    results = {}
    
    for dep_name, command in dependencies.items():
        try:
            import subprocess
            result = subprocess.run(command.split(), capture_output=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ {dep_name} disponible")
                results[dep_name] = True
            else:
                print(f"✗ {dep_name} non trouvé")
                results[dep_name] = False
        except:
            print(f"✗ {dep_name} non trouvé")
            results[dep_name] = False
    
    if not results.get('LaTeX (pdflatex)', False):
        print("\nPour installer LaTeX:")
        print("  Ubuntu/Debian: sudo apt-get install texlive-latex-extra")
        print("  macOS: brew install mactex")
        print("  Windows: https://miktex.org/")
    
    if not results.get('FFmpeg (pour audio)', False):
        print("\nPour installer FFmpeg:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: https://ffmpeg.org/download.html")
    
    return results

def create_env_file():
    """
    Crée un fichier .env d'exemple
    """
    env_content = """# Configuration pour le générateur de capsules

# Clé API Gemini (obligatoire)
GOOGLE_API_KEY=your_gemini_api_key_here

# Chemin vers le fichier de credentials GCP (optionnel si gcloud configuré)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# Configuration du logging (optionnel)
LOG_LEVEL=INFO
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"\n✓ Fichier .env créé: {env_file}")
        print("Éditez ce fichier avec vos vraies valeurs")
    else:
        print(f"\n✓ Fichier .env existe déjà: {env_file}")

def main():
    """
    Script principal de configuration
    """
    print("GÉNÉRATEUR DE CAPSULES D'APPRENTISSAGE")
    print("Configuration de l'environnement GCP")
    print("=" * 50)
    
    # Vérifier les dépendances système
    deps_ok = check_system_dependencies()
    
    # Configurer GCP
    gcp_ok = setup_gcp_credentials()
    
    # Configurer Gemini
    gemini_ok = setup_gemini_api()
    
    # Tester Text-to-Speech
    tts_ok = test_text_to_speech() if gcp_ok else False
    
    # Créer le fichier .env
    create_env_file()
    
    # Résumé
    print("\n" + "=" * 50)
    print("RÉSUMÉ DE LA CONFIGURATION")
    print("=" * 50)
    
    print(f"GCP Credentials: {'✓' if gcp_ok else '✗'}")
    print(f"API Gemini: {'✓' if gemini_ok else '✗'}")
    print(f"API Text-to-Speech: {'✓' if tts_ok else '✗'}")
    print(f"LaTeX: {'✓' if deps_ok.get('LaTeX (pdflatex)', False) else '✗'}")
    print(f"FFmpeg: {'✓' if deps_ok.get('FFmpeg (pour audio)', False) else '✗'}")
    
    if gemini_ok and (gcp_ok or tts_ok):
        print("\n🎉 Configuration réussie ! Vous pouvez lancer le générateur.")
        print("\nCommandes pour démarrer:")
        print("  python main.py votre_fichier.xlsx")
        print("  python main.py votre_fichier.xlsx --single 1  # Pour tester une seule ligne")
    else:
        print("\n⚠️  Configuration incomplète.")
        print("Le programme fonctionnera partiellement selon les services disponibles.")
        
        if not gemini_ok:
            print("- Sans Gemini: pas de génération de contenu")
        if not gcp_ok and not tts_ok:
            print("- Sans Text-to-Speech: pas de génération audio")

if __name__ == "__main__":
    main()