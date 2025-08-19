"""
Module pour traiter les fichiers Excel contenant les données des capsules
"""

import pandas as pd
import openpyxl
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Classe pour traiter les fichiers Excel"""
    
    def __init__(self):
        self.required_columns = ['Compétences', 'Thématiques', 'Sujets abordés']
        self.link_columns = ['Lien 1', 'Lien 2', 'Lien 3', 'Lien 4']
    
    def read_excel(self, file_path: str) -> List[Dict]:
        """
        Lit le fichier Excel et retourne une liste de dictionnaires
        Chaque dictionnaire représente une ligne avec ses données
        """
        try:
            logger.info(f"Lecture du fichier Excel: {file_path}")
            
            # Utiliser openpyxl pour préserver les liens hypertexte
            workbook = openpyxl.load_workbook(file_path)
            worksheet = workbook.active
            
            # Lire les en-têtes
            headers = []
            for cell in worksheet[1]:
                headers.append(cell.value if cell.value else "")
            
            logger.info(f"En-têtes trouvés: {headers}")
            
            # Vérifier que les colonnes requises sont présentes
            missing_columns = [col for col in self.required_columns if col not in headers]
            if missing_columns:
                raise ValueError(f"Colonnes manquantes dans le fichier Excel: {missing_columns}")
            
            # Lire les données
            rows_data = []
            for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=False), 2):
                row_dict = {}
                
                for col_idx, cell in enumerate(row):
                    if col_idx < len(headers):
                        col_name = headers[col_idx]
                        
                        if col_name in self.link_columns:
                            # Pour les colonnes de liens, extraire l'URL du lien hypertexte
                            if cell.hyperlink:
                                # Lien hypertexte présent
                                row_dict[col_name] = {
                                    'text': cell.value if cell.value else "",
                                    'url': cell.hyperlink.target if cell.hyperlink.target else ""
                                }
                            else:
                                # Pas de lien hypertexte, juste le texte
                                value = cell.value if cell.value else ""
                                if value and str(value).strip():
                                    row_dict[col_name] = {
                                        'text': str(value).strip(),
                                        'url': ""  # URL sera extraite plus tard si nécessaire
                                    }
                                else:
                                    row_dict[col_name] = None
                        else:
                            # Colonnes normales
                            row_dict[col_name] = cell.value if cell.value else ""
                
                # Ne garder que les lignes qui ont au moins un sujet
                if row_dict.get('Sujets abordés', '').strip():
                    rows_data.append(row_dict)
                else:
                    logger.debug(f"Ligne {row_idx} ignorée (pas de sujet)")
            
            logger.info(f"Lecture terminée: {len(rows_data)} lignes de données valides")
            return rows_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier Excel: {str(e)}")
            raise
    
    def get_links_from_row(self, row_data: Dict) -> List[Dict]:
        """
        Extrait tous les liens valides d'une ligne
        Retourne une liste de dictionnaires avec 'text' et 'url'
        """
        links = []
        
        for link_col in self.link_columns:
            if link_col in row_data and row_data[link_col]:
                link_data = row_data[link_col]
                if isinstance(link_data, dict):
                    text = link_data.get('text', '').strip()
                    url = link_data.get('url', '').strip()
                    
                    if text:  # Au minimum, il faut un texte
                        links.append({
                            'text': text,
                            'url': url,
                            'column': link_col
                        })
        
        return links
    
    def validate_row_data(self, row_data: Dict) -> tuple[bool, List[str]]:
        """
        Valide les données d'une ligne
        Retourne (is_valid, list_of_errors)
        """
        errors = []
        
        # Vérifier les colonnes requises
        for col in self.required_columns:
            if col not in row_data or not str(row_data[col]).strip():
                errors.append(f"Colonne '{col}' manquante ou vide")
        
        # Vérifier qu'il y a au moins un lien
        links = self.get_links_from_row(row_data)
        if not links:
            errors.append("Aucun lien externe trouvé")
        
        return len(errors) == 0, errors
    
    def get_summary_stats(self, rows_data: List[Dict]) -> Dict:
        """
        Calcule des statistiques sur les données
        """
        stats = {
            'total_rows': len(rows_data),
            'rows_with_links': 0,
            'total_links': 0,
            'thematiques': {},
            'competences': {}
        }
        
        for row in rows_data:
            links = self.get_links_from_row(row)
            if links:
                stats['rows_with_links'] += 1
                stats['total_links'] += len(links)
            
            # Compter les thématiques
            them = row.get('Thématiques', 'Non spécifié')
            stats['thematiques'][them] = stats['thematiques'].get(them, 0) + 1
            
            # Compter les compétences
            comp = row.get('Compétences', 'Non spécifié')
            stats['competences'][comp] = stats['competences'].get(comp, 0) + 1
        
        return stats

# Fonction utilitaire pour tester le module
def test_excel_processor(file_path: str):
    """Fonction de test pour le processeur Excel"""
    processor = ExcelProcessor()
    
    try:
        rows_data = processor.read_excel(file_path)
        print(f"Lecture réussie: {len(rows_data)} lignes")
        
        # Afficher les statistiques
        stats = processor.get_summary_stats(rows_data)
        print("\n=== STATISTIQUES ===")
        print(f"Lignes totales: {stats['total_rows']}")
        print(f"Lignes avec liens: {stats['rows_with_links']}")
        print(f"Liens totaux: {stats['total_links']}")
        
        print("\nThématiques:")
        for them, count in sorted(stats['thematiques'].items()):
            print(f"  - {them}: {count}")
        
        # Afficher quelques exemples
        print("\n=== EXEMPLES ===")
        for i, row in enumerate(rows_data[:3]):
            print(f"\nLigne {i+1}:")
            print(f"  Compétences: {row.get('Compétences', 'N/A')}")
            print(f"  Thématiques: {row.get('Thématiques', 'N/A')}")
            print(f"  Sujets: {row.get('Sujets abordés', 'N/A')}")
            
            links = processor.get_links_from_row(row)
            print(f"  Liens ({len(links)}):")
            for link in links:
                print(f"    - {link['text']} -> {link['url']}")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_excel_processor(sys.argv[1])
    else:
        print("Usage: python excel_processor.py <fichier_excel>")
