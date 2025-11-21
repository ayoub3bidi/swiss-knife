# Swiss Knife

<p align="center">
    <img src="./logo.png" alt="Swiss Knife Logo" width="100"/> <br/>
    A comprehensive collection of Python automation tools.
</p>

**Swiss Knife** is a production-ready Python package that provides a comprehensive collection of automation tools for file management, text processing, system utilities, network operations, and more.

## Features

### File Management
- **Duplicate Detection**: Find and remove duplicate files using cryptographic hashes
- **Bulk Renaming**: Rename files in bulk using regex patterns with safety checks
- **Broken Symlinks**: Detect and clean up broken symbolic links

### Text Processing  
- **CSV Conversion**: Convert CSV files to JSON/XML with intelligent type inference
- **Text Merging**: Merge multiple text files with customizable delimiters
- **Word Analysis**: Analyze word frequency with filtering and export options

### Security & Automation
- **Password Generation**: Generate secure passwords with customizable policies
- **Strength Analysis**: Analyze password strength with detailed feedback

### Network & Web
- **Website Monitoring**: Check website availability and SSL certificates
- **Network Scanning**: Discover devices and open ports on local networks
- **QR Code Generation**: Create QR codes for URLs, WiFi, contacts, and more

### System Utilities
- **Resource Monitoring**: Monitor CPU, memory, disk, and network usage
- **Process Management**: Manage processes based on resource usage
- **Disk Analysis**: Analyze directory sizes and file distributions

## Quick Start

### Installation

```bash
# Basic installation
pip install swiss-knife

# With optional dependencies for specific features
pip install swiss-knife[media]     # Image/audio processing
pip install swiss-knife[network]   # Network tools
pip install swiss-knife[system]    # System monitoring
pip install swiss-knife[all]       # Everything
```

### Command Line Usage

```bash
# Find duplicate files
sk-duplicates ~/Documents --algorithm sha256 --min-size 1MB

# Bulk rename files
sk-rename "IMG_(\d+)" "photo_\1" ~/Pictures --dry-run

# Convert CSV to JSON
sk-csv data.csv --format json --pretty

# Generate secure passwords
sk-password --length 16 --symbols --exclude-ambiguous

# Check website availability
sk-check https://example.com --ssl-warning-days 30

# Monitor system resources
sk-monitor --cpu-threshold 80 --memory-threshold 90
```

### Python API Usage

```python
from swiss_knife.file_management import find_duplicates, bulk_rename
from swiss_knife.text_processing import convert_csv
from swiss_knife.automation import generate_password

# Find duplicates
duplicates = find_duplicates(["/path/to/search"], algorithm="sha256")
print(f"Found {len(duplicates)} duplicate groups")

# Convert CSV to JSON
convert_csv("data.csv", "json", output_path="data.json", pretty=True)

# Generate secure password
password = generate_password(length=16, include_symbols=True)
print(f"Generated password: {password}")

# Bulk rename with safety checks
renamed_count = bulk_rename(r"IMG_(\d+)", r"photo_\1", "/path/to/images", dry_run=True)
```

## Security Features

Swiss Knife prioritizes security with multiple safety mechanisms:

- **Safe Defaults**: All destructive operations require explicit confirmation
- **Input Validation**: Comprehensive validation prevents injection attacks
- **Path Safety**: Protection against path traversal vulnerabilities  
- **Memory Limits**: Configurable limits prevent memory exhaustion
- **Dry Run Mode**: Test operations before executing them
- **Cryptographic Security**: Uses `secrets` module for secure randomness

## Development

```bash
# Clone the repository
git clone https://github.com/ayoub3bidi/swiss-knife.git
cd swiss-knife

# Install in development mode
pip install -e .[dev,all]

# Run tests
pytest

# Run linting
ruff check swiss_knife/

# Run security checks
bandit -r swiss_knife/
```
