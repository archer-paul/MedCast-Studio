#!/usr/bin/env python3
"""
Programme principal pour générer des capsules d'apprentissage en santé publique
Utilise les APIs GCP (Gemini, Text-to-Speech) pour créer du contenu éducatif
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional
import json

from excel_processor import ExcelProcessor
from content_generator import ContentGenerator
from pdf_generator import PDFGenerator
from audio_generator import AudioGenerator
from url_extractor import URLExtractor

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('capsules_generation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CapsuleGenerator:
    """Classe principale pour orchestrer la génération des capsules"""
    
    def __init__(self, excel_file: str, output_dir: str = "capsules_output"):
        self.excel_file = excel_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialisation des composants
        self.excel_processor = ExcelProcessor()
        self.url_extractor = URLExtractor()
        self.content_generator = ContentGenerator()
        self.pdf_generator = PDFGenerator()
        self.audio_generator = AudioGenerator()
        
    def process_single_capsule(self, row_data: Dict, row_index: int) -> bool:
        """Traite une seule capsule"""
        try:
            logger.info(f"Traitement de la capsule {row_index}: {row_data.get('Sujets abordés', 'N/A')}")
            
            # Extraire les liens valides
            links = self._extract_valid_links(row_data)
            if not links:
                logger.error(f"Ligne {row_index}: Aucun lien externe trouvé")
                return False
            
            # Créer le dossier de sortie pour cette capsule
            capsule_dir = self.output_dir / f"capsule_{row_index:03d}_{self._sanitize_filename(row_data.get('Sujets abordés', ''))}"
            capsule_dir.mkdir(exist_ok=True)
            
            # Extraire le contenu des URLs
            logger.info(f"Extraction du contenu de {len(links)} liens")
            url_contents = []
            for link_text, url in links:
                content = self.url_extractor.extract_content(url)
                if content:
                    url_contents.append({
                        'title': link_text,
                        'url': url,
                        'content': content
                    })
            
            if not url_contents:
                logger.error(f"Ligne {row_index}: Impossible d'extraire le contenu des liens")
                return False
            
            # Générer le script de la capsule
            logger.info("Génération du script de la capsule")
            script_data = self.content_generator.generate_capsule_script(
                competence=row_data.get('Compétences', ''),
                thematique=row_data.get('Thématiques', ''),
                sujet=row_data.get('Sujets abordés', ''),
                url_contents=url_contents
            )
            
            # Sauvegarder le script en texte
            script_file = capsule_dir / "script.txt"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_data['script'])
            logger.info(f"Script sauvegardé: {script_file}")
            
            # Sauvegarder les métadonnées
            metadata_file = capsule_dir / "metadata.json"
            metadata = {
                'competence': row_data.get('Compétences', ''),
                'thematique': row_data.get('Thématiques', ''),
                'sujet': row_data.get('Sujets abordés', ''),
                'sources': [{'title': uc['title'], 'url': uc['url']} for uc in url_contents],
                'qcm_count': len(script_data.get('qcm_positions', [])),
                'duration_estimate': script_data.get('duration_estimate', '5-10 minutes')
            }
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Générer le PDF
            logger.info("Génération du PDF")
            pdf_file = self.pdf_generator.generate_pdf(
                script_data=script_data,
                output_path=capsule_dir / "capsule.pdf",
                metadata=metadata
            )
            
            # Générer l'audio
            logger.info("Génération de l'audio")
            audio_file = self.audio_generator.generate_audio(
                script_text=script_data['script_for_audio'],
                output_path=capsule_dir / "capsule.mp3"
            )
            
            logger.info(f"Capsule {row_index} générée avec succès dans {capsule_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la capsule {row_index}: {str(e)}")
            return False
    
    def _extract_valid_links(self, row_data: Dict) -> List[tuple]:
        """Extrait les liens valides d'une ligne"""
        links = []
        for i in range(1, 5):  # Lien 1 à Lien 4
            link_key = f"Lien {i}"
            if link_key in row_data and row_data[link_key] and str(row_data[link_key]).strip() != "":
                link_text = str(row_data[link_key])
                url = self.url_extractor.extract_url_from_excel_link(link_text, row_data, link_key)
                if url:
                    links.append((link_text, url))
        return links
    
    def _sanitize_filename(self, filename: str) -> str:
        """Nettoie un nom de fichier"""
        import re
        # Remplace les caractères non autorisés par des underscores
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limite la longueur
        return filename[:50] if len(filename) > 50 else filename
    
    def process_all_capsules(self):
        """Traite toutes les capsules du fichier Excel"""
        try:
            logger.info(f"Début du traitement du fichier {self.excel_file}")
            
            # Lire le fichier Excel
            rows_data = self.excel_processor.read_excel(self.excel_file)
            logger.info(f"Trouvé {len(rows_data)} lignes à traiter")
            
            success_count = 0
            error_count = 0
            
            for i, row_data in enumerate(rows_data, 1):
                if self.process_single_capsule(row_data, i):
                    success_count += 1
                else:
                    error_count += 1
            
            logger.info(f"Traitement terminé: {success_count} succès, {error_count} erreurs")
            
            # Générer un rapport de synthèse
            self._generate_summary_report(success_count, error_count, rows_data)
            
        except Exception as e:
            logger.error(f"Erreur fatale: {str(e)}")
            raise
    
    def _generate_summary_report(self, success_count: int, error_count: int, rows_data: List[Dict]):
        """Génère un rapport de synthèse"""
        report_file = self.output_dir / "summary_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== RAPPORT DE GÉNÉRATION DES CAPSULES ===\n\n")
            f.write(f"Fichier source: {self.excel_file}\n")
            f.write(f"Nombre total de lignes: {len(rows_data)}\n")
            f.write(f"Capsules générées avec succès: {success_count}\n")
            f.write(f"Erreurs: {error_count}\n")
            f.write(f"Taux de réussite: {success_count/len(rows_data)*100:.1f}%\n")
            f.write(f"Répertoire de sortie: {self.output_dir}\n\n")
            
            # Liste des thématiques traitées
            thematiques = {}
            for row in rows_data:
                them = row.get('Thématiques', 'Non spécifié')
                thematiques[them] = thematiques.get(them, 0) + 1
            
            f.write("=== RÉPARTITION PAR THÉMATIQUES ===\n")
            for them, count in sorted(thematiques.items()):
                f.write(f"- {them}: {count} capsules\n")
        
        logger.info(f"Rapport de synthèse généré: {report_file}")

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Générateur de capsules d'apprentissage")
    parser.add_argument("excel_file", help="Chemin vers le fichier Excel")
    parser.add_argument("--output", "-o", default="capsules_output", 
                       help="Répertoire de sortie (défaut: capsules_output)")
    parser.add_argument("--single", "-s", type=int, 
                       help="Traiter une seule ligne (numéro de ligne)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.excel_file):
        logger.error(f"Fichier Excel non trouvé: {args.excel_file}")
        return 1
    
    generator = CapsuleGenerator(args.excel_file, args.output)
    
    if args.single:
        # Traiter une seule ligne pour les tests
        rows_data = generator.excel_processor.read_excel(args.excel_file)
        if 1 <= args.single <= len(rows_data):
            success = generator.process_single_capsule(rows_data[args.single - 1], args.single)
            return 0 if success else 1
        else:
            logger.error(f"Numéro de ligne invalide: {args.single}")
            return 1
    else:
        # Traiter tous
        generator.process_all_capsules()
        return 0

if __name__ == "__main__":
    sys.exit(main())
