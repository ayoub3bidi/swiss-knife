# CLI Reference

These are the CLI tools installed by `pip install swiss-knife-py`.
For additional standalone scripts (network scanner, system monitor, etc.) see the repository's `network_web/` and `system_utilities/` directories.

## sk

Package umbrella command. Use it to check the installed version and list available tools.

### Usage

```bash
sk [-h] [-V]
```

### Options

- `-V`, `--version`: Print the installed package version and exit (`swiss-knife X.Y.Z`)
- `-h`, `--help`: Show installed tools and usage examples

Running `sk` with no arguments prints the same help as `sk --help`.

Tool-specific work is done via the `sk-*` commands listed below—not via `sk` subcommands.

### Examples

```bash
sk --version
sk --help
sk
```

## Global options

Every packaged CLI (including `sk` and each `sk-*` tool) supports:

- `-V`, `--version`: Print the installed package version and exit
- `-h`, `--help`: Show command help

## sk-duplicates

Find and optionally delete duplicate files using cryptographic hashes.

### Usage

```bash
sk-duplicates [OPTIONS] PATHS...
```

### Options

- `--algorithm`: Hash algorithm to use (`md5`, `sha1`, `sha256`, `sha512`; default: `sha256`)
- `--min-size`: Minimum file size in bytes (default: `0`)
- `--delete-duplicates`: Delete duplicate files, keeping one file per duplicate group
- `--keep-strategy`: File to keep (`first`, `last`, `shortest_name`, `longest_name`; default: `first`)
- `--export-json`: Export duplicate groups to a JSON file
- `--yes`: Skip confirmation prompts for deletion
- `--help`: Show help message

### Examples

```bash
sk-duplicates ~/Documents
sk-duplicates ~/Documents --algorithm md5
sk-duplicates ~/Downloads --min-size 1024
sk-duplicates ~/Downloads --delete-duplicates --keep-strategy shortest_name --yes
sk-duplicates ~/Documents --export-json duplicates_report.json
```

## sk-password

Generate secure passwords or check password strength.

### Usage

```bash
sk-password [OPTIONS]
```

### Options

- `--length`, `-l`: Password length (default: `12`)
- `--count`, `-c`: Number of passwords to generate (default: `1`)
- `--no-uppercase`: Exclude uppercase letters
- `--no-lowercase`: Exclude lowercase letters
- `--no-digits`: Exclude digits
- `--no-symbols`: Exclude symbols
- `--exclude-ambiguous`: Exclude `0`, `O`, `1`, `l`, and `I`
- `--min-uppercase`: Minimum uppercase letters (default: `1`)
- `--min-lowercase`: Minimum lowercase letters (default: `1`)
- `--min-digits`: Minimum digits (default: `1`)
- `--min-symbols`: Minimum symbols (default: `0`)
- `--check`: Check strength of the supplied password instead of generating one
- `--help`: Show help message

### Examples

```bash
sk-password
sk-password --length 20
sk-password --count 5 --length 10
sk-password --length 30 --exclude-ambiguous
sk-password --check "MyStr0ng!P@ssw0rd2024"
```

## sk-csv

Convert CSV files to JSON or XML.

### Usage

```bash
sk-csv [OPTIONS] INPUT
```

### Options

- `--format`: Output format (`json` or `xml`; default: `json`)
- `--output`, `-o`: Output file path; defaults to the input file with the new extension
- `--delimiter`: CSV delimiter character (default: comma)
- `--no-infer-types`: Keep all CSV values as strings
- `--pretty`: Pretty-print JSON output (default)
- `--no-pretty`: Disable pretty-printing for JSON
- `--root-tag`: XML root element tag name (default: `data`)
- `--row-tag`: XML row element tag name (default: `row`)
- `--max-size-mb`: Maximum file size to process in MB (default: `100`)
- `--help`: Show help message

### Examples

```bash
sk-csv data.csv --format json --output data.json
sk-csv data.csv --format xml --output data.xml
sk-csv data.csv --format json --delimiter ";"
sk-csv data.csv --format xml --root-tag people --row-tag person
```

## sk-rename

Bulk rename files using regex patterns.

### Usage

```bash
sk-rename [OPTIONS] PATTERN REPLACEMENT [DIRECTORY]
```

### Options

- `--recursive`, `-r`: Process subdirectories recursively
- `--dry-run`, `-n`: Show what would be renamed without making changes
- `--yes`, `-y`: Skip confirmation prompts
- `--help`: Show help message

### Examples

```bash
sk-rename "IMG_(\d+)" "photo_\1" ~/Pictures --dry-run
sk-rename "IMG_(\d+)" "photo_\1" ~/Pictures --yes
sk-rename "IMG_(\d+)" "photo_\1" ~/Pictures --recursive --dry-run
```
