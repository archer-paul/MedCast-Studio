# MedCast Studio

**[English](README.md) | Français**

**MedCast Studio** est un générateur automatisé de capsules d'apprentissage pour la formation médicale et en santé publique. Il transforme vos contenus pédagogiques en capsules multimédia complètes incluant texte, PDF et audio avec voix off.

## Vue d'ensemble

MedCast Studio analyse vos fichiers Excel contenant les thématiques d'apprentissage et les sources de référence, puis génère automatiquement des capsules éducatives structurées avec QCM intégrés. Chaque capsule est disponible en trois formats : script textuel, document PDF professionnel et fichier audio avec narration française.

### Fonctionnalités principales

- **Génération de contenu intelligente** : Utilise l'IA Google Gemini pour créer du contenu pédagogique de qualité
- **Capsules multimédia** : Export simultané en texte, PDF et audio
- **QCM intégrés** : Questions à choix multiples avec mises en situation réalistes
- **Narration audio professionnelle** : Voix off française naturelle via Google Text-to-Speech
- **Mise en page automatisée** : Documents PDF avec mise en forme professionnelle
- **Traitement par lots** : Génération automatique de dizaines de capsules
- **Régénération sélective** : Modification et régénération des contenus après édition manuelle

## Architecture du projet

```
capsules_output/
├── capsule_001_donnees_personnelles/
│   ├── script.txt          # Script textuel éditable
│   ├── capsule.pdf         # Document PDF formaté
│   ├── capsule.mp3         # Fichier audio avec narration
│   └── metadata.json       # Métadonnées de la capsule
├── capsule_002_pseudonymisation/
│   └── [même structure...]
└── summary_report.txt      # Rapport de génération globale
```

## Installation et configuration

### Prérequis système

#### Services cloud requis
- **Compte Google Cloud Platform** avec APIs activées :
  - Google Gemini API (génération de contenu)
  - Cloud Text-to-Speech API (narration audio)

#### Dépendances Python
```bash
# Installation des dépendances Python
pip install -r requirements.txt
```

#### Dépendances système (optionnelles mais recommandées)
```bash
# LaTeX pour génération PDF de qualité professionnelle
# Ubuntu/Debian :
sudo apt-get install texlive-latex-extra

# macOS :
brew install mactex

# Windows : télécharger MiKTeX depuis https://miktex.org/

# FFmpeg pour traitement audio avancé
# Ubuntu/Debian :
sudo apt-get install ffmpeg

# macOS :
brew install ffmpeg

# Windows : télécharger depuis https://ffmpeg.org/download.html
```

### Configuration automatique

Le moyen le plus simple de configurer MedCast Studio est d'utiliser le script de configuration intégré :

```bash
python setup_config.py
```

Ce script interactif vous guide pour :
- Configurer vos identifiants Google Cloud Platform
- Tester la connectivité aux APIs
- Vérifier la disponibilité des dépendances système
- Créer les fichiers de configuration nécessaires

### Configuration manuelle

#### 1. Configuration de l'API Google Gemini

1. Rendez-vous sur [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Créez une nouvelle clé API
3. Ajoutez la clé à votre fichier `.env` ou définissez la variable d'environnement :

```bash
export GOOGLE_API_KEY="votre_cle_api_gemini"
```

#### 2. Configuration des services Google Cloud

1. Créez un nouveau projet sur [Google Cloud Console](https://console.cloud.google.com/)
2. Activez les APIs requises :
   - Cloud Text-to-Speech API
   - Generative AI API (si disponible dans votre région)
3. Créez un Service Account avec les rôles suivants :
   - Cloud Text-to-Speech API User
   - Generative AI User
4. Téléchargez le fichier JSON contenant les clés du Service Account
5. Configurez le chemin vers ce fichier :

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/chemin/vers/votre/service-account-key.json"
```

#### 3. Fichier de configuration .env

Créez un fichier `.env` à la racine du projet :

```env
# Configuration MedCast Studio

# Clé API Google Gemini (obligatoire)
GOOGLE_API_KEY=votre_cle_api_gemini

# Chemin vers les identifiants Google Cloud (obligatoire pour l'audio)
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Niveau de journalisation (optionnel)
LOG_LEVEL=INFO
```

## Préparation du fichier Excel

### Structure requise

Votre fichier Excel doit contenir les colonnes suivantes (les noms exacts sont importants) :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| **Compétences** | Description de la compétence pédagogique visée | "1.2 Caractériser et traiter la donnée à caractère personnel de santé en appliquant la réglementation" |
| **Thématiques** | Catégorie thématique de la capsule | "Données de Santé" |
| **Sujets abordés** | Sujet spécifique traité dans la capsule | "Distinguer donnée à caractère personnel, donnée anonyme et donnée pseudonyme" |
| **Lien 1** à **Lien 4** | URLs de référence avec hyperliens Excel | [Donnée sensible \| CNIL](https://www.cnil.fr/fr/definition/donnee-sensible) |

### Conseils pour optimiser vos sources

- **Utilisez des sources officielles** : Sites gouvernementaux, institutions académiques, organisations professionnelles
- **Variez les types de contenus** : Articles, guides, réglementations, cas d'études
- **Vérifiez l'accessibilité** : Assurez-vous que les URLs sont publiquement accessibles
- **Privilégiez le français** : Pour une cohérence avec la narration audio

## Utilisation

### Génération complète de capsules

Pour traiter un fichier Excel complet et générer toutes les capsules :

```bash
python main.py "votre_fichier.xlsx"
```

### Options de génération

```bash
# Test sur une seule ligne (recommandé pour le premier essai)
python main.py "votre_fichier.xlsx" --single 1

# Spécifier un répertoire de sortie personnalisé
python main.py "votre_fichier.xlsx" --output "mes_capsules_medicales"

# Traitement d'une plage de lignes spécifique
python main.py "votre_fichier.xlsx" --start-row 5 --end-row 10
```

### Régénération après modifications

Une fonctionnalité unique de MedCast Studio est la possibilité de modifier manuellement les scripts générés et de régénérer automatiquement les formats PDF et audio correspondants.

#### Flux de travail de révision

1. **Génération initiale** : Créez vos capsules avec MedCast Studio
2. **Révision manuelle** : Éditez le fichier `script.txt` dans chaque dossier de capsule
3. **Régénération sélective** : Utilisez le script de régénération pour recréer les formats finaux

#### Commandes de régénération

```bash
# Régénérer toutes les capsules (audio + PDF) à partir des scripts modifiés
python regenerate_capsules.py

# Régénérer une capsule spécifique
python regenerate_capsules.py --capsule 001

# Régénérer seulement l'audio (si vous avez seulement modifié la narration)
python regenerate_capsules.py --audio-only

# Régénérer seulement les PDF (si vous avez modifié la structure)
python regenerate_capsules.py --pdf-only

# Combiner les options (par exemple, audio seulement pour la capsule 5)
python regenerate_capsules.py --capsule 5 --audio-only
```

#### Avantages de la régénération

- **Contrôle éditorial complet** : Corrigez les erreurs, ajustez le ton, précisez des concepts
- **Efficacité** : Pas besoin de relancer tout le processus de génération
- **Flexibilité** : Régénérez seulement ce qui a changé (audio ou PDF)
- **Itération rapide** : Testez différentes versions de vos contenus

## Structure des fichiers générés

### 1. Script textuel (`script.txt`)

Le cœur de chaque capsule, structuré comme suit :

```
# [Titre de la capsule]

## Introduction
[Présentation du sujet et des objectifs d'apprentissage]

## Développement
[Contenu principal basé sur les sources référencées]

## Quiz - Questions d'évaluation

### Question 1
[Question à choix multiples avec mise en situation]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

**Réponse correcte : [X]**
**Explication :** [Justification détaillée]

## Conclusion
[Synthèse et points clés à retenir]
```

### 2. Document PDF (`capsule.pdf`)

Document formaté professionnellement incluant :
- **Page de titre** avec métadonnées de la capsule
- **Table des matières** automatique
- **Contenu structuré** avec hiérarchie claire
- **Questions QCM** dans des encadrés visuels
- **Mise en page** adaptée à l'impression et à la lecture numérique

### 3. Fichier audio (`capsule.mp3`)

Narration audio de qualité professionnelle :
- **Durée** : 5 à 10 minutes selon le contenu
- **Voix** : Française masculine naturelle (configurable)
- **Qualité** : 24 kHz, format MP3 optimisé
- **Rythme** : Adapté à l'apprentissage avec pauses appropriées

### 4. Métadonnées (`metadata.json`)

Informations techniques et pédagogiques :

```json
{
  "competence": "Description de la compétence visée",
  "thematique": "Catégorie thématique",
  "sujet": "Sujet spécifique de la capsule",
  "sources": [
    {
      "title": "Titre de la source",
      "url": "https://exemple.com/source"
    }
  ],
  "qcm_count": 3,
  "duration_estimate": "7.5 minutes",
  "generation_date": "2024-01-15T10:30:00",
  "word_count": 1245
}
```

## Personnalisation avancée

### Modification de la voix de narration

Éditez le fichier `audio_generator.py` pour changer les paramètres vocaux :

```python
# Configuration de la voix dans audio_generator.py
self.voice_config = texttospeech.VoiceSelectionParams(
    language_code="fr-FR",
    name="fr-FR-Standard-A",  # Voix féminine
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
)

# Paramètres audio
self.audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=0.8,  # Plus lent pour la compréhension
    pitch=-1.0,         # Ton plus grave
    volume_gain_db=2.0  # Volume plus fort
)
```

### Ajustement de la longueur des capsules

Modifiez les prompts dans `content_generator.py` pour cibler une durée différente :

```python
# Dans content_generator.py, section generate_capsule_content
# Changez la durée cible dans le prompt :
"Durée cible: 10-15 minutes de narration (environ 1500-2000 mots)"
```

### Personnalisation du style PDF

Modifiez les styles LaTeX dans `pdf_generator.py` :

```python
# Dans pdf_generator.py, méthode _create_latex_content
# Personnalisez les couleurs, polices, mise en page, etc.
```

## Qualité et standards pédagogiques

### Niveau de contenu
- **Public cible** : Étudiants en médecine, professionnels de santé
- **Niveau académique** : Licence à Master
- **Approche pédagogique** : Apprentissage par problèmes et cas concrets

### Standards des QCM
- **Nombre par capsule** : 2 à 4 questions
- **Format** : Mises en situation professionnelles réalistes
- **Options de réponse** : 4 choix (A, B, C, D)
- **Feedback pédagogique** : Explications détaillées pour chaque réponse

### Assurance qualité
- **Sources multiples** : Croisement automatique des références
- **Vérification factuelle** : Basé sur des sources officielles
- **Cohérence pédagogique** : Structure uniforme entre toutes les capsules

## Performances et limitations

### Temps de traitement estimés
- **1 capsule** : 2 à 5 minutes
- **10 capsules** : 20 à 45 minutes  
- **50 capsules** : 2 à 4 heures
- **Variables d'impact** : Longueur des sources, charge des APIs, connectivité réseau

### Limitations techniques
- **API Gemini** : 32 000 tokens par requête
- **Text-to-Speech** : 5 000 caractères par appel (division automatique)
- **Extraction web** : Timeout de 30 secondes par URL
- **Formats supportés** : Excel (.xlsx), sources web HTML/PDF

### Modes de fonctionnement dégradé

MedCast Studio s'adapte automatiquement aux services disponibles :

#### Sans LaTeX
- **Fallback automatique** vers la bibliothèque ReportLab
- **Qualité réduite** mais fonctionnelle pour les PDF
- **Alternative ultime** : génération de fichiers texte formatés

#### Sans Text-to-Speech
- **Fichiers placeholder** créés avec instructions
- **Scripts textuels** disponibles pour lecture manuelle
- **Recommandations** d'outils alternatifs de synthèse vocale

#### Sans connectivité web
- **Mode hors ligne** avec contenu basé sur les titres uniquement
- **Avertissements** dans les logs et rapports
- **Suggestions** de sources alternatives

## Résolution des problèmes courants

### Erreurs d'authentification

**Problème** : `ERROR: Could not automatically determine credentials`
**Solutions** :
1. Vérifiez le chemin dans `GOOGLE_APPLICATION_CREDENTIALS`
2. Exécutez `gcloud auth application-default login`
3. Relancez `python setup_config.py` pour re-configurer

### Erreurs de génération PDF

**Problème** : `LaTeX Error: File not found`
**Solutions** :
1. Installez LaTeX complet : `sudo apt-get install texlive-full`
2. Vérifiez que `pdflatex` est dans votre PATH
3. Le système basculera automatiquement sur ReportLab si nécessaire

### Problèmes d'extraction web

**Problème** : `URLError: SSL certificate verify failed`
**Solutions** :
1. Vérifiez votre connectivité internet
2. Testez les URLs manuellement dans un navigateur
3. Supprimez les URLs problématiques du fichier Excel

### Dépassement de quota

**Problème** : `Quota exceeded for requests`
**Solutions** :
1. Attendez la réinitialisation du quota (généralement quotidien)
2. Augmentez vos quotas dans Google Cloud Console
3. Utilisez l'option `--single` pour tester avant traitement complet

### Problèmes de performance

**Problème** : Traitement très lent ou timeouts
**Solutions** :
1. Réduisez le nombre de sources par capsule
2. Vérifiez votre connectivité réseau
3. Exécutez le traitement par petits lots avec `--start-row` et `--end-row`

## Diagnostic et journalisation

### Fichiers de logs

Tous les événements sont enregistrés dans :
- `capsules_generation.log` : Log principal de génération
- `regenerate_capsules.log` : Log des régénérations
- Rotation automatique des fichiers volumineux

### Mode diagnostic

```bash
# Mode verbose pour plus de détails
python main.py "fichier.xlsx" --verbose

# Test de configuration
python setup_config.py

# Test unitaire d'un composant
python content_generator.py --test
```

## Évolutions et feuille de route

### Améliorations prévues
- Support multilingue (anglais, espagnol)
- Interface web intuitive avec Streamlit
- Templates de capsules personnalisables par discipline
- Intégration directe avec plateformes LMS (Moodle, Canvas)
- Analytics d'apprentissage et statistiques d'usage

### Contributions

MedCast Studio est un projet ouvert aux contributions de la communauté médicale et éducative.

**Pour contribuer** :
1. Forkez le repository
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos modifications (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request avec description détaillée

**Types de contributions recherchées** :
- Nouveaux templates pédagogiques
- Support de formats additionnels (PowerPoint, Markdown)
- Améliorations de l'interface utilisateur
- Optimisations de performance
- Tests automatisés
- Documentation et exemples

## Support et assistance

### Ressources d'aide

1. **Logs détaillés** : Consultez `capsules_generation.log` pour diagnostic
2. **Mode test** : Utilisez `--single 1` pour isoler les problèmes
3. **Configuration** : Relancez `python setup_config.py` en cas de doute
4. **Documentation API** : Consultez la documentation Google Cloud

### Contact et communauté

- **Issues GitHub** : Rapportez bugs et demandes de fonctionnalités
- **Discussions** : Participez aux échanges communautaires
- **Wiki** : Consultez les guides avancés et FAQ

### Licence et conditions d'utilisation

MedCast Studio est distribué sous licence ouverte pour usage éducatif et de recherche en santé publique. L'utilisation commerciale nécessite une licence spécifique.

---

**MedCast Studio** - Transformez vos connaissances en capsules d'apprentissage multimédia de qualité professionnelle.

*Version 1.0 - Développé pour la formation médicale et la santé publique*