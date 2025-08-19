"""
Module pour générer le contenu des capsules en utilisant Google Gemini
"""

import google.generativeai as genai
import os
import logging
from typing import Dict, List, Optional
import json
import re
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Classe pour générer le contenu des capsules avec Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Variable d'environnement GOOGLE_API_KEY non définie")
        
        genai.configure(api_key=self.api_key)
        
        # Configuration du modèle
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        logger.info("ContentGenerator initialisé avec Gemini")
    
    def generate_capsule_script(self, competence: str, thematique: str, sujet: str, 
                               url_contents: List[Dict]) -> Dict:
        """
        Génère le script complet d'une capsule éducative
        """
        logger.info(f"Génération du script pour: {sujet}")
        
        try:
            # Préparer le contexte
            sources_text = self._prepare_sources_context(url_contents)
            
            # Générer le script principal
            script_content = self._generate_main_script(competence, thematique, sujet, sources_text)
            
            # Générer les QCM
            qcm_data = self._generate_qcm(competence, thematique, sujet, sources_text)
            
            # Assembler le script final (pour PDF)
            final_script = self._assemble_final_script(script_content, qcm_data)
            
            # Créer la version pour l'audio (utiliser le script complet avec QCM)
            audio_script = final_script
            
            result = {
                'script': final_script,
                'script_for_audio': audio_script,
                'qcm_data': qcm_data,
                'qcm_positions': self._find_qcm_positions(final_script),
                'duration_estimate': self._estimate_duration(audio_script),
                'metadata': {
                    'competence': competence,
                    'thematique': thematique,
                    'sujet': sujet,
                    'sources_count': len(url_contents),
                    'generated_at': datetime.now().isoformat()
                }
            }
            
            logger.info(f"Script généré avec succès: {len(final_script)} caractères")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du script: {str(e)}")
            raise
    
    def _prepare_sources_context(self, url_contents: List[Dict]) -> str:
        """Prépare le contexte des sources pour Gemini"""
        context = "SOURCES DOCUMENTAIRES:\n\n"
        
        for i, source in enumerate(url_contents, 1):
            context += f"SOURCE {i}: {source['title']}\n"
            context += f"URL: {source['url']}\n"
            context += f"CONTENU:\n{source['content'][:2000]}...\n\n"
        
        return context
    
    def _generate_main_script(self, competence: str, thematique: str, sujet: str, 
                             sources_text: str) -> str:
        """Génère le script principal de la capsule"""
        
        prompt = f"""
Tu es un expert en pédagogie médicale spécialisé dans la santé publique et la réglementation des données de santé. 

Tu dois créer un script de capsule éducative de 5-10 minutes pour des étudiants en médecine de niveau licence.

CONTEXTE DE LA CAPSULE:
- Compétence: {competence}
- Thématique: {thematique} 
- Sujet spécifique: {sujet}

{sources_text}

CONSIGNES POUR LE SCRIPT:
1. Durée cible: 5-10 minutes de narration (environ 800-1200 mots)
2. Niveau: Licence en médecine (vulgarisé mais précis)
3. Ton: Pédagogique, engageant, professionnel
4. Structure obligatoire:
   - Introduction accrocheuse (30 secondes)
   - Corps principal avec 3-4 points clés
   - Conclusion avec synthèse et ouverture
5. Inclure des exemples concrets et cas pratiques
6. Utiliser un langage clair et accessible
7. Intégrer les informations des sources fournies
8. Marquer clairement les transitions

FORMAT DE SORTIE:
Écris le script sous forme de texte narratif continu, comme s'il était lu par un narrateur.
Utilise des marqueurs de transition comme "Passons maintenant à...", "Il est important de noter que...", etc.

Ne pas inclure les QCM dans ce script - ils seront ajoutés séparément.
"""

        response = self.model.generate_content(prompt)
        return response.text.strip()
    
    def _generate_qcm(self, competence: str, thematique: str, sujet: str, 
                     sources_text: str) -> List[Dict]:
        """Génère 2-3 QCM avec mises en situation"""
        
        prompt = f"""
Tu dois créer 2 à 3 QCM (questions à choix multiples) pour tester la compréhension des étudiants.

CONTEXTE:
- Compétence: {competence}
- Thématique: {thematique}
- Sujet: {sujet}

{sources_text}

CONSIGNES POUR LES QCM:
1. Créer exactement 2 ou 3 questions
2. Chaque question doit être basée sur une MISE EN SITUATION concrète
3. 4 propositions de réponse par question (A, B, C, D)
4. UNE SEULE bonne réponse par question
5. Les mauvaises réponses doivent être plausibles
6. Niveau adapté aux étudiants en licence de médecine
7. Questions pratiques sur l'application de la réglementation

FORMAT DE SORTIE (JSON):
{{
  "qcm": [
    {{
      "question_number": 1,
      "situation": "Description de la mise en situation...",
      "question": "Quelle est la bonne réponse dans cette situation ?",
      "options": {{
        "A": "Proposition A",
        "B": "Proposition B", 
        "C": "Proposition C",
        "D": "Proposition D"
      }},
      "correct_answer": "B",
      "explanation": "Explication détaillée de pourquoi B est correct et pourquoi les autres sont incorrectes"
    }}
  ]
}}

Retourne UNIQUEMENT le JSON, sans texte avant ou après.
"""

        response = self.model.generate_content(prompt)
        
        try:
            # Nettoyer la réponse pour extraire le JSON
            json_text = response.text.strip()
            if json_text.startswith('```json'):
                json_text = json_text[7:-3]
            elif json_text.startswith('```'):
                json_text = json_text[3:-3]
            
            qcm_data = json.loads(json_text)
            return qcm_data['qcm']
            
        except json.JSONDecodeError as e:
            logger.warning(f"Erreur de parsing JSON pour les QCM: {e}")
            # Fallback: créer un QCM basique
            return self._create_fallback_qcm(sujet)
    
    def _create_fallback_qcm(self, sujet: str) -> List[Dict]:
        """Crée un QCM de fallback en cas d'erreur"""
        return [{
            "question_number": 1,
            "situation": f"Dans le contexte de {sujet}, vous devez prendre une décision importante.",
            "question": "Quelle est la première étape à respecter ?",
            "options": {
                "A": "Consulter la réglementation en vigueur",
                "B": "Agir selon son intuition",
                "C": "Demander l'avis d'un collègue",
                "D": "Reporter la décision"
            },
            "correct_answer": "A",
            "explanation": "Il est essentiel de toujours consulter la réglementation en vigueur avant de prendre toute décision concernant les données de santé."
        }]
    
    def _assemble_final_script(self, main_script: str, qcm_data: List[Dict]) -> str:
        """Assemble le script final avec les QCM intégrés"""
        
        # Diviser le script en sections
        paragraphs = [p.strip() for p in main_script.split('\n\n') if p.strip()]
        
        if len(paragraphs) < 3:
            # Si pas assez de paragraphes, ajouter les QCM à la fin
            final_script = main_script + "\n\n"
            for qcm in qcm_data:
                final_script += self._format_qcm_for_script(qcm) + "\n\n"
            return final_script
        
        # Insérer les QCM de manière équilibrée
        final_script = ""
        total_sections = len(paragraphs)
        qcm_positions = []
        
        # Calculer les positions d'insertion
        if len(qcm_data) == 2:
            positions = [total_sections // 3, 2 * total_sections // 3]
        elif len(qcm_data) == 3:
            positions = [total_sections // 4, total_sections // 2, 3 * total_sections // 4]
        else:
            positions = [total_sections // 2]  # Au milieu par défaut
        
        qcm_index = 0
        for i, paragraph in enumerate(paragraphs):
            final_script += paragraph + "\n\n"
            
            # Insérer un QCM si on est à une position prévue
            if i in positions and qcm_index < len(qcm_data):
                qcm_formatted = self._format_qcm_for_script(qcm_data[qcm_index])
                final_script += qcm_formatted + "\n\n"
                qcm_positions.append(len(final_script))
                qcm_index += 1
        
        # Ajouter les QCM restants à la fin
        while qcm_index < len(qcm_data):
            qcm_formatted = self._format_qcm_for_script(qcm_data[qcm_index])
            final_script += qcm_formatted + "\n\n"
            qcm_index += 1
        
        return final_script
    
    def _format_qcm_for_script(self, qcm: Dict) -> str:
        """Formate un QCM pour l'insertion dans le script"""
        formatted = f"=== QCM {qcm['question_number']} ===\n\n"
        formatted += f"SITUATION: {qcm['situation']}\n\n"
        formatted += f"QUESTION: {qcm['question']}\n\n"
        
        for letter, option in qcm['options'].items():
            formatted += f"{letter}) {option}\n"
        
        formatted += f"\nRÉPONSE CORRECTE: {qcm['correct_answer']}\n"
        formatted += f"EXPLICATION: {qcm['explanation']}\n"
        
        return formatted
    
    def _find_qcm_positions(self, script: str) -> List[int]:
        """Trouve les positions des QCM dans le script"""
        positions = []
        lines = script.split('\n')
        
        for i, line in enumerate(lines):
            if line.startswith('=== QCM'):
                positions.append(i)
        
        return positions
    
    def _estimate_duration(self, script: str) -> str:
        """Estime la durée de lecture du script"""
        # Compter les mots (moyenne 150 mots/minute en français)
        words = len(script.split())
        duration_minutes = words / 150
        
        if duration_minutes < 1:
            return f"{int(duration_minutes * 60)} secondes"
        else:
            return f"{duration_minutes:.1f} minutes"

# Fonction utilitaire pour tester le module
def test_content_generator():
    """Fonction de test pour le générateur de contenu"""
    try:
        generator = ContentGenerator()
        
        # Données de test
        test_data = {
            'competence': '1.2 Caractériser et traiter la donnée à caractère personnel de santé en appliquant la réglementation',
            'thematique': 'Données de Santé',
            'sujet': 'Distinguer donnée à caractère personnel, donnée anonyme et donnée pseudonyme',
            'url_contents': [{
                'title': 'Test Source',
                'url': 'https://example.com',
                'content': 'Ceci est un contenu de test pour démontrer la génération de capsule éducative.'
            }]
        }
        
        result = generator.generate_capsule_script(**test_data)
        
        print("=== SCRIPT GÉNÉRÉ ===")
        print(result['script'][:500] + "...")
        print(f"\nDurée estimée: {result['duration_estimate']}")
        print(f"Nombre de QCM: {len(result['qcm_data'])}")
        
    except Exception as e:
        print(f"Erreur lors du test: {e}")

if __name__ == "__main__":
    test_content_generator()
