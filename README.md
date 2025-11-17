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

A comprehensive collection of Python automation scripts for audio processing, file management, text processing, system utilities, and network monitoring. From batch audio conversion to intelligent duplicate detection, these scripts solve common problems with simple, well-documented solutions.

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
python convert/batch_audio_converter.py --format mp3 *.wav

# File Management
python file_management/duplicate_finder.py ~/Documents
python file_management/bulk_renamer.py "\s+" "_" ~/Documents

# Text Processing
python text_processing/csv_converter.py data.csv -f json
python text_processing/markdown_converter.py README.md
python text_processing/text_merger.py *.txt -o merged.txt

# Network/Web
python network_web/website_checker.py https://example.com
python network_web/website_checker.py --file urls.txt --export-json report.json
python network_web/qr_generator.py --url https://example.com -o qr.png
python network_web/qr_generator.py --wifi --ssid MyNet --password pass123 -o wifi.png
python network_web/network_scanner.py --network 192.168.1.0/24 --quick
```

## Project Structure
```
sacred-scripts/
├── convert/              # Audio, video, and image conversion tools
├── file_management/      # File organization and cleanup utilities
├── text_processing/      # Text file conversion and manipulation
├── system_utilities/     # System monitoring and management
├── network_web/          # Network and web monitoring tools
├── automation/           # System automation scripts  
├── utilities/            # General-purpose helper scripts
├── docs/                 # Documentation and examples
└── Makefile             # Build and development commands
```

## Features

### 🎵 Audio/Video Processing
- **Batch Audio Converter**: Multi-format conversion (MP3, WAV, OGG, FLAC) with quality presets and parallel processing
- **WAV to MP3 conversion**: Simple single-file conversion with quality control
- **Audio visualization generator**: Create animated waveform videos from any audio format
- **Batch Image Converter**: Multi-format image conversion and resizing (JPEG, PNG, WebP, HEIC)

### 📁 File Management
- **Duplicate File Finder**: Advanced duplicate detection using cryptographic hash comparison (MD5, SHA1, SHA256, SHA512)
  - Size-based filtering and file extension targeting
  - Safe deletion with multiple keep strategies
  - JSON/text export for reporting
- **Bulk File Renamer**: Regex-based pattern matching with advanced features
  - Sequential numbering and custom placeholders
  - Collision detection and prevention
  - Interactive mode and dry-run support
- **Broken Symlink Detector**: Find and manage broken symbolic links
  - Circular reference detection
  - Safe deletion with trash support

### 📝 Text Processing
- **CSV to JSON/XML Converter**: Convert CSV files with intelligent type inference
  - Automatic type conversion (numbers, booleans)
  - Custom delimiters (comma, tab, pipe, etc.)
  - Header normalization and empty field handling
  - Multiple encoding support
- **Markdown to HTML Converter**: Convert Markdown to styled HTML
  - Multiple themes (GitHub, Monokai, Dracula, Solarized)
  - Syntax highlighting with Pygments
  - Table of contents generation
  - Batch directory conversion
- **Text File Merger**: Merge multiple text files with delimiters
  - Multiple delimiter presets and custom delimiters
  - File headers with timestamps and statistics
  - Flexible sorting (by name, size, date, extension)
  - Content processing (line numbers, whitespace handling)
  - Preview mode for testing
- **Word Frequency Analyzer**: Analyze word frequency with advanced filtering
  - Smart tokenization and stop words removal
  - Context extraction and pattern matching
  - Per-file breakdown for multi-file analysis
  - JSON/CSV export with statistics

### ⚙️ System Utilities
- **System Resource Monitor**: Real-time monitoring with configurable alerts
  - CPU, memory, disk, and network tracking
  - Alert thresholds with cooldown periods
  - Historical trending and statistics
- **Process Killer**: Terminate processes by resource usage
  - Memory/CPU threshold-based termination
  - Protected system processes
  - Dry-run mode for safety
- **Disk Space Analyzer**: Analyze directory sizes with visualization
  - Extension breakdown and largest files
  - Subdirectory analysis
  - JSON export for reporting

### 🌐 Network/Web Tools
- **Website Availability Checker**: Monitor website health and SSL certificates
  - HTTP/HTTPS availability checking
  - Response time measurement
  - SSL certificate expiration monitoring
  - Redirect tracking and custom headers
  - JSON/CSV export for reporting
- **QR Code Generator**: Create QR codes for multiple data types
  - URL, WiFi, vCard, Email, SMS, Phone, Geolocation
  - 6 visual styles with custom colors
  - Text labels and batch generation
  - High-resolution output
- **Local Network Scanner**: Discover devices and open ports
  - Network range and single host scanning
  - Service detection and banner grabbing
  - Hostname and MAC address resolution
  - Concurrent multi-threaded scanning
  - JSON/CSV export

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
pip install -r text_processing/requirements.txt
pip install -r system_utilities/requirements.txt
pip install -r network_web/requirements.txt
```

## Usage Examples

### Audio Conversion
```bash
# Convert single WAV file
python convert/wav_to_mp3.py input.wav

# Batch convert with quality control
python convert/batch_audio_converter.py --format mp3 --quality high *.wav

# Convert entire directory with parallel processing
python convert/batch_audio_converter.py --format flac --workers 8 ~/Music/
```

### File Management
```bash
# Find all duplicates in a directory
python file_management/duplicate_finder.py ~/Documents

# Find large duplicate files only
python file_management/duplicate_finder.py ~/Videos --min-size 10MB

# Delete duplicates keeping shortest filenames
python file_management/duplicate_finder.py ~/temp --delete-duplicates --keep-strategy shortest_name

# Bulk rename files
python file_management/bulk_renamer.py "\s+" "_" ~/Documents

# Find broken symlinks
python file_management/broken_symlinks.py ~/Projects
```

### Text Processing
```bash
# Convert CSV to JSON
python text_processing/csv_converter.py data.csv -f json

# Convert CSV to XML with custom tags
python text_processing/csv_converter.py data.csv -f xml --root-tag data --row-tag record

# Convert Markdown to HTML
python text_processing/markdown_converter.py README.md --theme github

# Merge text files
python text_processing/text_merger.py *.txt -o merged.txt

# Merge logs with timestamps
python text_processing/text_merger.py logs/*.log -o combined.log --timestamp --stats

# Word frequency analysis
python text_processing/word_frequency.py document.txt --remove-stop-words --top 30
```

### System Utilities
```bash
# Monitor system resources
python system_utilities/system_monitor.py

# Quick status check
python system_utilities/system_monitor.py --once --show-processes

# Kill memory-intensive processes (dry run)
python system_utilities/process_killer.py --min-memory 1024 --dry-run

# Analyze disk space
python system_utilities/disk_analyzer.py ~/Documents
```

### Network/Web Tools
```bash
# Check single website
python network_web/website_checker.py https://example.com

# Check multiple websites
python network_web/website_checker.py https://google.com https://github.com --verbose

# Monitor sites from file
python network_web/website_checker.py --file urls.txt --export-json report.json

# SSL certificate monitoring
python network_web/website_checker.py https://example.com --ssl-warning-days 30

# QR code for URL
python network_web/qr_generator.py --url https://example.com -o qr.png

# WiFi QR code
python network_web/qr_generator.py --wifi --ssid MyNetwork --password pass123 -o wifi.png

# Contact card
python network_web/qr_generator.py --vcard --name "John Doe" --vcard-phone "+1234567890" -o contact.png

# Batch QR generation
python network_web/qr_generator.py --batch urls.txt --output-dir qr_codes/

# Network scanning
python network_web/network_scanner.py --network 192.168.1.0/24 --quick
python network_web/network_scanner.py --host 192.168.1.1 --port-range 1 1024
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
make validate-text  # Check text processing dependencies
make validate-network # Check network/web dependencies
make lint           # Code quality checks
make clean          # Remove temporary files
make package        # Create distribution

# Demo commands
make demo           # Show all available tools
make convert-demo   # Audio conversion examples
make files-demo     # File management examples
make text-demo      # Text processing examples
make system-demo    # System utilities examples
make network-demo   # Network/web examples
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
- Collision detection for renames
- Protected system processes
- SSL certificate verification

## TODO List

### Audio/Video Processing
- [x] WAV to MP3 converter
- [x] Audio visualization generator  
- [x] Batch audio format converter (MP3, WAV, OGG, FLAC)
- [x] Batch image converter and resizer

### File Management
- [x] Duplicate finder with hash comparison
- [x] Bulk file renamer with regex patterns
- [x] Broken symlink detector

### System Utilities
- [x] System resource monitor with alerts
- [x] Process killer by memory usage
- [x] Disk space analyzer with visualization

### Text Processing
- [x] CSV to JSON/XML converter
- [x] Markdown to HTML converter
- [x] Text file merger with delimiters
- [x] Word frequency analyzer

### Network/Web
- [x] Website availability checker
- [x] QR code generator for URLs/text
- [x] Local network scanner

### Development Tools
- [x] Code formatter for multiple languages
- [x] License header injector
- [x] Dead code detector

### Automation
- [x] Desktop screenshot scheduler
- [x] Database backup automator
- [x] Password generator with policies

### Data/Analysis
- [x] JSON prettifier/minifier
- [x] Configuration file merger
- [x] Environment variable manager
- [x] Excel report generator
- [ ] API response validator

## Library Usage (Coming Soon)
```python
from sacred_scripts import AudioConverter, DuplicateFinder, CSVConverter, WebsiteChecker

# Audio processing
converter = AudioConverter()
converter.batch_convert('*.wav', format='mp3', quality='high')

# Duplicate detection
finder = DuplicateFinder(hash_algorithm='sha256', min_size='10MB')
duplicates = finder.find_duplicates(['/path/to/search'])

# CSV conversion
csv_conv = CSVConverter()
data = csv_conv.read_csv('data.csv')
json_output = csv_conv.to_json(data, pretty=True)

# Website monitoring
checker = WebsiteChecker(timeout=10, check_ssl_expiry=True)
results = checker.check_urls(['https://example.com'])
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author
**Ayoub Abidi** - [ayoub3bidi](https://github.com/ayoub3bidi)
