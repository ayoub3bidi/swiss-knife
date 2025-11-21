# CLI Reference

Swiss Knife provides several command-line tools for common automation tasks.

## sk-duplicates

Find and manage duplicate files using cryptographic hashes.

### Usage

```bash
sk-duplicates [OPTIONS] DIRECTORIES...
```

### Options

- `--algorithm, -a`: Hash algorithm to use (md5, sha1, sha256, sha512)
- `--min-size`: Minimum file size to check (e.g., 1MB, 500KB)
- `--max-size`: Maximum file size to check
- `--extensions`: File extensions to include (e.g., .jpg,.png,.pdf)
- `--exclude-extensions`: File extensions to exclude
- `--dry-run`: Show what would be done without making changes
- `--remove-duplicates`: Remove duplicate files (keeps one copy)
- `--interactive`: Prompt before removing each duplicate
- `--output, -o`: Save results to file (JSON format)
- `--verbose, -v`: Verbose output
- `--help`: Show help message

### Examples

```bash
# Basic duplicate detection
sk-duplicates ~/Documents

# Use SHA256 for better accuracy
sk-duplicates ~/Documents --algorithm sha256

# Only check image files larger than 1MB
sk-duplicates ~/Pictures --extensions .jpg,.jpeg,.png --min-size 1MB

# Remove duplicates interactively
sk-duplicates ~/Downloads --remove-duplicates --interactive

# Save results to file
sk-duplicates ~/Documents --output duplicates_report.json
```

## sk-password

Generate secure passwords with customizable options.

### Usage

```bash
sk-password [OPTIONS]
```

### Options

- `--length, -l`: Password length (default: 12)
- `--count, -c`: Number of passwords to generate (default: 1)
- `--uppercase`: Include uppercase letters (default: true)
- `--lowercase`: Include lowercase letters (default: true)
- `--digits`: Include digits (default: true)
- `--symbols`: Include symbols
- `--exclude-ambiguous`: Exclude ambiguous characters (0, O, l, 1, etc.)
- `--custom-chars`: Use custom character set
- `--no-similar`: Exclude similar-looking characters
- `--analyze`: Show password strength analysis
- `--output, -o`: Save passwords to file
- `--help`: Show help message

### Examples

```bash
# Generate a 16-character password
sk-password --length 16

# Generate 5 passwords with symbols
sk-password --count 5 --symbols

# Generate password excluding ambiguous characters
sk-password --length 20 --symbols --exclude-ambiguous

# Analyze password strength
sk-password --length 16 --analyze

# Save passwords to file
sk-password --count 10 --output passwords.txt
```

## sk-csv

Convert CSV files to different formats.

### Usage

```bash
sk-csv [OPTIONS] INPUT_FILE
```

### Options

- `--format, -f`: Output format (json, xml, yaml)
- `--output, -o`: Output file path
- `--pretty`: Pretty-print output
- `--delimiter`: CSV delimiter (default: comma)
- `--encoding`: File encoding (default: utf-8)
- `--no-header`: CSV has no header row
- `--help`: Show help message

### Examples

```bash
# Convert CSV to JSON
sk-csv data.csv --format json --output data.json

# Convert with pretty formatting
sk-csv data.csv --format json --pretty

# Convert CSV with semicolon delimiter
sk-csv data.csv --format xml --delimiter ";"
```

## sk-rename

Bulk rename files using regex patterns.

### Usage

```bash
sk-rename [OPTIONS] PATTERN REPLACEMENT DIRECTORY
```

### Options

- `--extensions`: File extensions to include
- `--recursive, -r`: Process subdirectories
- `--dry-run`: Show what would be renamed
- `--case-sensitive`: Case-sensitive pattern matching
- `--backup`: Create backup of original names
- `--verbose, -v`: Verbose output
- `--help`: Show help message

### Examples

```bash
# Rename IMG_001.jpg to Photo_001.jpg
sk-rename "IMG_(\d+)" "Photo_\1" ~/Pictures --extensions .jpg

# Dry run to preview changes
sk-rename "old_name" "new_name" ~/Documents --dry-run

# Recursive rename with backup
sk-rename "pattern" "replacement" ~/Files --recursive --backup
```

## sk-monitor

Monitor system resources and processes.

### Usage

```bash
sk-monitor [OPTIONS]
```

### Options

- `--cpu-threshold`: CPU usage threshold for alerts (%)
- `--memory-threshold`: Memory usage threshold for alerts (%)
- `--disk-threshold`: Disk usage threshold for alerts (%)
- `--interval`: Monitoring interval in seconds (default: 5)
- `--duration`: Monitoring duration in seconds
- `--output, -o`: Save monitoring data to file
- `--format`: Output format (json, csv)
- `--help`: Show help message

### Examples

```bash
# Monitor with default settings
sk-monitor

# Monitor with custom thresholds
sk-monitor --cpu-threshold 80 --memory-threshold 90

# Monitor for 1 hour and save to file
sk-monitor --duration 3600 --output system_stats.json
```

## sk-check

Check website availability and SSL certificates.

### Usage

```bash
sk-check [OPTIONS] URLS...
```

### Options

- `--timeout`: Request timeout in seconds (default: 10)
- `--ssl-warning-days`: Days before SSL expiry to warn (default: 30)
- `--follow-redirects`: Follow HTTP redirects
- `--output, -o`: Save results to file
- `--format`: Output format (json, csv)
- `--verbose, -v`: Verbose output
- `--help`: Show help message

### Examples

```bash
# Check single website
sk-check https://example.com

# Check multiple websites
sk-check https://site1.com https://site2.com

# Check with SSL certificate monitoring
sk-check https://example.com --ssl-warning-days 7

# Save results to file
sk-check https://example.com --output health_check.json
```

## Global Options

All commands support these global options:

- `--version`: Show version information
- `--help`: Show help message
- `--config`: Use custom configuration file
- `--quiet, -q`: Suppress non-error output
- `--debug`: Enable debug output

## Configuration Files

Swiss Knife supports configuration files in YAML format:

```yaml
# ~/.swiss-knife/config.yml
defaults:
  algorithm: sha256
  dry_run: false
  verbose: true

duplicates:
  min_size: 1MB
  extensions: [.jpg, .png, .pdf]

passwords:
  length: 16
  symbols: true
  exclude_ambiguous: true
```

Use with: `sk-duplicates --config ~/.swiss-knife/config.yml`
