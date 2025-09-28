# Sacred Scripts
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

A comprehensive collection of Python automation scripts for audio processing, file management, and everyday development tasks. From batch audio conversion to intelligent duplicate detection, these scripts solve common problems with simple, well-documented solutions.

## Quick Start
```bash
# Clone the repository
git clone https://github.com/ayoub3bidi/sacred-scripts.git
cd sacred-scripts

# Setup environment
make setup
make install

# Audio Processing
python convert/wav_to_mp3.py audio.wav
python convert/sound_to_video.py audio.mp3
python convert/batch_audio_converter.py --format mp3 *.wav

# File Management
python file_management/duplicate_finder.py ~/Documents
python file_management/duplicate_finder.py --min-size 10MB --extensions jpg,png ~/Pictures
```

## Project Structure
```
sacred-scripts/
├── convert/              # Audio, video, and file conversion tools
├── file_management/      # File organization and cleanup utilities
├── automation/           # System automation and utilities  
├── utilities/            # General-purpose helper scripts
├── docs/                 # Documentation and examples
└── Makefile             # Build and development commands
```

## Features

### 🎵 Audio/Video Processing
- **Batch Audio Converter**: Multi-format conversion (MP3, WAV, OGG, FLAC) with quality presets and parallel processing
- **WAV to MP3 conversion**: Simple single-file conversion with quality control
- **Audio visualization generator**: Create animated waveform videos from any audio format
- Video thumbnail generator (coming soon)
- GIF creator from video clips (coming soon)

### 📁 File Management
- **Duplicate File Finder**: Advanced duplicate detection using cryptographic hash comparison (MD5, SHA1, SHA256, SHA512)
  - Size-based filtering and file extension targeting
  - Safe deletion with multiple keep strategies
  - JSON/text export for reporting
  - Dry-run mode for safe testing
- Bulk file organizer by type/date (coming soon)
- Directory synchronizer (coming soon)
- Batch file renamer with regex patterns (coming soon)
- Broken symlink detector (coming soon)

### ⚙️ System Utilities
- Resource monitor with alerts (coming soon)
- Log file rotator and cleaner (coming soon)
- Disk space analyzer with visualization (coming soon)
- Startup time optimizer (coming soon)
- Process manager by memory usage (coming soon)

### 🛠️ Development Tools
- Code formatter for multiple languages (coming soon)
- License header injector (coming soon)
- Git commit message generator (coming soon)
- Dead code detector (coming soon)
- Dependency vulnerability scanner (coming soon)

## Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Dependencies
```bash
# Install all requirements
make install

# Or install specific modules:
pip install -r convert/requirements.txt
pip install -r file_management/requirements.txt
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

# Batch convert with quality control
python convert/batch_audio_converter.py --format mp3 --quality high *.wav

# Convert entire directory with parallel processing
python convert/batch_audio_converter.py --format flac --workers 8 ~/Music/

# Convert with custom output directory
python convert/batch_audio_converter.py --format ogg --output ./converted audio/*.mp3
```

### File Management
```bash
# Find all duplicates in a directory
python file_management/duplicate_finder.py ~/Documents

# Find large duplicate files only
python file_management/duplicate_finder.py ~/Videos --min-size 10MB

# Find duplicate images with specific extensions
python file_management/duplicate_finder.py ~/Pictures --extensions jpg,png,gif,bmp

# Export duplicate report as JSON
python file_management/duplicate_finder.py ~/Downloads --output json --file report.json

# Safely preview duplicate removal
python file_management/duplicate_finder.py ~/temp --delete-duplicates --dry-run

# Delete duplicates keeping shortest filenames
python file_management/duplicate_finder.py ~/temp --delete-duplicates --keep-strategy shortest_name

# Secure duplicate detection with SHA256
python file_management/duplicate_finder.py ~/Important --hash sha256
```

### Advanced Batch Operations
```bash
# High-quality lossless audio conversion
python convert/batch_audio_converter.py --format flac --quality lossless ~/audio/

# Fast low-quality conversion for demos
python convert/batch_audio_converter.py --format mp3 --quality low --overwrite *.wav

# Find and clean large duplicate videos
python file_management/duplicate_finder.py ~/Movies --min-size 500MB --delete-duplicates --dry-run
```

## Development

### Available Make Commands
```bash
make help           # Show all available commands
make setup          # Create virtual environment
make install        # Install dependencies
make test           # Run tests and validation
make validate-audio # Check audio processing dependencies
make validate-files # Check file management dependencies
make lint           # Code quality checks
make clean          # Remove temporary files
make package        # Create distribution

# Demo commands
make demo           # Show all available tools
make convert-demo   # Audio conversion examples
make files-demo     # File management examples
```

## Library Usage (Coming Soon)
```python
from sacred_scripts import AudioConverter, DuplicateFinder, FileManager

# Audio processing
converter = AudioConverter()
converter.batch_convert('*.wav', format='mp3', quality='high')

# Duplicate detection
finder = DuplicateFinder(hash_algorithm='sha256', min_size='10MB')
duplicates = finder.find_duplicates(['/path/to/search'])

# File operations
fm = FileManager()
fm.organize_directory('~/Downloads', by='type')
```

## Performance & Security

### Hash Algorithm Performance
- **MD5**: Fastest, suitable for general duplicate detection
- **SHA1**: Good balance of speed and security
- **SHA256**: Cryptographically secure, recommended for important data
- **SHA512**: Maximum security, slower processing

### Memory Efficiency
- Streaming hash calculation handles files of any size
- Progress tracking for long operations
- Minimal memory footprint (~8MB regardless of file sizes)

### Safety Features
- Dry-run mode for testing operations
- Safe deletion using system trash/recycle bin
- Comprehensive error handling
- Detailed operation logging

## TODO List

### Audio/Video Processing
- [x] WAV to MP3 converter
- [x] Audio visualization generator  
- [x] Batch audio format converter (MP3, WAV, OGG, FLAC)
- [x] Image batch resizer/converter

### File Management
- [x] Duplicate finder with hash comparison
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
