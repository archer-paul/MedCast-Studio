#!/usr/bin/env python3
"""
Script de régénération des capsules audio et PDF à partir des scripts modifiés
Permet aux utilisateurs de corriger manuellement les scripts dans script.txt 
et de regénérer automatiquement l'audio et les PDF avec leurs modifications.

Usage:
    python regenerate_capsules.py                    # Régénère toutes les capsules
    python regenerate_capsules.py --capsule 001      # Régénère une capsule spécifique
    python regenerate_capsules.py --audio-only       # Régénère seulement l'audio
    python regenerate_capsules.py --pdf-only         # Régénère seulement les PDF
"""

import os
import sys
import argparse
import logging
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from audio_generator import AudioGenerator
from pdf_generator import PDFGenerator
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('regenerate_capsules.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CapsuleRegenerator:
    """Classe pour régénérer les capsules à partir des scripts modifiés"""
    
    def __init__(self, output_dir: str = "capsules_output"):
        self.output_dir = Path(output_dir)
        if not self.output_dir.exists():
            raise ValueError(f"Dossier de sortie non trouvé: {output_dir}")
        
        self.audio_generator = AudioGenerator()
        self.pdf_generator = PDFGenerator()
        
        logger.info("CapsuleRegenerator initialisé")
    
    def find_capsule_directories(self) -> List[Path]:
        """Trouve tous les dossiers de capsules"""
        capsule_dirs = []
        for item in self.output_dir.iterdir():
            if item.is_dir() and item.name.startswith('capsule_'):
                # Vérifier que le dossier contient les fichiers nécessaires
                script_file = item / "script.txt"
                metadata_file = item / "metadata.json"
                
                if script_file.exists() and metadata_file.exists():
                    capsule_dirs.append(item)
                else:
                    logger.warning(f"Capsule incomplète ignorée: {item.name}")
        
        return sorted(capsule_dirs)
    
    def get_capsule_by_number(self, capsule_number: str) -> Optional[Path]:
        """Trouve une capsule spécifique par son numéro"""
        # Normaliser le numéro (ajouter des zéros si nécessaire)
        capsule_num = capsule_number.zfill(3)
        
        for item in self.output_dir.iterdir():
            if item.is_dir() and item.name.startswith(f'capsule_{capsule_num}'):
                script_file = item / "script.txt"
                metadata_file = item / "metadata.json"
                
                if script_file.exists() and metadata_file.exists():
                    return item
        
        return None
    
    def load_capsule_data(self, capsule_dir: Path) -> Dict:
        """Charge les données d'une capsule"""
        try:
            # Charger le script
            script_file = capsule_dir / "script.txt"
            with open(script_file, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Charger les métadonnées
            metadata_file = capsule_dir / "metadata.json"
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return {
                'script_content': script_content,
                'metadata': metadata,
                'script_file': script_file,
                'metadata_file': metadata_file
            }
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données de {capsule_dir.name}: {str(e)}")
            return None
    
    def parse_script_content(self, script_content: str) -> Dict:
        """Parse le contenu du script pour extraire les sections"""
        script_data = {
            'title': '',
            'introduction': '',
            'development': '',
            'conclusion': '',
            'quiz': []
        }
        
        try:
            lines = script_content.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('# '):
                    # Nouveau titre/section
                    if current_section:
                        script_data[current_section] = '\n'.join(current_content).strip()
                    
                    title_text = line[2:].strip()
                    if 'introduction' in title_text.lower():
                        current_section = 'introduction'
                    elif 'développement' in title_text.lower() or 'developpement' in title_text.lower():
                        current_section = 'development'
                    elif 'conclusion' in title_text.lower():
                        current_section = 'conclusion'
                    elif 'quiz' in title_text.lower() or 'qcm' in title_text.lower():
                        current_section = 'quiz'
                    else:
                        script_data['title'] = title_text
                        current_section = None
                    
                    current_content = []
                
                elif line.startswith('## ') and current_section == 'quiz':
                    # Question de quiz
                    if current_content:
                        script_data['quiz'].append('\n'.join(current_content).strip())
                    current_content = [line]
                
                else:
                    if current_section:
                        current_content.append(line)
            
            # Ajouter le dernier contenu
            if current_section and current_content:
                if current_section == 'quiz':
                    script_data['quiz'].append('\n'.join(current_content).strip())
                else:
                    script_data[current_section] = '\n'.join(current_content).strip()
        
        except Exception as e:
            logger.warning(f"Erreur lors du parsing du script: {str(e)}")
            # Fallback: utiliser tout le contenu comme développement
            script_data['development'] = script_content
        
        return script_data
    
    def regenerate_audio(self, capsule_dir: Path, capsule_data: Dict) -> bool:
        """Régénère l'audio d'une capsule"""
        try:
            logger.info(f"Régénération audio pour {capsule_dir.name}")
            
            script_content = capsule_data['script_content']
            audio_output_path = capsule_dir / "capsule.mp3"
            
            # Supprimer l'ancien fichier audio s'il existe
            if audio_output_path.exists():
                audio_output_path.unlink()
                logger.info("Ancien fichier audio supprimé")
            
            # Générer le nouvel audio
            result = self.audio_generator.generate_audio(script_content, audio_output_path)
            
            if result and result.exists():
                logger.info(f"Audio régénéré avec succès: {result}")
                return True
            else:
                logger.error("Échec de la génération audio")
                return False
        
        except Exception as e:
            logger.error(f"Erreur lors de la régénération audio de {capsule_dir.name}: {str(e)}")
            return False
    
    def regenerate_pdf(self, capsule_dir: Path, capsule_data: Dict) -> bool:
        """Régénère le PDF d'une capsule"""
        try:
            logger.info(f"Régénération PDF pour {capsule_dir.name}")
            
            # Parser le contenu du script
            script_data = self.parse_script_content(capsule_data['script_content'])
            metadata = capsule_data['metadata']
            
            pdf_output_path = capsule_dir / "capsule.pdf"
            
            # Supprimer l'ancien fichier PDF s'il existe
            if pdf_output_path.exists():
                pdf_output_path.unlink()
                logger.info("Ancien fichier PDF supprimé")
            
            # Générer le nouveau PDF
            result = self.pdf_generator.generate_pdf(script_data, pdf_output_path, metadata)
            
            if result and result.exists():
                logger.info(f"PDF régénéré avec succès: {result}")
                return True
            else:
                logger.error("Échec de la génération PDF")
                return False
        
        except Exception as e:
            logger.error(f"Erreur lors de la régénération PDF de {capsule_dir.name}: {str(e)}")
            return False
    
    def regenerate_capsule(self, capsule_dir: Path, audio_only: bool = False, pdf_only: bool = False) -> Dict:
        """Régénère une capsule complète"""
        logger.info(f"Début de la régénération de {capsule_dir.name}")
        
        result = {
            'capsule': capsule_dir.name,
            'audio_success': False,
            'pdf_success': False,
            'errors': []
        }
        
        try:
            # Charger les données de la capsule
            capsule_data = self.load_capsule_data(capsule_dir)
            if not capsule_data:
                result['errors'].append("Impossible de charger les données de la capsule")
                return result
            
            # Vérifier si le script a été modifié récemment
            script_file = capsule_data['script_file']
            script_mtime = script_file.stat().st_mtime
            
            audio_file = capsule_dir / "capsule.mp3"
            pdf_file = capsule_dir / "capsule.pdf"
            
            # Régénération conditionnelle
            regenerate_audio = not audio_only and not pdf_only
            regenerate_pdf = not audio_only and not pdf_only
            
            if audio_only:
                regenerate_audio = True
                regenerate_pdf = False
            elif pdf_only:
                regenerate_audio = False
                regenerate_pdf = True
            
            # Vérifier si les fichiers existent et sont plus anciens que le script
            if regenerate_audio and audio_file.exists():
                audio_mtime = audio_file.stat().st_mtime
                if audio_mtime >= script_mtime:
                    logger.info(f"Audio de {capsule_dir.name} déjà à jour, régénération forcée")
            
            if regenerate_pdf and pdf_file.exists():
                pdf_mtime = pdf_file.stat().st_mtime
                if pdf_mtime >= script_mtime:
                    logger.info(f"PDF de {capsule_dir.name} déjà à jour, régénération forcée")
            
            # Régénérer l'audio si demandé
            if regenerate_audio:
                result['audio_success'] = self.regenerate_audio(capsule_dir, capsule_data)
                if not result['audio_success']:
                    result['errors'].append("Échec de la régénération audio")
            else:
                result['audio_success'] = True  # Non demandé, considéré comme succès
            
            # Régénérer le PDF si demandé
            if regenerate_pdf:
                result['pdf_success'] = self.regenerate_pdf(capsule_dir, capsule_data)
                if not result['pdf_success']:
                    result['errors'].append("Échec de la régénération PDF")
            else:
                result['pdf_success'] = True  # Non demandé, considéré comme succès
            
        except Exception as e:
            error_msg = f"Erreur générale lors de la régénération: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result
    
    def regenerate_all(self, audio_only: bool = False, pdf_only: bool = False) -> Dict:
        """Régénère toutes les capsules"""
        logger.info("Début de la régénération de toutes les capsules")
        
        capsule_dirs = self.find_capsule_directories()
        if not capsule_dirs:
            logger.warning("Aucune capsule trouvée")
            return {'total': 0, 'success': 0, 'failed': 0, 'results': []}
        
        logger.info(f"Trouvé {len(capsule_dirs)} capsule(s) à régénérer")
        
        results = {
            'total': len(capsule_dirs),
            'success': 0,
            'failed': 0,
            'results': []
        }
        
        for capsule_dir in capsule_dirs:
            result = self.regenerate_capsule(capsule_dir, audio_only, pdf_only)
            results['results'].append(result)
            
            if result['audio_success'] and result['pdf_success']:
                results['success'] += 1
                logger.info(f"[OK] Capsule {capsule_dir.name} regeneree avec succes")
            else:
                results['failed'] += 1
                logger.error(f"[ERREUR] Echec de la regeneration de {capsule_dir.name}: {', '.join(result['errors'])}")
        
        return results

def print_results(results: Dict):
    """Affiche un résumé des résultats"""
    print("\n" + "="*60)
    print("RESUME DE LA REGENERATION")
    print("="*60)
    
    if 'total' in results:
        # Résultats globaux
        print(f"Total de capsules: {results['total']}")
        print(f"Succes: {results['success']}")
        print(f"Echecs: {results['failed']}")
        
        if results['results']:
            print("\nDetail par capsule:")
            for result in results['results']:
                status = "OK" if (result['audio_success'] and result['pdf_success']) else "ERREUR"
                print(f"  [{status}] {result['capsule']}")
                if result['errors']:
                    for error in result['errors']:
                        print(f"    - {error}")
    else:
        # Résultat unique
        status = "OK" if (results['audio_success'] and results['pdf_success']) else "ERREUR"
        print(f"[{status}] {results['capsule']}")
        if results['errors']:
            for error in results['errors']:
                print(f"  - {error}")
    
    print("\n" + "="*60)

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Régénère les capsules audio et PDF à partir des scripts modifiés",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python regenerate_capsules.py                    # Régénère toutes les capsules
  python regenerate_capsules.py --capsule 001      # Régénère la capsule 001
  python regenerate_capsules.py --audio-only       # Régénère seulement l'audio
  python regenerate_capsules.py --pdf-only         # Régénère seulement les PDF
  python regenerate_capsules.py --capsule 005 --audio-only  # Audio de la capsule 005 seulement
        """
    )
    
    parser.add_argument(
        '--capsule',
        type=str,
        help='Numéro de la capsule à régénérer (ex: 001, 5, 042)'
    )
    
    parser.add_argument(
        '--audio-only',
        action='store_true',
        help='Régénère seulement les fichiers audio'
    )
    
    parser.add_argument(
        '--pdf-only',
        action='store_true',
        help='Régénère seulement les fichiers PDF'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='capsules_output',
        help='Dossier contenant les capsules (défaut: capsules_output)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mode verbose (plus de détails)'
    )
    
    args = parser.parse_args()
    
    # Configuration du niveau de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Vérification des arguments incompatibles
    if args.audio_only and args.pdf_only:
        print("Erreur: --audio-only et --pdf-only ne peuvent pas être utilisés ensemble")
        return 1
    
    try:
        # Initialiser le régénérateur
        regenerator = CapsuleRegenerator(args.output_dir)
        
        if args.capsule:
            # Régénérer une capsule spécifique
            capsule_dir = regenerator.get_capsule_by_number(args.capsule)
            if not capsule_dir:
                print(f"Erreur: Capsule {args.capsule} non trouvée dans {args.output_dir}")
                return 1
            
            print(f"Régénération de la capsule {capsule_dir.name}...")
            result = regenerator.regenerate_capsule(capsule_dir, args.audio_only, args.pdf_only)
            print_results(result)
            
            return 0 if (result['audio_success'] and result['pdf_success']) else 1
        
        else:
            # Régénérer toutes les capsules
            print("Régénération de toutes les capsules...")
            results = regenerator.regenerate_all(args.audio_only, args.pdf_only)
            print_results(results)
            
            return 0 if results['failed'] == 0 else 1
    
    except Exception as e:
        logger.error(f"Erreur fatale: {str(e)}")
        print(f"Erreur: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())