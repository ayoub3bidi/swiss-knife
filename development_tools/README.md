# Development Tools

Automation tools for code formatting, project management, and development workflows.

## Available Scripts

### 🎨 Multi-Language Code Formatter (`code_formatter.py`)
Format code files using industry-standard formatters for 12+ languages.

**Features:**
- Support for 12+ languages (Python, JavaScript, TypeScript, C++, Java, Go, Rust, etc.)
- Automatic language detection from file extensions
- Check-only mode for CI/CD pipelines
- Recursive directory formatting
- Pattern exclusion (node_modules, .git, etc.)
- Detailed reporting and statistics
- JSON export for automation

**Supported Formatters:**
- Python: Black
- JavaScript/TypeScript: Prettier
- C/C++: clang-format
- Java: google-java-format
- Go: gofmt
- Rust: rustfmt
- HTML/CSS/JSON/YAML/Markdown: Prettier

### 📜 License Header Injector (`license_header_injector.py`)
Inject, update, or remove license headers in source code files across multiple languages.

**Features:**
- 6 built-in license templates (MIT, Apache 2.0, GPL v3, BSD 3-Clause, ISC, Unlicense)
- Custom license template support
- Multi-language comment style support (C/C++, Python, JavaScript, Java, etc.)
- Auto-detection of existing headers
- Update or remove existing headers
- Shebang and encoding declaration preservation
- Dry-run mode for safe testing
- Batch processing with filters
- Comprehensive statistics and reporting

**Supported Languages:**
- C/C++, Java, JavaScript, TypeScript, Go, Rust, Swift, C#, PHP
- Python, Ruby, Shell, Perl, R
- HTML, XML, SVG, Vue
- SQL, Lua, and more

**Usage:**
```bash
# Add MIT license to Python files
python license_header_injector.py -l mit -a "John Doe" src/ --ext py

# Add Apache license recursively
python license_header_injector.py -l apache -a "Acme Corp" . -r

# Update existing headers
python license_header_injector.py -l mit -a "John Doe" -y 2025 src/ --update -r

# Remove all headers
python license_header_injector.py src/ --remove -r

# Dry run preview
python license_header_injector.py -l mit -a "John Doe" src/ --dry-run -r

# Custom template
python license_header_injector.py -l custom --template my_license.txt -a "John Doe" src/
```

**License Templates:**
- `mit`: MIT License (permissive)
- `apache`: Apache License 2.0 (permissive with patent grant)
- `gpl3`: GNU GPL v3.0 (copyleft)
- `bsd3`: BSD 3-Clause License (permissive)
- `isc`: ISC License (very permissive, similar to MIT)
- `unlicense`: The Unlicense (public domain)
- `custom`: Load from custom template file

**Real-World Scenarios:**
```bash
# New open-source project setup
python license_header_injector.py -l mit -a "Your Name" . -r --exclude tests,docs

# Company project standardization
python license_header_injector.py -l apache -a "Company Name" src/ -r --ext py,js,ts,java

# Update copyright year across project
python license_header_injector.py -l mit -a "Your Name" -y 2025 . -r --update

# Remove headers before license change
python license_header_injector.py . --remove -r
python license_header_injector.py -l apache -a "Your Name" . -r
```

**Custom Template Format:**
Create a text file with your license text using placeholders:
- `{year}` - Copyright year
- `{author}` - Copyright holder/author name

Example custom template:
```
Proprietary Software License
Copyright (c) {year} {author}

This software and associated documentation files are proprietary.
Unauthorized copying, distribution, or use is strictly prohibited.
```

### 🔍 Dead Code Detector (`dead_code_detector.py`)
Detect unused functions, classes, variables, and imports in Python projects.

**Features:**
- Unused function/class/variable detection
- Unused import identification
- Confidence scoring (high/medium/low)
- Two-pass analysis (definitions + usages)
- Test file exclusion
- Private member filtering
- Detailed reporting by type and confidence
- JSON/CSV export

**Usage:**
```bash
# Analyze current directory
python dead_code_detector.py .

# High confidence only
python dead_code_detector.py src/ --min-confidence high

# Include test files
python dead_code_detector.py . --include-tests

# Include private members
python dead_code_detector.py src/ --include-private

# Export results
python dead_code_detector.py . --export-json dead_code.json

# Show all results
python dead_code_detector.py src/ --show-all
```

**Confidence Levels:**
- **HIGH**: No references found (very likely dead)
- **MEDIUM**: Very few references (possibly dead)
- **LOW**: Has references (might be used indirectly)

**Real-World Scenarios:**
```bash
# Pre-refactoring cleanup
python dead_code_detector.py . --min-confidence high --export-json cleanup.json

# Find unused imports
python dead_code_detector.py src/ --min-confidence high | grep import

# Full project audit
python dead_code_detector.py . --show-all --export-csv audit.csv

# Exclude tests from analysis
python dead_code_detector.py src/ --include-tests
```

**Limitations:**
- Python only (for now)
- May not detect dynamic usage (getattr, exec, etc.)
- External API calls not tracked
- Decorators may affect detection

**Best Practices:**
- Start with `--min-confidence high`
- Review medium confidence items manually
- Exclude test files initially
- Export results before making changes
- Use version control before deletion

## Installation

```bash
# Install Python dependencies
pip install -r development_tools/requirements.txt

# Install formatters (as needed)
pip install black                    # Python
npm install -g prettier              # JS/TS/HTML/CSS/JSON
rustup component add rustfmt         # Rust
# go install includes gofmt
```

## Quick Start

```bash
# Format single file
python development_tools/code_formatter.py script.py

# Format directory
python development_tools/code_formatter.py src/ --recursive

# Check formatting (CI/CD)
python development_tools/code_formatter.py src/ --check --recursive
```

## Usage Examples

### Basic Formatting

```bash
# Single file
python code_formatter.py app.py

# Multiple files
python code_formatter.py src/main.js src/utils.js src/api.ts

# Entire directory
python code_formatter.py src/

# Recursive
python code_formatter.py . --recursive
```

### Check Mode (CI/CD)

```bash
# Check without modifying
python code_formatter.py src/ --check

# CI/CD integration (exits with error if formatting needed)
python code_formatter.py . --check --recursive

# Pre-commit check
python code_formatter.py $(git diff --name-only --cached) --check
```

### Exclusion Patterns

```bash
# Exclude directories
python code_formatter.py . --recursive --exclude node_modules,dist,build

# Exclude test files
python code_formatter.py src/ --recursive --exclude tests,__tests__

# Complex exclusions
python code_formatter.py . --recursive --exclude "node_modules,dist,build,*.test.js"
```

### Verbose & Reporting

```bash
# Verbose output
python code_formatter.py src/ --verbose

# Export results
python code_formatter.py src/ --export-json format_report.json

# Both
python code_formatter.py . --recursive --verbose --export-json report.json
```

### Real-World Scenarios

**Pre-commit Hook:**
```bash
#!/bin/bash
python development_tools/code_formatter.py $(git diff --name-only --cached) --check
if [ $? -ne 0 ]; then
  echo "Code formatting issues detected. Run formatter before committing."
  exit 1
fi
```

**CI/CD Pipeline:**
```yaml
# .github/workflows/format-check.yml
- name: Check code formatting
  run: python development_tools/code_formatter.py . --check --recursive
```

**Format Changed Files:**
```bash
# Format files changed in last commit
python code_formatter.py $(git diff --name-only HEAD~1)

# Format uncommitted changes
python code_formatter.py $(git diff --name-only)
```

**Project Setup:**
```bash
# Format entire codebase
python code_formatter.py . --recursive --exclude node_modules,venv,dist

# Generate report
python code_formatter.py . --recursive --check --export-json format_status.json
```

### Language-Specific Examples

**Python Project:**
```bash
python code_formatter.py src/ tests/ --recursive
```

**JavaScript/TypeScript:**
```bash
python code_formatter.py src/ --recursive --exclude node_modules
```

**Mixed Project:**
```bash
python code_formatter.py . --recursive \
  --exclude "node_modules,venv,dist,build,target,*.min.js"
```

## Output Examples

**Console Output:**
```
Formatting: 100%|████████████████| 25/25 [00:05<00:00,  4.82file/s]

================================================================================
FORMATTING SUMMARY
================================================================================
Files checked:      25
Files formatted:    18
Files failed:       0
Files skipped:      2

Missing formatters: java, rust
```

**Check Mode Output:**
```
Checking: 100%|██████████████████| 50/50 [00:03<00:00, 15.23file/s]

================================================================================
FORMATTING SUMMARY
================================================================================
Files checked:      50
Files OK:           47
Needs formatting:   3
Files failed:       0
Files skipped:      0
```

## Formatter Installation

```bash
# Python
pip install black

# JavaScript/TypeScript/JSON/HTML/CSS/Markdown
npm install -g prettier

# C/C++
# Ubuntu/Debian
sudo apt-get install clang-format
# macOS
brew install clang-format

# Java
# Download from https://github.com/google/google-java-format/releases

# Go (included with Go)
# No additional installation needed

# Rust
rustup component add rustfmt
```

## Performance

- **Small projects** (< 100 files): < 5 seconds
- **Medium projects** (100-1000 files): 5-30 seconds
- **Large projects** (1000+ files): 30+ seconds

Depends on:
- Number of files
- Formatter speed
- File sizes
- System performance

## Coming Soon
- ✅ Multi-language code formatter (COMPLETED)
- [ ] License header injector
- [ ] Git commit message generator
- [ ] Dependency vulnerability scanner
- [ ] Dead code detector

## Dependencies
- `tqdm`: Progress bars for bulk operations
