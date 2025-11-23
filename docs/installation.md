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

Swiss Knife supports optional feature sets that can be installed as needed:

### Media Processing
For image and audio processing capabilities:
```bash
pip install swiss-knife-py[media]
```

### Network Tools
For network scanning and web utilities:
```bash
pip install swiss-knife-py[network]
```

### System Monitoring
For system resource monitoring:
```bash
pip install swiss-knife-py[system]
```

### Text Processing
For advanced text processing features:
```bash
pip install swiss-knife-py[text]
```

### Data Processing
For Excel and YAML processing:
```bash
pip install swiss-knife-py[data]
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
# Check CLI tools
sk-duplicates --help

# Test Python import
python -c "import swiss_knife; print('Swiss Knife installed successfully!')"
```

## Troubleshooting

### Permission Issues
If you encounter permission errors, try installing with the `--user` flag:
```bash
pip install --user swiss-knife
```

### Virtual Environment (Recommended)
For isolated installations, use a virtual environment:
```bash
python -m venv swiss-knife-env
source swiss-knife-env/bin/activate  # On Windows: swiss-knife-env\Scripts\activate
pip install swiss-knife-py[all]
```

### Upgrade
To upgrade to the latest version:
```bash
pip install --upgrade swiss-knife
```
