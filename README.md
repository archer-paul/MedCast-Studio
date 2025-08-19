# MedCast Studio

**[Français](README_FR.md) | English**

**MedCast Studio** is an automated learning capsule generator for medical training and public health education. It transforms your educational content into complete multimedia capsules including text, PDF, and audio with voice-over narration.

## Overview

MedCast Studio analyzes your Excel files containing learning topics and reference sources, then automatically generates structured educational capsules with integrated MCQs. Each capsule is available in three formats: text script, professional PDF document, and audio file with French narration.

### Key Features

- **Intelligent content generation**: Uses Google Gemini AI to create quality educational content
- **Multimedia capsules**: Simultaneous export to text, PDF, and audio formats
- **Integrated MCQs**: Multiple choice questions with realistic scenarios
- **Professional audio narration**: Natural French voice-over via Google Text-to-Speech
- **Automated layout**: PDF documents with professional formatting
- **Batch processing**: Automatic generation of dozens of capsules
- **Selective regeneration**: Modify and regenerate content after manual editing

## Project Architecture

```
capsules_output/
├── capsule_001_personal_data/
│   ├── script.txt          # Editable text script
│   ├── capsule.pdf         # Formatted PDF document
│   ├── capsule.mp3         # Audio file with narration
│   └── metadata.json       # Capsule metadata
├── capsule_002_pseudonymization/
│   └── [same structure...]
└── summary_report.txt      # Global generation report
```

## Installation and Configuration

### System Requirements

#### Required cloud services
- **Google Cloud Platform account** with activated APIs:
  - Google Gemini API (content generation)
  - Cloud Text-to-Speech API (audio narration)

#### Python dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt
```

#### System dependencies (optional but recommended)
```bash
# LaTeX for professional quality PDF generation
# Ubuntu/Debian:
sudo apt-get install texlive-latex-extra

# macOS:
brew install mactex

# Windows: download MiKTeX from https://miktex.org/

# FFmpeg for advanced audio processing
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Windows: download from https://ffmpeg.org/download.html
```

### Automatic Configuration

The easiest way to configure MedCast Studio is using the integrated configuration script:

```bash
python setup_config.py
```

This interactive script guides you through:
- Configuring your Google Cloud Platform credentials
- Testing API connectivity
- Checking system dependencies availability
- Creating necessary configuration files

### Manual Configuration

#### 1. Google Gemini API Configuration

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add the key to your `.env` file or set the environment variable:

```bash
export GOOGLE_API_KEY="your_gemini_api_key"
```

#### 2. Google Cloud Services Configuration

1. Create a new project on [Google Cloud Console](https://console.cloud.google.com/)
2. Enable required APIs:
   - Cloud Text-to-Speech API
   - Generative AI API (if available in your region)
3. Create a Service Account with the following roles:
   - Cloud Text-to-Speech API User
   - Generative AI User
4. Download the JSON file containing the Service Account keys
5. Configure the path to this file:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

#### 3. .env Configuration File

Create a `.env` file at the project root:

```env
# MedCast Studio Configuration

# Google Gemini API Key (required)
GOOGLE_API_KEY=your_gemini_api_key

# Path to Google Cloud credentials (required for audio)
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Logging level (optional)
LOG_LEVEL=INFO
```

## Excel File Preparation

### Required Structure

Your Excel file must contain the following columns (exact names are important):

| Column | Description | Example |
|---------|-------------|---------|
| **Compétences** | Description of the targeted pedagogical skill | "1.2 Characterize and process personal health data by applying regulations" |
| **Thématiques** | Thematic category of the capsule | "Health Data" |
| **Sujets abordés** | Specific topic covered in the capsule | "Distinguish personal data, anonymous data and pseudonymous data" |
| **Lien 1** to **Lien 4** | Reference URLs with Excel hyperlinks | [Sensitive Data \| CNIL](https://www.cnil.fr/fr/definition/donnee-sensible) |

### Tips for Optimizing Your Sources

- **Use official sources**: Government sites, academic institutions, professional organizations
- **Vary content types**: Articles, guides, regulations, case studies
- **Check accessibility**: Ensure URLs are publicly accessible
- **Prefer French**: For consistency with audio narration

## Usage

### Complete Capsule Generation

To process a complete Excel file and generate all capsules:

```bash
python main.py "your_file.xlsx"
```

### Generation Options

```bash
# Test on a single row (recommended for first try)
python main.py "your_file.xlsx" --single 1

# Specify a custom output directory
python main.py "your_file.xlsx" --output "my_medical_capsules"

# Process a specific range of rows
python main.py "your_file.xlsx" --start-row 5 --end-row 10
```

### Regeneration After Modifications

A unique feature of MedCast Studio is the ability to manually modify generated scripts and automatically regenerate corresponding PDF and audio formats.

#### Revision Workflow

1. **Initial generation**: Create your capsules with MedCast Studio
2. **Manual revision**: Edit the `script.txt` file in each capsule folder
3. **Selective regeneration**: Use the regeneration script to recreate final formats

#### Regeneration Commands

```bash
# Regenerate all capsules (audio + PDF) from modified scripts
python regenerate_capsules.py

# Regenerate a specific capsule
python regenerate_capsules.py --capsule 001

# Regenerate only audio (if you only modified narration)
python regenerate_capsules.py --audio-only

# Regenerate only PDFs (if you modified structure)
python regenerate_capsules.py --pdf-only

# Combine options (e.g., audio only for capsule 5)
python regenerate_capsules.py --capsule 5 --audio-only
```

#### Regeneration Benefits

- **Complete editorial control**: Fix errors, adjust tone, clarify concepts
- **Efficiency**: No need to restart the entire generation process
- **Flexibility**: Regenerate only what has changed (audio or PDF)
- **Rapid iteration**: Test different versions of your content

## Generated File Structure

### 1. Text Script (`script.txt`)

The core of each capsule, structured as follows:

```
# [Capsule Title]

## Introduction
[Subject presentation and learning objectives]

## Development
[Main content based on referenced sources]

## Quiz - Assessment Questions

### Question 1
[Multiple choice question with scenario]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

**Correct Answer: [X]**
**Explanation:** [Detailed justification]

## Conclusion
[Summary and key takeaways]
```

### 2. PDF Document (`capsule.pdf`)

Professionally formatted document including:
- **Title page** with capsule metadata
- **Automatic table of contents**
- **Structured content** with clear hierarchy
- **MCQ questions** in visual boxes
- **Layout** adapted for printing and digital reading

### 3. Audio File (`capsule.mp3`)

Professional quality audio narration:
- **Duration**: 5 to 10 minutes depending on content
- **Voice**: Natural French male voice (configurable)
- **Quality**: 24 kHz, optimized MP3 format
- **Pace**: Adapted for learning with appropriate pauses

### 4. Metadata (`metadata.json`)

Technical and pedagogical information:

```json
{
  "competence": "Description of targeted skill",
  "thematique": "Thematic category",
  "sujet": "Specific capsule topic",
  "sources": [
    {
      "title": "Source title",
      "url": "https://example.com/source"
    }
  ],
  "qcm_count": 3,
  "duration_estimate": "7.5 minutes",
  "generation_date": "2024-01-15T10:30:00",
  "word_count": 1245
}
```

## Advanced Customization

### Modifying Narration Voice

Edit the `audio_generator.py` file to change voice parameters:

```python
# Voice configuration in audio_generator.py
self.voice_config = texttospeech.VoiceSelectionParams(
    language_code="fr-FR",
    name="fr-FR-Standard-A",  # Female voice
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
)

# Audio parameters
self.audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=0.8,  # Slower for comprehension
    pitch=-1.0,         # Lower tone
    volume_gain_db=2.0  # Louder volume
)
```

### Adjusting Capsule Length

Modify prompts in `content_generator.py` to target a different duration:

```python
# In content_generator.py, generate_capsule_content section
# Change target duration in the prompt:
"Target duration: 10-15 minutes of narration (approximately 1500-2000 words)"
```

### PDF Style Customization

Modify LaTeX styles in `pdf_generator.py`:

```python
# In pdf_generator.py, _create_latex_content method
# Customize colors, fonts, layout, etc.
```

## Quality and Educational Standards

### Content Level
- **Target audience**: Medical students, health professionals
- **Academic level**: Bachelor's to Master's
- **Pedagogical approach**: Problem-based learning and concrete cases

### MCQ Standards
- **Number per capsule**: 2 to 4 questions
- **Format**: Realistic professional scenarios
- **Answer options**: 4 choices (A, B, C, D)
- **Pedagogical feedback**: Detailed explanations for each answer

### Quality Assurance
- **Multiple sources**: Automatic cross-referencing
- **Fact checking**: Based on official sources
- **Pedagogical consistency**: Uniform structure across all capsules

## Performance and Limitations

### Estimated Processing Times
- **1 capsule**: 2 to 5 minutes
- **10 capsules**: 20 to 45 minutes
- **50 capsules**: 2 to 4 hours
- **Impact variables**: Source length, API load, network connectivity

### Technical Limitations
- **Gemini API**: 32,000 tokens per request
- **Text-to-Speech**: 5,000 characters per call (automatic division)
- **Web extraction**: 30-second timeout per URL
- **Supported formats**: Excel (.xlsx), HTML/PDF web sources

### Degraded Operation Modes

MedCast Studio automatically adapts to available services:

#### Without LaTeX
- **Automatic fallback** to ReportLab library
- **Reduced quality** but functional PDFs
- **Ultimate alternative**: Generation of formatted text files

#### Without Text-to-Speech
- **Placeholder files** created with instructions
- **Text scripts** available for manual reading
- **Recommendations** for alternative speech synthesis tools

#### Without Web Connectivity
- **Offline mode** with content based on titles only
- **Warnings** in logs and reports
- **Suggestions** for alternative sources

## Common Troubleshooting

### Authentication Errors

**Problem**: `ERROR: Could not automatically determine credentials`
**Solutions**:
1. Check the path in `GOOGLE_APPLICATION_CREDENTIALS`
2. Run `gcloud auth application-default login`
3. Restart `python setup_config.py` to reconfigure

### PDF Generation Errors

**Problem**: `LaTeX Error: File not found`
**Solutions**:
1. Install complete LaTeX: `sudo apt-get install texlive-full`
2. Check that `pdflatex` is in your PATH
3. The system will automatically fall back to ReportLab if necessary

### Web Extraction Issues

**Problem**: `URLError: SSL certificate verify failed`
**Solutions**:
1. Check your internet connectivity
2. Test URLs manually in a browser
3. Remove problematic URLs from Excel file

### Quota Exceeded

**Problem**: `Quota exceeded for requests`
**Solutions**:
1. Wait for quota reset (usually daily)
2. Increase your quotas in Google Cloud Console
3. Use `--single` option to test before full processing

### Performance Issues

**Problem**: Very slow processing or timeouts
**Solutions**:
1. Reduce number of sources per capsule
2. Check your network connectivity
3. Run processing in small batches with `--start-row` and `--end-row`

## Diagnostics and Logging

### Log Files

All events are recorded in:
- `capsules_generation.log`: Main generation log
- `regenerate_capsules.log`: Regeneration log
- Automatic rotation of large files

### Diagnostic Mode

```bash
# Verbose mode for more details
python main.py "file.xlsx" --verbose

# Configuration test
python setup_config.py

# Unit test of a component
python content_generator.py --test
```

## Evolution and Roadmap

### Planned Improvements
- Multilingual support (English, Spanish)
- Intuitive web interface with Streamlit
- Customizable capsule templates by discipline
- Direct integration with LMS platforms (Moodle, Canvas)
- Learning analytics and usage statistics

### Contributions

MedCast Studio is a project open to contributions from the medical and educational community.

**To contribute**:
1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request with detailed description

**Types of contributions sought**:
- New pedagogical templates
- Support for additional formats (PowerPoint, Markdown)
- User interface improvements
- Performance optimizations
- Automated tests
- Documentation and examples

## Support and Assistance

### Help Resources

1. **Detailed logs**: Check `capsules_generation.log` for diagnostics
2. **Test mode**: Use `--single 1` to isolate problems
3. **Configuration**: Restart `python setup_config.py` if in doubt
4. **API documentation**: Consult Google Cloud documentation

### Contact and Community

- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Participate in community exchanges
- **Wiki**: Consult advanced guides and FAQ

### License and Terms of Use

MedCast Studio is distributed under open license for educational and research use in public health. Commercial use requires a specific license.

---

**MedCast Studio** - Transform your knowledge into professional-quality multimedia learning capsules.

*Version 1.0 - Developed for medical training and public health*