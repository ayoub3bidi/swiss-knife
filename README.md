# Swiss Knife

<p align="center">
    <img src="https://raw.githubusercontent.com/ayoub3bidi/swiss-knife/main/logo.png" alt="Swiss Knife Logo" width="100"/> <br/>
    A Python package that provides essential automation tools with a focus on safety, security, and ease of use.
</p>

<p align="center">
    <a href="https://pypi.org/project/swiss-knife-py/"><img src="https://img.shields.io/pypi/pyversions/swiss-knife-py.svg" alt="Python versions"></a>
    <a href="https://github.com/ayoub3bidi/swiss-knife/actions/workflows/ci.yml"><img src="https://github.com/ayoub3bidi/swiss-knife/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="https://github.com/ayoub3bidi/swiss-knife/actions/workflows/security.yml"><img src="https://github.com/ayoub3bidi/swiss-knife/actions/workflows/security.yml/badge.svg" alt="Security"></a>
    <a href="https://codecov.io/gh/ayoub3bidi/swiss-knife"><img src="https://codecov.io/gh/ayoub3bidi/swiss-knife/branch/main/graph/badge.svg" alt="codecov"></a>
    <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
</p>

## Features

### File Management
- **Duplicate Detection**: Find and remove duplicate files using cryptographic hashes (MD5, SHA1, SHA256, SHA512)
- **Bulk Renaming**: Rename files in bulk using regex patterns with safety checks and dry-run mode

### Text Processing  
- **CSV Conversion**: Convert CSV files to JSON/XML with intelligent type inference and validation

### Security & Automation
- **Password Generation**: Generate secure passwords with customizable policies and strength analysis

### Utilities
- **Data Helpers**: Parse booleans and environment variables, convert key styles, validate UUIDs and HTTP status codes, and decode base64 text

## Standalone Scripts

This repository also contains standalone scripts in `automation/`, `convert/`, `file_management/`, `network_web/`, `system_utilities/`, `text_processing/`, `utilities/`, and `development_tools/`. These scripts are not installed by `pip install swiss-knife-py`; use the separate requirements files in those directories when running them directly from the repository.

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
from swiss_knife.utilities import get_env_int, convert_keys_to_camel_case

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

# Parse helpers
retry_count = get_env_int("RETRY_COUNT", default=3)
payload = convert_keys_to_camel_case({"first_name": "Alice"})
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
