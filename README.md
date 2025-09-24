# Sacred Scripts (It's kinda a stupid name, I know)

<p align="center">
    <img src="./logo.png"/> <br/>
    Automating the mundane, one script at a time.
</p>

<p align="center">
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="Python">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity">
    <img src="https://img.shields.io/badge/Maintained%3F-yes-green.svg" alt="Maintenance">
  </a>
  <a href="http://makeapullrequest.com">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
  </a>
</p>


A collection of useful Python scripts for automation, file conversion, and everyday development tasks. From audio processing to system utilities, these scripts aim to solve common problems with simple, well-documented solutions.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/ayoub3bidi/sacred-scripts.git
cd sacred-scripts

# Setup environment
make setup
make install

# Convert audio files
python convert/wav_to_mp3.py audio.wav
python convert/sound_to_video.py audio.mp3
```

## Project Structure

```
sacred-scripts/
├── convert/          # Audio, video, and file conversion tools
├── automation/       # System automation and utilities
├── utilities/        # General-purpose helper scripts
├── docs/            # Documentation and examples
└── Makefile         # Build and development commands
```

## Features

### Audio/Video Processing
- WAV to MP3 conversion with quality control
- Audio visualization video generator
- Batch audio format converter
- Video thumbnail generator
- GIF creator from video clips

### File Management
- Bulk file organizer by type/date
- Duplicate file finder and cleaner
- Directory synchronizer
- Batch file renamer with regex patterns
- Broken symlink detector

### System Utilities
- Resource monitor with alerts
- Log file rotator and cleaner
- Disk space analyzer with visualization
- Startup time optimizer
- Process manager by memory usage

### Development Tools
- Code formatter for multiple languages
- License header injector
- Git commit message generator
- Dead code detector
- Dependency vulnerability scanner

## Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Dependencies
```bash
# Install all requirements
make install

# Or manually:
pip install -r convert/requirements.txt
pip install -r automation/requirements.txt
pip install -r utilities/requirements.txt
```

## Usage Examples

### Audio Conversion
```bash
# Convert single WAV file
python convert/wav_to_mp3.py input.wav

# Create audio visualization
python convert/sound_to_video.py music.mp3
```

### Batch Operations
```bash
# Convert all WAV files in directory
python utilities/batch_converter.py --format mp3 *.wav

# Organize downloads folder
python automation/file_organizer.py ~/Downloads
```

## Development

### Available Make Commands
```bash
make help      # Show all available commands
make setup     # Create virtual environment
make install   # Install dependencies
make test      # Run tests and validation
make lint      # Code quality checks
make clean     # Remove temporary files
make package   # Create distribution
```

## Library Usage (Coming Soon)

```python
from sacred_scripts import AudioConverter, FileManager

# Programmatic API
converter = AudioConverter()
converter.batch_convert('*.wav', format='mp3', quality='high')

# File operations
fm = FileManager()
fm.organize_directory('~/Downloads', by='type')
```

## TODO List

### Audio/Video Processing
- [x] WAV to MP3 converter
- [x] Audio visualization generator
- [ ] Batch audio format converter (MP3, WAV, OGG, FLAC)
- [ ] Video thumbnail generator
- [ ] GIF creator from video clips
- [ ] Batch watermark applicator
- [ ] Metadata extractor/editor for media files
- [ ] Image batch resizer/converter

### File Management
- [ ] Duplicate finder with hash comparison
- [ ] Bulk file renamer with regex patterns
- [ ] Directory synchronizer
- [ ] File organizer by date/type/size
- [ ] Broken symlink detector

### System Utilities
- [ ] System resource monitor with alerts
- [ ] Process killer by memory usage
- [ ] Startup time optimizer
- [ ] Disk space analyzer with visualization
- [ ] Log file rotator/cleaner

### Development Tools
- [ ] Code formatter for multiple languages
- [ ] License header injector
- [ ] Git commit message generator
- [ ] Dependency vulnerability scanner
- [ ] Dead code detector

### Network/Web
- [ ] Website availability checker
- [ ] Bulk URL shortener
- [ ] QR code generator for URLs/text
- [ ] Local network scanner
- [ ] WiFi password manager

### Text Processing
- [ ] CSV to JSON/XML converter
- [ ] Text file merger with delimiters
- [ ] Word frequency analyzer
- [ ] Markdown to HTML converter
- [ ] Email extractor from text files

### Automation
- [ ] Desktop screenshot scheduler
- [ ] Database backup automator
- [ ] Email sender with templates
- [ ] Calendar event creator from CSV
- [ ] Password generator with policies

### Data/Analysis
- [ ] Excel report generator
- [ ] JSON prettifier/minifier
- [ ] Configuration file merger
- [ ] Environment variable manager
- [ ] API response validator
