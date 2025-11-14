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
