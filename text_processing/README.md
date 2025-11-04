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

### 📝 Markdown to HTML Converter (`markdown_converter.py`)
Convert Markdown files to styled HTML with syntax highlighting, themes, and table of contents.

**Features:**
- Multiple HTML templates (minimal, styled)
- Syntax highlighting with multiple themes (GitHub, Monokai, Dracula, Solarized)
- Automatic table of contents generation
- Table support
- YAML frontmatter metadata parsing
- Code block line numbers
- Custom page titles
- Batch directory conversion
- Responsive design

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

### Markdown to HTML
```bash
# Basic conversion with styled template
python text_processing/markdown_converter.py README.md

# Minimal template (no styling)
python text_processing/markdown_converter.py doc.md --template minimal -o doc.html

# Different syntax highlighting theme
python text_processing/markdown_converter.py code.md --theme monokai

# Convert entire directory
python text_processing/markdown_converter.py docs/ -o html/ --recursive
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

### Markdown Converter

#### Basic Conversions
```bash
# Convert with default styled template
python markdown_converter.py README.md

# Custom output path
python markdown_converter.py docs.md -o documentation.html

# Minimal template (no CSS styling)
python markdown_converter.py notes.md --template minimal
```

#### Syntax Highlighting Themes
```bash
# GitHub theme (default)
python markdown_converter.py code.md --theme github

# Dark themes
python markdown_converter.py tutorial.md --theme monokai
python markdown_converter.py guide.md --theme dracula
python markdown_converter.py docs.md --theme solarized-dark

# Light themes
python markdown_converter.py article.md --theme default
python markdown_converter.py blog.md --theme solarized-light
```

#### Table of Contents & Features
```bash
# Disable table of contents
python markdown_converter.py doc.md --no-toc

# Add line numbers to code blocks
python markdown_converter.py tutorial.md --line-numbers

# Custom page title
python markdown_converter.py post.md --title "My Blog Post"

# Add generation timestamp footer
python markdown_converter.py article.md --footer

# Combine options
python markdown_converter.py guide.md --theme monokai --line-numbers --footer
```

#### Batch Conversion
```bash
# Convert all markdown in directory
python markdown_converter.py docs/ -o html/

# Recursive conversion (subdirectories)
python markdown_converter.py project/ -o output/ --recursive

# Blog/documentation site generation
python markdown_converter.py blog/posts/ -o blog/html/ --recursive --theme github --footer
```

#### Advanced Usage
```bash
# Disable specific features
python markdown_converter.py simple.md --no-tables --no-highlight

# Technical documentation
python markdown_converter.py api_docs.md --line-numbers --theme monokai -o docs/api.html

# Blog post with metadata
python markdown_converter.py post.md --theme github --footer --title "Blog Post Title"
```

### Real-World Scenarios

#### Documentation Generation
```bash
# Convert project README
python markdown_converter.py README.md -o docs/index.html --theme github

# Generate API documentation
python markdown_converter.py api/ -o docs/api/ --recursive --line-numbers

# Technical guides with TOC
python markdown_converter.py guides/ -o website/guides/ --recursive --theme monokai
```

#### Blog/Static Site
```bash
# Convert blog posts
python markdown_converter.py posts/ -o public/ --recursive --footer

# With custom theme
python markdown_converter.py articles/ -o site/articles/ --recursive --theme dracula --footer
```

#### Code Tutorials
```bash
# Python tutorial with line numbers
python markdown_converter.py python_tutorial.md --line-numbers --theme monokai

# Multi-language docs
python markdown_converter.py tutorials/ -o docs/ --recursive --line-numbers --theme github
```

### CSV to Markdown Workflow
```bash
# First convert data
python csv_converter.py data.csv -f json

# Then create markdown report and convert to HTML
echo "# Data Report\n\nData processed successfully." > report.md
python markdown_converter.py report.md --theme github --footer
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

### CSV Converter Implementation
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
- JSON/YAML to Markdown converter
- Text file merger with delimiters
- Word frequency analyzer
- Email extractor from text files
