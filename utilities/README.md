# Utilities

General-purpose helper scripts for data manipulation and common tasks.

## Available Scripts

### 📋 JSON Formatter (`json_formatter.py`)
Format, validate, minify, and manipulate JSON files with comprehensive error handling.

**Features:**
- Prettify with custom indentation
- Minify (remove whitespace)
- Sort keys alphabetically
- Validate JSON syntax
- Merge multiple JSON files
- Batch directory processing
- Backup support
- Size statistics

**Usage:**
```bash
# Prettify JSON
python json_formatter.py data.json

# Minify JSON
python json_formatter.py data.json --minify

# Custom indentation
python json_formatter.py data.json --indent 4

# Sort keys
python json_formatter.py data.json --sort-keys

# Save to different file
python json_formatter.py input.json -o output.json

# Format directory recursively
python json_formatter.py data/ -r

# Validate only
python json_formatter.py data.json --validate-only

# Merge files
python json_formatter.py file1.json file2.json --merge -o merged.json

# Create backup
python json_formatter.py data.json --backup
```

**No Dependencies:** Pure Python stdlib.

### ⚙️ Configuration File Merger (`config_merger.py`)
Merge and manage configuration files across environments with support for JSON, YAML, TOML, INI, and ENV formats.

**Features:**
- Multi-format support (JSON, YAML, TOML, INI, ENV)
- Three merge strategies (override, deep merge, append)
- Cross-format conversion
- Configuration diff tool
- Conflict detection

**Usage:**
```bash
# Basic merge
python config_merger.py base.json dev.json -o config.json

# Multi-environment
python config_merger.py base.json common.json prod.json -o final.json

# Deep merge
python config_merger.py base.yaml override.yaml -o merged.yaml --strategy merge

# Show differences
python config_merger.py config1.json config2.json --diff

# Convert format
python config_merger.py config.json -o config.yaml

# Cross-format merge
python config_merger.py base.yaml override.toml -o final.json
```

**Merge Strategies:**
- `override`: Simple key replacement
- `merge`: Deep merge nested structures
- `append`: Append to lists instead of replacing
