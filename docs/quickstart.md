# Quick Start Guide

This guide covers the installable `swiss_knife` package and its CLI tools.

## Installation

```bash
pip install swiss-knife-py[all]
```

Check the installed version:

```bash
sk --version
```

## Command Line Usage

### Find Duplicate Files

```bash
sk-duplicates ~/Documents
sk-duplicates ~/Documents --algorithm sha256
sk-duplicates ~/Documents --min-size 1024
sk-duplicates ~/Downloads --delete-duplicates --yes
```

### Generate Secure Passwords

```bash
sk-password --length 16
sk-password --length 20 --exclude-ambiguous
sk-password --count 5 --length 10
sk-password --check "MyStr0ng!P@ssw0rd2024"
```

### Convert CSV Files

```bash
sk-csv data.csv --format json --output data.json
sk-csv data.csv --format xml --root-tag people --row-tag person
```

### Rename Files

```bash
sk-rename 'IMG_(\d+)' 'photo_\1' ~/Pictures --dry-run
sk-rename 'IMG_(\d+)' 'photo_\1' ~/Pictures --yes
```

## Python API Usage

### File Management

```python
from swiss_knife.file_management import bulk_rename, find_duplicates

duplicates = find_duplicates(["/path/to/search"], algorithm="sha256")
for file_hash, files in duplicates.items():
    print(file_hash, files)

bulk_rename(
    pattern=r"IMG_(\d+)",
    replacement=r"photo_\1",
    target_dir="/path/to/images",
    dry_run=True,
)
```

### Text Processing

```python
from swiss_knife.text_processing import convert_csv

convert_csv(
    input_path="data.csv",
    output_format="json",
    output_path="data.json",
    pretty=True,
)
```

### Automation

```python
from swiss_knife.automation import PasswordGenerator, generate_password

password = generate_password(length=16, include_symbols=True)
analysis = PasswordGenerator().check_strength(password)
print(analysis["strength"])
```

## Next Steps

- Read the [CLI Reference](cli-reference.md) for command details
- Explore the [Python API](api-reference.md) for programmatic usage
- Check the [Installation Guide](installation.md) for optional dependencies
