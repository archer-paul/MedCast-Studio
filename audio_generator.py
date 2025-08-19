"""
Module pour générer l'audio des capsules avec Google Text-to-Speech
"""

import os
import logging
from pathlib import Path
from typing import Optional
import tempfile
import re

from google.cloud import texttospeech
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

logger = logging.getLogger(__name__)

class AudioGenerator:
    """Classe pour générer l'audio des capsules avec GCP Text-to-Speech"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
        
        # Configuration pour la voix française masculine
        self.voice_config = texttospeech.VoiceSelectionParams(
            language_code="fr-FR",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
            name="fr-FR-Standard-B"  # Voix masculine française naturelle
        )
        
        # Configuration audio
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9,  # Légèrement plus lent pour la compréhension
            pitch=-2.0,  # Ton légèrement plus grave
            volume_gain_db=0.0
        )
        
        logger.info("AudioGenerator initialisé")
    
    def _initialize_client(self):
        """Initialise le client Text-to-Speech"""
        try:
            # Vérifier d'abord si la variable d'environnement est définie
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_path:
                # Vérifier si le fichier existe
                if os.path.exists(credentials_path):
                    self.client = texttospeech.TextToSpeechClient()
                    logger.info("Client Text-to-Speech initialisé avec succès")
                else:
                    logger.error(f"Fichier credentials non trouvé: {credentials_path}")
                    logger.info("Vérifiez le chemin dans votre fichier .env")
            else:
                logger.error("Variable GOOGLE_APPLICATION_CREDENTIALS non définie")
                logger.info("Définissez GOOGLE_APPLICATION_CREDENTIALS dans votre fichier .env")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du client TTS: {str(e)}")
            logger.warning("L'audio ne pourra pas être généré sans authentification GCP")
    
    def generate_audio(self, script_text: str, output_path: Path) -> Optional[Path]:
        """
        Génère l'audio à partir du script de la capsule
        """
        if not self.client:
            logger.error("Client Text-to-Speech non disponible")
            return self._create_audio_placeholder(output_path)
        
        try:
            logger.info(f"Génération audio: {output_path}")
            
            # Préparer le texte pour la synthèse vocale
            processed_text = self._preprocess_text_for_speech(script_text)
            
            # Diviser le texte en chunks si nécessaire (limite GCP: 5000 caractères)
            text_chunks = self._split_text_for_tts(processed_text)
            
            if len(text_chunks) == 1:
                # Texte court, génération directe
                audio_data = self._synthesize_speech(text_chunks[0])
                self._save_audio(audio_data, output_path)
            else:
                # Texte long, génération en plusieurs parties puis assemblage
                audio_parts = []
                for i, chunk in enumerate(text_chunks):
                    logger.info(f"Génération partie {i+1}/{len(text_chunks)}")
                    audio_data = self._synthesize_speech(chunk)
                    audio_parts.append(audio_data)
                
                # Assembler les parties audio
                self._concatenate_audio_parts(audio_parts, output_path)
            
            logger.info(f"Audio généré avec succès: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération audio: {str(e)}")
            return self._create_audio_placeholder(output_path)
    
    def _preprocess_text_for_speech(self, text: str) -> str:
        """
        Prétraite le texte pour améliorer la synthèse vocale
        """
        # Supprimer seulement les marqueurs visuels, garder le contenu des QCM
        text = re.sub(r'=== QCM \d+ ===\s*\n*', '\n\nMaintenant, testons vos connaissances avec un Q.C.M.\n\n', text)
        
        # Améliorer les marqueurs de QCM pour l'audio
        text = re.sub(r'SITUATION\s*:\s*', 'Voici une situation pratique : ', text)
        text = re.sub(r'QUESTION\s*:\s*', 'Question : ', text)
        text = re.sub(r'RÉPONSE CORRECTE\s*:\s*', '\n\nLa bonne réponse est : ', text)
        text = re.sub(r'REPONSE CORRECTE\s*:\s*', '\n\nLa bonne réponse est : ', text)
        text = re.sub(r'EXPLICATION\s*:\s*', '\n\nExplication : ', text)
        
        # Supprimer les marqueurs de formatage Markdown mais garder le contenu
        text = re.sub(r'\*\*\([^)]*Introduction[^)]*\)\*\*', '', text)
        text = re.sub(r'\*\*\([^)]*Conclusion[^)]*\)\*\*', '\n\nPour conclure,', text)
        text = re.sub(r'\*\*\([^)]*Point \d+[^)]*\)\*\*', '\n\nPassons maintenant au point suivant.', text)
        text = re.sub(r'\*\*\([^)]*Corps principal[^)]*\)\*\*', '', text)
        text = re.sub(r'\*\*\([^)]*Transition[^)]*\)\*\*', '\n\n', text)
        text = re.sub(r'\*\*\([^)]+\)\*\*', '', text)  # Autres titres entre parenthèses
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **texte** -> texte
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *texte* -> texte
        
        # Améliorer les options de QCM pour l'audio
        text = re.sub(r'\nA\)\s*', '\nOption A : ', text)
        text = re.sub(r'\nB\)\s*', '\nOption B : ', text)
        text = re.sub(r'\nC\)\s*', '\nOption C : ', text)
        text = re.sub(r'\nD\)\s*', '\nOption D : ', text)
        
        # Ajouter des pauses avant les réponses et explications
        text = re.sub(r'La bonne réponse est :', '<break time="2s"/>La bonne réponse est :', text)
        text = re.sub(r'Explication :', '<break time="1s"/>Explication :', text)
        
        # Améliorer la prononciation de certains termes
        replacements = {
            'RGPD': 'R.G.P.D.',
            'CNIL': 'C.N.I.L.',
            'API': 'A.P.I.',
            'URL': 'U.R.L.',
            'QCM': 'Q.C.M.',
            'etc.': 'et cetera',
            'ex.': 'par exemple',
            'cf.': 'voir',
            '&': 'et',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Ajouter des pauses aux points et points-virgules
        text = re.sub(r'\.(\s+)', '.<break time="0.5s"/>\\1', text)
        text = re.sub(r';(\s+)', ';<break time="0.3s"/>\\1', text)
        
        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Supprimer les lignes vides multiples mais garder la structure
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        return text
    
    def _split_text_for_tts(self, text: str, max_chars: int = 4000) -> list:
        """
        Divise le texte en chunks adaptés à l'API Text-to-Speech
        """
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Diviser par phrases pour respecter la limite
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            # Si une seule phrase dépasse la limite, la diviser par mots
            if len(sentence) > max_chars:
                words = sentence.split()
                current_word_chunk = ""
                
                for word in words:
                    if len(current_word_chunk) + len(word) + 1 <= max_chars:
                        current_word_chunk += word + " "
                    else:
                        if current_word_chunk:
                            chunks.append(current_word_chunk.strip())
                        current_word_chunk = word + " "
                
                if current_word_chunk:
                    if len(current_chunk) + len(current_word_chunk) <= max_chars:
                        current_chunk += current_word_chunk
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = current_word_chunk
            else:
                if len(current_chunk) + len(sentence) + 1 <= max_chars:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Texte divisé en {len(chunks)} parties pour la synthèse")
        return chunks
    
    def _synthesize_speech(self, text: str) -> bytes:
        """
        Synthétise la parole pour un chunk de texte
        """
        # Encapsuler le texte en SSML pour un meilleur contrôle
        ssml_text = f'<speak>{text}</speak>'
        
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
        
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=self.voice_config,
            audio_config=self.audio_config
        )
        
        return response.audio_content
    
    def _save_audio(self, audio_data: bytes, output_path: Path):
        """Sauvegarde les données audio"""
        with open(output_path, "wb") as f:
            f.write(audio_data)
    
    def _concatenate_audio_parts(self, audio_parts: list, output_path: Path):
        """
        Concatène plusieurs parties audio en un seul fichier
        """
        try:
            # Essayer d'utiliser pydub pour une concaténation propre
            from pydub import AudioSegment
            import io
            
            combined = AudioSegment.empty()
            
            for i, audio_data in enumerate(audio_parts):
                audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_data))
                combined += audio_segment
                
                # Ajouter une petite pause entre les segments (sauf le dernier)
                if i < len(audio_parts) - 1:
                    pause = AudioSegment.silent(duration=500)  # 500ms de pause
                    combined += pause
            
            combined.export(str(output_path), format="mp3")
            logger.info("Audio assemblé avec pydub")
            
        except ImportError:
            logger.warning("pydub non disponible, concaténation simple")
            # Fallback: concaténation binaire simple (moins propre mais fonctionnel)
            with open(output_path, "wb") as f:
                for audio_data in audio_parts:
                    f.write(audio_data)
    
    def _create_audio_placeholder(self, output_path: Path) -> Path:
        """
        Crée un fichier placeholder en cas d'échec de génération audio
        """
        placeholder_text = f"""
Fichier audio placeholder pour la capsule.

L'audio n'a pas pu être généré automatiquement.
Cela peut être dû à:
- Problème d'authentification GCP
- Service Text-to-Speech non disponible
- Erreur de configuration

Consultez les logs pour plus de détails.
Fichier généré le: {output_path.name}
"""
        
        # Créer un fichier texte avec les instructions
        text_path = output_path.with_suffix('.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(placeholder_text)
        
        logger.info(f"Placeholder audio créé: {text_path}")
        return text_path
    
    def test_voice_config(self) -> bool:
        """
        Teste la configuration de la voix avec un texte court
        """
        if not self.client:
            logger.error("Client non disponible pour le test")
            return False
        
        try:
            test_text = "Bonjour, ceci est un test de la synthèse vocale française."
            audio_data = self._synthesize_speech(test_text)
            
            logger.info(f"Test réussi, {len(audio_data)} bytes générés")
            return True
            
        except Exception as e:
            logger.error(f"Échec du test de voix: {str(e)}")
            return False
    
    def get_available_voices(self) -> list:
        """
        Récupère la liste des voix disponibles pour le français
        """
        if not self.client:
            return []
        
        try:
            voices_request = texttospeech.ListVoicesRequest(language_code="fr-FR")
            voices_response = self.client.list_voices(request=voices_request)
            
            voices = []
            for voice in voices_response.voices:
                voices.append({
                    'name': voice.name,
                    'gender': voice.ssml_gender.name,
                    'language_codes': list(voice.language_codes)
                })
            
            logger.info(f"Trouvé {len(voices)} voix françaises disponibles")
            return voices
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des voix: {str(e)}")
            return []

def test_audio_generator():
    """Fonction de test pour le générateur audio"""
    generator = AudioGenerator()
    
    # Test de la configuration
    print("=== TEST DE CONFIGURATION ===")
    if generator.client:
        print("✓ Client Text-to-Speech initialisé")
        
        # Test des voix disponibles
        voices = generator.get_available_voices()
        print(f"Voix françaises disponibles: {len(voices)}")
        for voice in voices[:3]:  # Afficher les 3 premières
            print(f"  - {voice['name']} ({voice['gender']})")
        
        # Test de synthèse
        print("\n=== TEST DE SYNTHÈSE ===")
        if generator.test_voice_config():
            print("✓ Test de synthèse réussi")
        else:
            print("✗ Échec du test de synthèse")
    else:
        print("✗ Client Text-to-Speech non disponible")
    
    # Test avec un texte d'exemple
    test_text = """
    Bonjour et bienvenue dans cette capsule d'apprentissage sur la réglementation des données de santé.
    
    [PAUSE]
    
    Aujourd'hui, nous allons voir comment distinguer les différents types de données personnelles dans le contexte médical.
    
    Merci de votre attention.
    """
    
    output_path = Path("test_audio.mp3")
    
    try:
        result = generator.generate_audio(test_text, output_path)
        if result and result.exists():
            print(f"\n✓ Audio de test généré: {result}")
            print(f"Taille: {result.stat().st_size} bytes")
        else:
            print(f"\n✗ Échec de la génération audio")
    except Exception as e:
        print(f"\n✗ Erreur: {e}")

if __name__ == "__main__":
    test_audio_generator()
