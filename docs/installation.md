# Installation Guide

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Basic Installation

Install Swiss Knife using pip:

```bash
pip install swiss-knife-py
```

## Installation with Optional Dependencies

Swiss Knife supports optional dependencies that can be installed as needed:

### XML Safety
For XML hardening during CSV-to-XML conversion:
```bash
pip install swiss-knife-py[xml]
```

### All Features
To install all optional dependencies:
```bash
pip install swiss-knife-py[all]
```

## Development Installation

For development and contributing:

```bash
# Clone the repository
git clone https://github.com/ayoub3bidi/swiss-knife.git
cd swiss-knife

# Install in development mode with all dependencies
pip install -e .[dev,all]
```

## Verification

Verify your installation by running:

```bash
# Check package version and list installed tools
sk --version
sk --help

# Check a tool CLI
sk-duplicates --help

# Test Python import
python -c "import swiss_knife; print('Swiss Knife installed successfully!')"
python -c "import swiss_knife; print(swiss_knife.__version__)"
```

## Troubleshooting

### Permission Issues
If you encounter permission errors, try installing with the `--user` flag:
```bash
pip install --user swiss-knife-py
```

### Virtual Environment (Recommended)
For isolated installations, use a virtual environment:
```bash
python -m venv swiss-knife-env
source swiss-knife-env/bin/activate  # On Windows: swiss-knife-env\Scripts\activate
pip install swiss-knife-py[all]
```

### Command name collision
The `sk` command is a short name that may conflict with other tools on your system. If `which sk` does not point to Swiss Knife, check the version with `sk-duplicates --version` or `pip show swiss-knife-py` instead.

### Upgrade
To upgrade to the latest version:
```bash
pip install --upgrade swiss-knife-py
```
