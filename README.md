# Swiss Knife

<p align="center">
    <img src="https://raw.githubusercontent.com/ayoub3bidi/swiss-knife/main/logo.png" alt="Swiss Knife Logo" width="100"/> <br/>
    A Python automation toolkit for file management, text processing, and security utilities.
</p>

**Swiss Knife** is a Python package that provides essential automation tools with a focus on safety, security, and ease of use.

## Features

### File Management
- **Duplicate Detection**: Find and remove duplicate files using cryptographic hashes (MD5, SHA1, SHA256, SHA512)
- **Bulk Renaming**: Rename files in bulk using regex patterns with safety checks and dry-run mode

### Text Processing  
- **CSV Conversion**: Convert CSV files to JSON/XML with intelligent type inference and validation

### Security & Automation
- **Password Generation**: Generate secure passwords with customizable policies and strength analysis

## Quick Start

### Installation

```bash
# Basic installation
pip install swiss-knife-py

# With XML processing support (recommended for security)
pip install swiss-knife-py[xml]

# With development tools
pip install swiss-knife-py[dev]
```

### Command Line Usage

```bash
# Find duplicate files
sk-duplicates ~/Documents --algorithm sha256 --min-size 1MB

# Convert CSV to JSON
sk-csv data.csv --format json --output data.json --pretty

# Generate secure password
sk-password --length 16 --exclude-ambiguous

# Bulk rename files
sk-rename 'IMG_(\d+)' 'photo_\1' ~/Pictures --dry-run
```

### Python API Usage

```python
from swiss_knife.file_management.duplicate_finder import find_duplicates
from swiss_knife.file_management.bulk_renamer import bulk_rename
from swiss_knife.text_processing.csv_converter import convert_csv
from swiss_knife.automation.password_generator import generate_password

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
