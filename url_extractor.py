"""
Module pour extraire le contenu des pages web à partir des URLs
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict
import time
import re
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class URLExtractor:
    """Classe pour extraire le contenu des URLs"""
    
    def __init__(self):
        self.session = self._create_session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _create_session(self) -> requests.Session:
        """Crée une session HTTP avec retry automatique"""
        session = requests.Session()
        
        # Configuration du retry
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def extract_url_from_excel_link(self, link_text: str, row_data: Dict, column: str) -> Optional[str]:
        """
        Extrait l'URL réelle d'un lien Excel
        Si pas d'URL, essaye de deviner à partir du texte
        """
        # Si on a déjà l'URL dans les données
        if isinstance(row_data.get(column), dict):
            url = row_data[column].get('url', '').strip()
            if url and self._is_valid_url(url):
                return url
        
        # Sinon, essayer de deviner l'URL à partir du texte
        text = link_text.strip()
        if not text:
            return None
        
        # Patterns courants pour deviner les URLs
        if 'cnil' in text.lower():
            return self._search_cnil_url(text)
        elif 'legifrance' in text.lower():
            return self._search_legifrance_url(text)
        elif 'service-public' in text.lower():
            return self._search_service_public_url(text)
        else:
            # Recherche générale
            return self._search_general_url(text)
    
    def _is_valid_url(self, url: str) -> bool:
        """Vérifie si une URL est valide"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _search_cnil_url(self, text: str) -> Optional[str]:
        """Recherche spécifique pour le site CNIL"""
        # Patterns courants CNIL
        base_url = "https://www.cnil.fr"
        
        # Quelques URLs connues
        known_patterns = {
            'donnée sensible': '/fr/definition/donnee-sensible',
            'données de santé': '/fr/definition/donnee-de-sante',
            'donnée à caractère personnel': '/fr/definition/donnee-caractere-personnel',
            'pseudonymisation': '/fr/definition/pseudonymisation',
            'anonymisation': '/fr/definition/anonymisation'
        }
        
        text_lower = text.lower()
        for pattern, path in known_patterns.items():
            if pattern in text_lower:
                return base_url + path
        
        # Recherche plus générale sur le site CNIL
        return f"{base_url}/fr/rechercher?search={text.split('|')[0].strip()}"
    
    def _search_legifrance_url(self, text: str) -> Optional[str]:
        """Recherche spécifique pour Légifrance"""
        return f"https://www.legifrance.gouv.fr/search/all?tab=all&searchField=ALL&query={text.split('|')[0].strip()}"
    
    def _search_service_public_url(self, text: str) -> Optional[str]:
        """Recherche spécifique pour Service Public"""
        return f"https://www.service-public.fr/recherche?keyword={text.split('|')[0].strip()}"
    
    def _search_general_url(self, text: str) -> Optional[str]:
        """Recherche générale via DuckDuckGo"""
        # Utiliser DuckDuckGo pour éviter les problèmes avec Google
        query = text.split('|')[0].strip()
        return f"https://duckduckgo.com/?q={query}"
    
    def extract_content(self, url: str) -> Optional[str]:
        """
        Extrait le contenu textuel d'une page web
        """
        if not url or not self._is_valid_url(url):
            logger.warning(f"URL invalide: {url}")
            return None
        
        try:
            logger.info(f"Extraction du contenu de: {url}")
            
            # Faire la requête HTTP
            response = self.session.get(
                url, 
                headers=self.headers, 
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Parser le HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Supprimer les éléments indésirables
            for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
                element.decompose()
            
            # Extraire le contenu principal
            content = self._extract_main_content(soup)
            
            # Nettoyer le texte
            content = self._clean_text(content)
            
            if len(content) < 100:
                logger.warning(f"Contenu très court extrait de {url}: {len(content)} caractères")
            else:
                logger.info(f"Contenu extrait avec succès: {len(content)} caractères")
            
            return content
            
        except requests.RequestException as e:
            logger.error(f"Erreur HTTP lors de l'extraction de {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de {url}: {str(e)}")
            return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extrait le contenu principal d'une page HTML
        """
        # Essayer différents sélecteurs pour le contenu principal
        content_selectors = [
            'main',
            'article',
            '.content',
            '#content',
            '.main-content',
            '#main-content',
            '.article-content',
            '.post-content',
            'div[role="main"]'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text()
        
        # Si aucun sélecteur spécifique, prendre le body
        body = soup.find('body')
        if body:
            return body.get_text()
        
        # En dernier recours, tout le document
        return soup.get_text()
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoie le texte extrait
        """
        if not text:
            return ""
        
        # Supprimer les espaces multiples et normaliser
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les caractères spéciaux indésirables
        text = re.sub(r'[^\w\s\.,;:!?()\-\'"àâäéèêëïîôöùûüÿç]', ' ', text)
        
        # Supprimer les espaces en début/fin
        text = text.strip()
        
        # Limiter la longueur pour éviter les contenus trop longs
        max_length = 10000  # 10k caractères max
        if len(text) > max_length:
            text = text[:max_length] + "..."
            logger.info(f"Contenu tronqué à {max_length} caractères")
        
        return text
    
    def test_url(self, url: str) -> Dict:
        """
        Teste une URL et retourne des informations de diagnostic
        """
        result = {
            'url': url,
            'valid': False,
            'accessible': False,
            'content_length': 0,
            'error': None,
            'title': None
        }
        
        try:
            if not self._is_valid_url(url):
                result['error'] = "URL invalide"
                return result
            
            result['valid'] = True
            
            # Tester l'accès
            response = self.session.head(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            result['accessible'] = True
            
            # Obtenir le contenu
            content = self.extract_content(url)
            if content:
                result['content_length'] = len(content)
                
                # Essayer d'obtenir le titre
                response = self.session.get(url, headers=self.headers, timeout=30)
                soup = BeautifulSoup(response.content, 'html.parser')
                title_tag = soup.find('title')
                if title_tag:
                    result['title'] = title_tag.get_text().strip()
            
        except Exception as e:
            result['error'] = str(e)
        
        return result

# Fonction utilitaire pour tester le module
def test_url_extractor(url: str):
    """Fonction de test pour l'extracteur d'URLs"""
    extractor = URLExtractor()
    
    print(f"Test de l'URL: {url}")
    
    # Test de diagnostic
    diagnosis = extractor.test_url(url)
    print("\n=== DIAGNOSTIC ===")
    print(f"URL valide: {diagnosis['valid']}")
    print(f"Accessible: {diagnosis['accessible']}")
    print(f"Longueur du contenu: {diagnosis['content_length']}")
    print(f"Titre: {diagnosis['title']}")
    if diagnosis['error']:
        print(f"Erreur: {diagnosis['error']}")
    
    # Test d'extraction
    if diagnosis['accessible']:
        content = extractor.extract_content(url)
        if content:
            print(f"\n=== CONTENU EXTRAIT ({len(content)} caractères) ===")
            print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print("\nÉchec de l'extraction du contenu")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_url_extractor(sys.argv[1])
    else:
        print("Usage: python url_extractor.py <url>")