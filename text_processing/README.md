# Text Processing Tools

Collection of utilities for text file manipulation, conversion, and analysis.

## Available Scripts

### 📊 CSV to JSON/XML Converter (`csv_converter.py`)
Convert CSV files to JSON or XML format with intelligent type inference and flexible formatting options.

**Features:**
- Multi-format output (JSON, XML)
- Automatic type inference (numbers, booleans)
- Custom delimiters (comma, tab, pipe, etc.)
- Header normalization (spaces → underscores, lowercase)
- Empty row/field handling
- Whitespace trimming
- Multiple encoding support
- Progress tracking
- Compression statistics

## Installation

```bash
# Install dependencies
pip install -r text_processing/requirements.txt
```

## Quick Start

### CSV to JSON
```bash
# Basic conversion
python text_processing/csv_converter.py data.csv -f json

# Custom output path
python text_processing/csv_converter.py data.csv -f json -o output.json

# Compact JSON (no pretty-printing)
python text_processing/csv_converter.py data.csv -f json --no-pretty
```

### CSV to XML
```bash
# Basic XML conversion
python text_processing/csv_converter.py data.csv -f xml

# Custom XML tags
python text_processing/csv_converter.py data.csv -f xml --root-tag data --row-tag record
```

## Usage Examples

### CSV Converter

#### Basic Conversions
```bash
# Convert to JSON with default settings
python csv_converter.py sales_data.csv -f json

# Convert to XML
python csv_converter.py contacts.csv -f xml -o contacts.xml

# Tab-separated values (TSV)
python csv_converter.py data.tsv -f json -d $'\t'

# Pipe-delimited
python csv_converter.py data.txt -f json -d '|'
```

#### JSON Formatting
```bash
# Compact JSON (single line)
python csv_converter.py data.csv -f json --no-pretty

# Custom indentation
python csv_converter.py data.csv -f json --indent 4

# Sort keys alphabetically
python csv_converter.py data.csv -f json --sort-keys
```

#### XML Formatting
```bash
# Default XML tags (root, row)
python csv_converter.py data.csv -f xml

# Custom root and row tags
python csv_converter.py users.csv -f xml --root-tag users --row-tag user

# Business data with meaningful tags
python csv_converter.py products.csv -f xml --root-tag catalog --row-tag product
```

#### Advanced Options
```bash
# Keep all values as strings (no type conversion)
python csv_converter.py data.csv -f json --no-infer-types

# Skip empty rows (default)
python csv_converter.py data.csv -f json

# Remove empty fields from output
python csv_converter.py data.csv -f json --skip-empty-fields

# Handle different encodings
python csv_converter.py latin1_data.csv -f json --encoding latin-1
```

### Real-World Scenarios

#### E-commerce Data Export
```bash
# Convert product catalog to JSON for API
python csv_converter.py products.csv -f json -o api/products.json --sort-keys

# Generate XML feed for partners
python csv_converter.py inventory.csv -f xml --root-tag inventory --row-tag item
```

#### Data Analysis Workflow
```bash
# Convert Excel export (CSV) to JSON for analysis
python csv_converter.py sales_report.csv -f json --indent 4

# Handle large datasets efficiently
python csv_converter.py large_dataset.csv -f json --skip-empty-rows --skip-empty-fields
```

## Technical Details

### Type Inference Algorithm
- **Booleans**: `true/false`, `yes/no`, `y/n`, `1/0` (case-insensitive)
- **Integers**: Numeric strings without decimal points
- **Floats**: Numeric strings with decimals or scientific notation
- **Strings**: Everything else

### Header Normalization
1. Strip leading/trailing whitespace
2. Remove special characters (keep alphanumeric, dash, underscore)
3. Replace spaces/hyphens with underscores
4. Convert to lowercase
5. Prefix with `field_` if starts with digit

### Output Formats

**JSON Structure:**
```json
[
  {
    "id": 1,
    "name": "Product A",
    "price": 29.99,
    "active": true
  }
]
```

**XML Structure:**
```xml
<?xml version="1.0" ?>
<root>
  <row>
    <id type="integer">1</id>
    <name>Product A</name>
    <price type="float">29.99</price>
    <active type="boolean">true</active>
  </row>
</root>
```

## Performance

- Small files (< 1MB): < 1 second
- Medium files (1-100MB): 1-30 seconds
- Large files (100MB-1GB): 30 seconds - 5 minutes

## Troubleshooting

### Encoding Issues
```bash
# If you see garbled characters, try different encoding
python csv_converter.py data.csv -f json --encoding latin-1
python csv_converter.py data.csv -f json --encoding utf-16
```

### Type Conversion Problems
- Numbers treated as strings: Ensure no leading zeros or spaces
- Booleans not recognized: Use standard values (true/false, yes/no, 1/0)

### Large Files
- Use `--no-pretty` for faster processing
- Use `--skip-empty-rows --skip-empty-fields` to reduce size

## Coming Soon
- CSV to YAML converter
- CSV validation and cleanup
- Column filtering and transformation
- Multiple file batch processing
