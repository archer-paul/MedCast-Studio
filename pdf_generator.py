"""
Module pour générer des PDF - Version simplifiée sans erreurs
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import shutil
import re

logger = logging.getLogger(__name__)

class PDFGenerator:
    """Classe pour générer des PDF à partir des scripts de capsules"""
    
    def __init__(self):
        self.temp_dir = None
        self._check_latex_installation()
    
    def _check_latex_installation(self):
        """Vérifie que LaTeX est installé"""
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("LaTeX trouvé et disponible")
            else:
                logger.warning("LaTeX non trouvé, utilisation du fallback")
        except:
            logger.warning("LaTeX non disponible, utilisation du fallback")
    
    def generate_pdf(self, script_data: Dict, output_path: Path, metadata: Dict) -> Path:
        """Génère un PDF à partir des données de script"""
        try:
            logger.info(f"Génération PDF: {output_path}")
            
            if self._latex_available():
                return self._generate_pdf_latex(script_data, output_path, metadata)
            else:
                return self._generate_pdf_fallback(script_data, output_path, metadata)
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération PDF: {str(e)}")
            return self._create_text_fallback(script_data, output_path, metadata)
    
    def _latex_available(self) -> bool:
        """Vérifie si LaTeX est disponible"""
        try:
            subprocess.run(['pdflatex', '--version'], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def _generate_pdf_latex(self, script_data: Dict, output_path: Path, metadata: Dict) -> Path:
        """Génère le PDF avec LaTeX"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Créer le fichier LaTeX
            latex_content = self._create_latex_content(script_data, metadata)
            latex_file = temp_path / "capsule.tex"
            
            # Écrire le fichier avec l'encodage correct
            with open(latex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            try:
                # Première compilation avec pdflatex
                result1 = subprocess.run([
                    'pdflatex', 
                    '-interaction=nonstopmode',
                    '-output-directory', str(temp_path),
                    str(latex_file)
                ], capture_output=True, text=True, timeout=60)
                
                if result1.returncode != 0:
                    # Log l'erreur pour debug
                    logger.error(f"Erreur pdflatex (première passe): {result1.stderr}")
                    logger.error(f"Sortie pdflatex: {result1.stdout}")
                    # Essayer de trouver le fichier .log
                    log_file = temp_path / "capsule.log"
                    if log_file.exists():
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            logger.error(f"Contenu du log LaTeX: {f.read()}")
                    raise subprocess.CalledProcessError(result1.returncode, result1.args)
                
                # Deuxième passe pour la table des matières
                result2 = subprocess.run([
                    'pdflatex', 
                    '-interaction=nonstopmode',
                    '-output-directory', str(temp_path),
                    str(latex_file)
                ], capture_output=True, text=True, timeout=60)
                
                # Copier le PDF
                pdf_temp = temp_path / "capsule.pdf"
                if pdf_temp.exists():
                    shutil.copy2(pdf_temp, output_path)
                    logger.info(f"PDF généré avec succès: {output_path}")
                    return output_path
                else:
                    raise FileNotFoundError("PDF non généré par LaTeX")
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"Erreur de compilation LaTeX: {e}")
                # En cas d'erreur, utiliser le fallback
                return self._generate_pdf_fallback(script_data, output_path, metadata)
    
    def _create_latex_content(self, script_data: Dict, metadata: Dict) -> str:
        """Crée le contenu LaTeX"""
        
        def latex_escape(text):
            """Échappe les caractères spéciaux LaTeX"""
            if not text:
                return ""
            
            # Nettoyer d'abord les caractères problématiques
            text = str(text)
            
            # Nettoyer les artefacts de formatage avant l'échappement
            text = re.sub(r'textbf\{\s*\d+\s*\}', '', text)  # Supprimer textbf{1}, textbf{2}, etc.
            text = re.sub(r'\\textbf\{\s*\d+\s*\}', '', text)  # Supprimer \textbf{1}, \textbf{2}, etc.
            text = re.sub(r'textbf\{[^}]*\}', '', text)  # Supprimer tous les textbf{...}
            text = re.sub(r'\\textbf\{[^}]*\}', '', text)  # Supprimer tous les \textbf{...}
            
            # Remplacements de base - ORDRE IMPORTANT !
            text = text.replace('\\', '\\textbackslash ')
            text = text.replace('{', '\\{')
            text = text.replace('}', '\\}')
            text = text.replace('$', '\\$')
            text = text.replace('&', '\\&')
            text = text.replace('%', '\\%')
            text = text.replace('#', '\\#')
            text = text.replace('^', '\\textasciicircum ')
            text = text.replace('_', '\\_')
            text = text.replace('~', '\\textasciitilde ')
            
            # Nettoyer les lignes vides multiples
            text = re.sub(r'\n\s*\n', '\n\n', text)
            
            # Supprimer les caractères de contrôle
            text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
            
            # Nettoyer les espaces multiples
            text = re.sub(r' +', ' ', text)
            
            return text
        
        def process_markdown(text):
            """Convertit le Markdown en LaTeX"""
            # **texte** -> \textbf{texte}
            text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\\1}', text)
            return text
        
        # Extraire les données
        title = metadata.get('sujet', 'Capsule apprentissage')
        competence = metadata.get('competence', '')
        thematique = metadata.get('thematique', '')
        script = script_data.get('script', '')
        
        # Traiter le script
        script = process_markdown(script)
        
        # Échapper tout
        title_clean = latex_escape(title)
        competence_clean = latex_escape(competence)
        thematique_clean = latex_escape(thematique)
        script_clean = latex_escape(script)
        
        # Créer le contenu LaTeX
        latex_content = f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage[french]{{babel}}
\\usepackage{{geometry}}
\\usepackage{{fancyhdr}}
\\usepackage{{titlesec}}
\\usepackage{{xcolor}}
\\usepackage{{tcolorbox}}
\\usepackage{{enumitem}}
\\usepackage{{hyperref}}
\\usepackage{{lmodern}}

% Configuration
\\geometry{{margin=2.5cm}}
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{Capsule apprentissage - Sante Publique}}
\\fancyhead[R]{{\\thepage}}
\\fancyfoot[C]{{Universite - Formation Medicale}}

% Couleurs
\\definecolor{{maincolor}}{{RGB}}{{0,102,153}}
\\definecolor{{accentcolor}}{{RGB}}{{0,153,204}}
\\definecolor{{qcmcolor}}{{RGB}}{{240,248,255}}

% Titres
\\titleformat{{\\section}}{{\\Large\\bfseries\\color{{maincolor}}}}{{\\thesection}}{{1em}}{{}}

% Boîte QCM
\\newtcolorbox{{qcmbox}}{{
    colframe=maincolor,
    colback=qcmcolor,
    boxrule=1.5pt,
    arc=4pt,
    left=10pt,
    right=10pt,
    top=8pt,
    bottom=8pt,
    title=QCM - Question a choix multiple,
    fonttitle=\\bfseries,
    coltitle=white,
    colbacktitle=maincolor
}}

\\begin{{document}}

% Page de titre
\\begin{{titlepage}}
    \\centering
    \\vspace*{{2cm}}
    
    {{\\Huge\\bfseries\\color{{maincolor}} Capsule d'Apprentissage}}\\\\[1cm]
    {{\\Large\\color{{accentcolor}} {title_clean}}}\\\\[2cm]
    
    \\begin{{tcolorbox}}[colframe=maincolor, colback=white, boxrule=1pt]
        \\textbf{{Competence :}} {competence_clean}\\\\[0.5cm]
        \\textbf{{Thematique :}} {thematique_clean}\\\\[0.5cm]
        \\textbf{{Date :}} {datetime.now().strftime("%d/%m/%Y")}
    \\end{{tcolorbox}}
    
    \\vfill
    
    {{\\large Formation en Sante Publique}}\\\\
    {{\\large Niveau Licence - Medecine}}
    
\\end{{titlepage}}

% Table des matières
\\tableofcontents
\\newpage

% Contenu
\\section{{Objectifs d'apprentissage}}

Cette capsule a pour objectif de vous permettre de maitriser les aspects reglementaires lies au traitement des donnees de sante.

\\section{{Contenu de la capsule}}

{self._format_script_simple(script_clean)}

\\section{{Synthese}}

Cette capsule vous a presente les elements essentiels. La reglementation evolue constamment.

\\section{{Pour aller plus loin}}

\\begin{{itemize}}
    \\item Consultez regulierement le site de la CNIL
    \\item Referez-vous aux textes reglementaires
    \\item Participez aux formations continues
\\end{{itemize}}

\\end{{document}}
"""
        
        return latex_content
    
    def _format_script_simple(self, script: str) -> str:
        """Formate le script de manière simple"""
        
        if not script:
            return "Contenu non disponible."
        
        # Nettoyer le script des artefacts d'échappement et de formatage
        script = re.sub(r'\\textbackslash\s*', ' ', script)
        script = re.sub(r'textbf\{\s*\d+\s*\}', '', script)  # Supprimer textbf{1}, textbf{2}, etc.
        script = re.sub(r'\\textbf\{\s*\d+\s*\}', '', script)  # Supprimer \textbf{1}, \textbf{2}, etc.
        script = re.sub(r'textbf\{[^}]*\}', '', script)  # Supprimer tous les textbf{...}
        script = re.sub(r'\\textbf\{[^}]*\}', '', script)  # Supprimer tous les \textbf{...}
        
        # Séparer le contenu principal des QCM de manière plus robuste
        parts = re.split(r'={3,}\s*QCM\s+\d+\s*={3,}', script, flags=re.IGNORECASE)
        main_content = parts[0] if parts else script
        
        # Récupérer les QCM séparément
        qcm_matches = list(re.finditer(r'={3,}\s*QCM\s+(\d+)\s*={3,}\s*\n\n(.*?)(?=\n\n={3,}|$)', script, re.DOTALL | re.IGNORECASE))
        
        # Traiter le contenu principal
        formatted_content = ""
        
        # Nettoyer et diviser en paragraphes
        paragraphs = [p.strip() for p in main_content.split('\n\n') if p.strip()]
        
        qcm_inserted = 0
        for i, paragraph in enumerate(paragraphs):
            # Nettoyer le paragraphe des artefacts
            paragraph = re.sub(r'textbf\{\s*\d+\s*\}', '', paragraph)
            paragraph = re.sub(r'\\textbf\{\s*\d+\s*\}', '', paragraph)
            paragraph = re.sub(r'textbf\{[^}]*\}', '', paragraph)
            paragraph = re.sub(r'\\textbf\{[^}]*\}', '', paragraph)
            paragraph = re.sub(r'\s+', ' ', paragraph).strip()
            
            if not paragraph:
                continue
            
            # Traiter les titres en gras
            if paragraph.startswith('**') and paragraph.endswith('**'):
                title = paragraph[2:-2].strip()
                formatted_content += f"\\subsection*{{{title}}}\n\n"
            else:
                # Paragraphe normal
                formatted_content += paragraph + "\n\n"
            
            # Insérer un QCM après certains paragraphes
            if (qcm_inserted < len(qcm_matches) and 
                i > 0 and 
                (i + 1) % max(1, len(paragraphs) // (len(qcm_matches) + 1)) == 0):
                
                match = qcm_matches[qcm_inserted]
                qcm_num = match.group(1)
                qcm_content = match.group(2)
                
                formatted_content += "\\vspace{0.5cm}\n"
                formatted_content += "\\begin{qcmbox}\n"
                formatted_content += self._format_qcm_simple(qcm_content.strip())
                formatted_content += "\\end{qcmbox}\n"
                formatted_content += "\\vspace{0.5cm}\n\n"
                qcm_inserted += 1
        
        # Ajouter les QCM restants à la fin
        while qcm_inserted < len(qcm_matches):
            match = qcm_matches[qcm_inserted]
            qcm_num = match.group(1)
            qcm_content = match.group(2)
            
            formatted_content += "\\vspace{0.5cm}\n"
            formatted_content += "\\begin{qcmbox}\n"
            formatted_content += self._format_qcm_simple(qcm_content.strip())
            formatted_content += "\\end{qcmbox}\n"
            formatted_content += "\\vspace{0.5cm}\n\n"
            qcm_inserted += 1
        
        return formatted_content.strip()
    
    def _format_qcm_simple(self, qcm_text: str) -> str:
        """Formate un QCM de manière simple"""
        
        if not qcm_text:
            return ""
        
        # Nettoyer le texte des artefacts
        qcm_text = re.sub(r'\\textbackslash\s*', ' ', qcm_text)
        qcm_text = re.sub(r'textbf\{\s*\d+\s*\}', '', qcm_text)  # Supprimer textbf{1}, textbf{2}, etc.
        qcm_text = re.sub(r'\\textbf\{\s*\d+\s*\}', '', qcm_text)  # Supprimer \textbf{1}, \textbf{2}, etc.
        qcm_text = re.sub(r'textbf\{[^}]*\}', '', qcm_text)  # Supprimer tous les textbf{...}
        qcm_text = re.sub(r'\\textbf\{[^}]*\}', '', qcm_text)  # Supprimer tous les \textbf{...}
        qcm_text = re.sub(r'\\text[a-z]+\{[^}]*\}', '', qcm_text)
        
        lines = [line.strip() for line in qcm_text.split('\n') if line.strip()]
        result = ""
        
        situation = ""
        question = ""
        options = []
        correct_answer = ""
        explanation = ""
        
        # Parser le contenu du QCM
        current_section = ""
        for line in lines:
            # Nettoyer chaque ligne des artefacts
            line = re.sub(r'textbf\{\s*\d+\s*\}', '', line)
            line = re.sub(r'\\textbf\{\s*\d+\s*\}', '', line)
            line = re.sub(r'textbf\{[^}]*\}', '', line)
            line = re.sub(r'\\textbf\{[^}]*\}', '', line)
            line = line.strip()
            
            if not line:
                continue
            
            if line.upper().startswith('SITUATION:'):
                current_section = "situation"
                situation = line[10:].strip()
            elif line.upper().startswith('QUESTION:'):
                current_section = "question"
                question = line[9:].strip()
            elif re.match(r'^[A-D]\)', line, re.IGNORECASE):
                option_text = line[2:].strip()
                options.append(option_text)
            elif line.upper().startswith(('REPONSE CORRECTE:', 'RÉPONSE CORRECTE:')):
                correct_answer = re.split(r':', line, 1)[1].strip()
            elif line.upper().startswith('EXPLICATION:'):
                current_section = "explanation"
                explanation = line[12:].strip()
            else:
                # Continuer la section en cours
                if current_section == "situation" and situation:
                    situation += " " + line
                elif current_section == "question" and question:
                    question += " " + line
                elif current_section == "explanation" and explanation:
                    explanation += " " + line
        
        # Construire le QCM formaté
        if situation:
            result += f"\\textbf{{Situation :}} {situation}\\par\n\\vspace{{0.3cm}}\n\n"
        
        if question:
            result += f"\\textbf{{Question :}} {question}\\par\n\\vspace{{0.3cm}}\n\n"
        
        if options:
            result += "\\begin{enumerate}[label=\\Alph*), leftmargin=*, itemsep=3pt]\n"
            for option in options:
                result += f"\\item {option}\n"
            result += "\\end{enumerate}\n\\vspace{0.3cm}\n\n"
        
        if correct_answer:
            result += f"\\textbf{{Reponse correcte :}} {correct_answer}\\par\n\\vspace{{0.2cm}}\n\n"
        
        if explanation:
            result += f"\\textbf{{Explication :}} {explanation}\\par\n"
        
        return result.strip()
    
    def _generate_pdf_fallback(self, script_data: Dict, output_path: Path, metadata: Dict) -> Path:
        """Génère un PDF avec reportlab"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Titre
            title = metadata.get('sujet', 'Capsule apprentissage')
            story.append(Paragraph(f"<b>{title}</b>", styles['Title']))
            story.append(Spacer(1, 20))
            
            # Contenu
            script = script_data.get('script', '')
            paragraphs = script.split('\\n\\n')
            
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para, styles['Normal']))
                    story.append(Spacer(1, 12))
            
            doc.build(story)
            logger.info(f"PDF généré avec reportlab: {output_path}")
            return output_path
            
        except ImportError:
            logger.warning("Reportlab non disponible")
            return self._create_text_fallback(script_data, output_path, metadata)
    
    def _create_text_fallback(self, script_data: Dict, output_path: Path, metadata: Dict) -> Path:
        """Crée un fichier texte de fallback"""
        
        text_path = output_path.with_suffix('.txt')
        
        content = f"""CAPSULE D'APPRENTISSAGE - SANTE PUBLIQUE
========================================

Titre: {metadata.get('sujet', 'N/A')}
Competence: {metadata.get('competence', 'N/A')}
Thematique: {metadata.get('thematique', 'N/A')}
Date: {datetime.now().strftime('%d/%m/%Y')}

CONTENU
=======

{script_data.get('script', 'Contenu non disponible')}

INFORMATIONS
============

Duree estimee: {script_data.get('duration_estimate', 'Non calculee')}
Nombre de QCM: {len(script_data.get('qcm_data', []))}
"""
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Fichier texte cree: {text_path}")
        return text_path