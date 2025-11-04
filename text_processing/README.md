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

### 🔗 Text File Merger (`text_merger.py`)
Merge multiple text files with customizable delimiters and advanced formatting options.

**Features:**
- Multiple delimiter presets (line, double, hash, star, dash, blank, minimal, section)
- Custom delimiters support
- File headers with optional timestamps and statistics
- Flexible sorting (by name, size, date, extension)
- Content processing (line numbers, whitespace stripping, empty line removal)
- Glob patterns and recursive directory merging
- Error handling strategies (skip, stop, replace)
- Preview mode for testing

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

### Text File Merger
```bash
# Basic merge
python text_processing/text_merger.py *.txt -o merged.txt

# Merge with timestamps and stats
python text_processing/text_merger.py logs/*.log -o combined.log --timestamp --stats

# Clean merge (no headers, remove empty lines)
python text_processing/text_merger.py *.txt -o clean.txt --no-filename --remove-empty

# Merge sorted by date with line numbers
python text_processing/text_merger.py *.py -o all_code.py --sort date --line-numbers

# Recursive directory merge
python text_processing/text_merger.py src/ tests/ -o all_files.txt -r --ext py,js
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

### Text File Merger

#### Basic Merging
```bash
# Merge all text files in directory
python text_merger.py *.txt -o merged.txt

# Merge specific files
python text_merger.py file1.txt file2.txt file3.txt -o output.txt

# Merge with custom delimiter
python text_merger.py *.log -o combined.log -d "### NEXT FILE ###"
```

#### Delimiter Presets
```bash
# Line delimiter (default)
python text_merger.py *.txt -o output.txt -d line

# Double line delimiter
python text_merger.py *.txt -o output.txt -d double

# Hash delimiter
python text_merger.py *.txt -o output.txt -d hash

# Section delimiter (with extra spacing)
python text_merger.py *.txt -o output.txt -d section

# No delimiter (blank)
python text_merger.py *.txt -o output.txt -d blank
```

#### Headers and Metadata
```bash
# Add file headers with timestamps
python text_merger.py logs/*.log -o combined.log --timestamp

# Add file statistics (lines, size)
python text_merger.py *.txt -o output.txt --stats

# Both timestamp and stats
python text_merger.py *.log -o full_info.log --timestamp --stats

# No file headers (clean merge)
python text_merger.py *.txt -o clean.txt --no-filename
```

#### Sorting Files
```bash
# Sort by name (default)
python text_merger.py *.txt -o output.txt --sort name

# Sort by file size (largest first)
python text_merger.py *.log -o output.log --sort size --reverse

# Sort by modification date (newest first)
python text_merger.py *.txt -o output.txt --sort date --reverse

# Sort by extension
python text_merger.py * -o output.txt --sort extension --ext txt,log,md
```

#### Content Processing
```bash
# Add line numbers to output
python text_merger.py *.py -o all_code.py --line-numbers

# Remove empty lines
python text_merger.py *.txt -o clean.txt --remove-empty

# Strip whitespace from lines
python text_merger.py *.log -o trimmed.log --strip

# Combine all processing
python text_merger.py *.txt -o processed.txt --line-numbers --remove-empty --strip
```

#### Directory and Pattern Merging
```bash
# Merge all files from directory
python text_merger.py logs/ -o combined.log

# Recursive merge from multiple directories
python text_merger.py src/ tests/ -o all_files.txt -r

# Filter by extension
python text_merger.py project/ -o code.txt -r --ext py,js,ts

# Glob patterns
python text_merger.py "**/*.log" -o all_logs.txt

# Multiple patterns
python text_merger.py src/**/*.py tests/**/*.py -o python_files.txt
```

#### Preview Mode
```bash
# Preview merge without writing file
python text_merger.py *.txt -o test.txt --preview

# Preview more lines
python text_merger.py *.log -o test.log --preview --preview-lines 100
```

#### Error Handling
```bash
# Skip files with read errors (default)
python text_merger.py *.txt -o output.txt --on-error skip

# Stop on first error
python text_merger.py *.txt -o output.txt --on-error stop

# Replace unreadable characters
python text_merger.py *.txt -o output.txt --on-error replace

# Different encoding
python text_merger.py *.txt -o output.txt --encoding latin-1
```

### Real-World Scenarios

#### Log File Analysis
```bash
# Merge all logs with timestamps sorted by date
python text_merger.py logs/*.log -o analysis.log --sort date --timestamp --stats

# Combine error logs from multiple servers
python text_merger.py server1/error.log server2/error.log server3/error.log \
  -o all_errors.log --sort date --reverse
```

#### Code Consolidation
```bash
# Merge all Python files for review
python text_merger.py src/**/*.py -o review.py --line-numbers --sort name

# Combine source and tests
python text_merger.py src/ tests/ -o codebase.txt -r --ext py --line-numbers
```

#### Documentation Generation
```bash
# Merge markdown docs in order
python text_merger.py docs/*.md -o full_docs.md --sort name

# Combine READMEs from subprojects
python text_merger.py */README.md -o project_overview.md --timestamp
```

#### Report Consolidation
```bash
# Merge weekly reports
python text_merger.py reports/week*.txt -o monthly_report.txt --sort date

# Combine CSV files (headers removed)
python text_merger.py data/*.csv -o combined.csv --no-filename --remove-empty
```

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

### Text Merger Delimiter Presets
- `line`: 80 dashes (default)
- `double`: 80 equal signs
- `hash`: 80 hash symbols
- `star`: 80 asterisks
- `dash`: 40 dash pairs
- `blank`: No delimiter
- `minimal`: Three dashes
- `section`: Equal signs with extra spacing

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

### CSV Converter
- Small files (< 1MB): < 1 second
- Medium files (1-100MB): 1-30 seconds
- Large files (100MB-1GB): 30 seconds - 5 minutes

### Text Merger
- Small merges (< 100 files): < 1 second
- Medium merges (100-1000 files): 1-10 seconds
- Large merges (1000+ files): 10-60 seconds
- Memory efficient: processes files individually

## Troubleshooting

### Encoding Issues
```bash
# If you see garbled characters, try different encoding
python csv_converter.py data.csv -f json --encoding latin-1
python csv_converter.py data.csv -f json --encoding utf-16

# Text merger with different encoding
python text_merger.py *.txt -o output.txt --encoding latin-1
```

### Type Conversion Problems
- Numbers treated as strings: Ensure no leading zeros or spaces
- Booleans not recognized: Use standard values (true/false, yes/no, 1/0)

### Large Files
- Use `--no-pretty` for faster processing
- Use `--skip-empty-rows --skip-empty-fields` to reduce size
- Text merger processes files individually for memory efficiency

### Merge Errors
```bash
# Skip problematic files
python text_merger.py *.txt -o output.txt --on-error skip

# Replace unreadable characters
python text_merger.py *.txt -o output.txt --on-error replace
```

## Coming Soon
- ✅ Text file merger with delimiters (COMPLETED)
- [ ] Word frequency analyzer
- [ ] Email extractor from text files
- [ ] JSON/YAML to Markdown converter
- [ ] CSV validation and cleanup
- [ ] Column filtering and transformation
- [ ] Multiple file batch processing

## Dependencies
- `tqdm`: Progress bars
- `python-dateutil`: Date/time utilities
- `markdown`: Markdown parsing and conversion
- `Pygments`: Syntax highlighting for code blocks
