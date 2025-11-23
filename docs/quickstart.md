# Quick Start Guide

This guide will help you get started with Swiss Knife in just a few minutes.

## Installation

```bash
pip install swiss-knife-py[all]
```

## Command Line Usage

### Find Duplicate Files

```bash
# Find duplicates in your Documents folder
sk-duplicates ~/Documents

# Use SHA256 for better accuracy
sk-duplicates ~/Documents --algorithm sha256

# Only check files larger than 1MB
sk-duplicates ~/Documents --min-size 1MB

# Dry run to see what would be found
sk-duplicates ~/Documents --dry-run
```

### Generate Secure Passwords

```bash
# Generate a 16-character password
sk-password --length 16

# Include symbols and exclude ambiguous characters
sk-password --length 20 --symbols --exclude-ambiguous

# Generate multiple passwords
sk-password --count 5
```

## Python API Usage

### File Management

```python
from swiss_knife.file_management import find_duplicates, bulk_rename

# Find duplicate files
duplicates = find_duplicates(["/path/to/search"], algorithm="sha256")
for group in duplicates:
    print(f"Duplicates found: {group}")

# Bulk rename files
renamed_count = bulk_rename(
    pattern=r"IMG_(\d+)",
    replacement=r"photo_\1", 
    directory="/path/to/images",
    dry_run=True  # Test first
)
print(f"Would rename {renamed_count} files")
```

### Text Processing

```python
from swiss_knife.text_processing import convert_csv

# Convert CSV to JSON
convert_csv(
    input_file="data.csv",
    output_format="json",
    output_path="data.json",
    pretty=True
)
```

### Password Generation

```python
from swiss_knife.automation import generate_password, analyze_password_strength

# Generate secure password
password = generate_password(length=16, include_symbols=True)
print(f"Generated: {password}")

# Analyze password strength
strength = analyze_password_strength(password)
print(f"Strength: {strength['score']}/100")
```

## Common Use Cases

### 1. Clean Up Duplicate Files

```bash
# Find and review duplicates
sk-duplicates ~/Downloads --dry-run

# Remove duplicates (keeping one copy)
sk-duplicates ~/Downloads --remove-duplicates
```

### 2. Organize Photos

```python
from swiss_knife.file_management import bulk_rename

# Rename IMG_001.jpg to Photo_001.jpg
bulk_rename(
    pattern=r"IMG_(\d+)",
    replacement=r"Photo_\1",
    directory="~/Pictures",
    extensions=[".jpg", ".jpeg", ".png"]
)
```

### 3. Process Data Files

```python
from swiss_knife.text_processing import convert_csv, merge_text_files

# Convert CSV to JSON
convert_csv("sales_data.csv", "json", "sales_data.json")

# Merge multiple log files
merge_text_files(
    input_files=["log1.txt", "log2.txt", "log3.txt"],
    output_file="combined_logs.txt",
    delimiter="\n---\n"
)
```

## Next Steps

- Read the [CLI Reference](cli-reference.md) for all available commands
- Explore the [Python API](api-reference.md) for programmatic usage
- Check out [examples](https://github.com/ayoub3bidi/swiss-knife/tree/main/examples) in the repository
- Join the [community discussions](https://github.com/ayoub3bidi/swiss-knife/discussions)

## Getting Help

If you encounter any issues:

1. Check the [troubleshooting section](installation.md#troubleshooting)
2. Search [existing issues](https://github.com/ayoub3bidi/swiss-knife/issues)
3. Create a [new issue](https://github.com/ayoub3bidi/swiss-knife/issues/new) if needed
