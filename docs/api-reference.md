# Python API Reference

Swiss Knife provides a comprehensive Python API for automation tasks.

## Core Module

### swiss_knife.core

Core utilities and safety functions used throughout the package.

```python
from swiss_knife.core import validate_path, safe_file_operation
```

## File Management

### swiss_knife.file_management

Tools for file operations, duplicate detection, and bulk renaming.

#### find_duplicates()

Find duplicate files using cryptographic hashes.

```python
from swiss_knife.file_management import find_duplicates

duplicates = find_duplicates(
    directories=["/path/to/search"],
    algorithm="sha256",
    min_size=1024,  # bytes
    max_size=None,
    extensions=[".jpg", ".png"],
    exclude_extensions=None
)
```

**Parameters:**
- `directories` (list): Directories to search
- `algorithm` (str): Hash algorithm (md5, sha1, sha256, sha512)
- `min_size` (int): Minimum file size in bytes
- `max_size` (int): Maximum file size in bytes
- `extensions` (list): File extensions to include
- `exclude_extensions` (list): File extensions to exclude

**Returns:** List of duplicate groups

#### bulk_rename()

Rename files in bulk using regex patterns.

```python
from swiss_knife.file_management import bulk_rename

count = bulk_rename(
    pattern=r"IMG_(\d+)",
    replacement=r"Photo_\1",
    directory="/path/to/files",
    extensions=[".jpg"],
    recursive=False,
    dry_run=True
)
```

**Parameters:**
- `pattern` (str): Regex pattern to match
- `replacement` (str): Replacement pattern
- `directory` (str): Directory to process
- `extensions` (list): File extensions to include
- `recursive` (bool): Process subdirectories
- `dry_run` (bool): Preview changes without executing

**Returns:** Number of files renamed

## Text Processing

### swiss_knife.text_processing

Tools for text manipulation and format conversion.

#### convert_csv()

Convert CSV files to different formats.

```python
from swiss_knife.text_processing import convert_csv

convert_csv(
    input_file="data.csv",
    output_format="json",
    output_path="data.json",
    delimiter=",",
    encoding="utf-8",
    has_header=True,
    pretty=True
)
```

**Parameters:**
- `input_file` (str): Path to input CSV file
- `output_format` (str): Output format (json, xml, yaml)
- `output_path` (str): Path for output file
- `delimiter` (str): CSV delimiter
- `encoding` (str): File encoding
- `has_header` (bool): Whether CSV has header row
- `pretty` (bool): Pretty-print output

#### merge_text_files()

Merge multiple text files into one.

```python
from swiss_knife.text_processing import merge_text_files

merge_text_files(
    input_files=["file1.txt", "file2.txt"],
    output_file="merged.txt",
    delimiter="\n---\n",
    encoding="utf-8"
)
```

## Automation

### swiss_knife.automation

Security and automation tools including password generation.

#### generate_password()

Generate secure passwords with customizable options.

```python
from swiss_knife.automation import generate_password

password = generate_password(
    length=16,
    include_uppercase=True,
    include_lowercase=True,
    include_digits=True,
    include_symbols=False,
    exclude_ambiguous=True,
    custom_chars=None
)
```

**Parameters:**
- `length` (int): Password length
- `include_uppercase` (bool): Include uppercase letters
- `include_lowercase` (bool): Include lowercase letters
- `include_digits` (bool): Include digits
- `include_symbols` (bool): Include symbols
- `exclude_ambiguous` (bool): Exclude ambiguous characters
- `custom_chars` (str): Custom character set

**Returns:** Generated password string

#### analyze_password_strength()

Analyze password strength and provide feedback.

```python
from swiss_knife.automation import analyze_password_strength

analysis = analyze_password_strength("mypassword123")
print(f"Score: {analysis['score']}/100")
print(f"Feedback: {analysis['feedback']}")
```

**Returns:** Dictionary with score and feedback

## Network & Web

### swiss_knife.network_web

Network utilities and web tools.

#### check_website()

Check website availability and SSL certificate status.

```python
from swiss_knife.network_web import check_website

result = check_website(
    url="https://example.com",
    timeout=10,
    follow_redirects=True,
    ssl_warning_days=30
)
```

#### generate_qr_code()

Generate QR codes for various data types.

```python
from swiss_knife.network_web import generate_qr_code

generate_qr_code(
    data="https://example.com",
    output_path="qr_code.png",
    size=10,
    border=4
)
```

## System Utilities

### swiss_knife.system_utilities

System monitoring and process management tools.

#### monitor_system()

Monitor system resources.

```python
from swiss_knife.system_utilities import monitor_system

stats = monitor_system(
    duration=60,  # seconds
    interval=5,   # seconds
    cpu_threshold=80,
    memory_threshold=90
)
```

#### analyze_disk_usage()

Analyze disk usage by directory.

```python
from swiss_knife.system_utilities import analyze_disk_usage

usage = analyze_disk_usage(
    path="/home/user",
    max_depth=3,
    min_size=1024*1024  # 1MB
)
```

## Error Handling

All functions raise appropriate exceptions for error conditions:

```python
from swiss_knife.exceptions import (
    SwissKnifeError,
    FileOperationError,
    ValidationError
)

try:
    result = find_duplicates(["/invalid/path"])
except FileOperationError as e:
    print(f"File operation failed: {e}")
except ValidationError as e:
    print(f"Invalid input: {e}")
```

## Configuration

### Global Configuration

```python
from swiss_knife import config

# Set global defaults
config.set_default_algorithm("sha256")
config.set_dry_run_mode(True)
config.set_verbose_mode(True)
```

### Context Managers

Use context managers for safe operations:

```python
from swiss_knife.core import safe_operation

with safe_operation():
    # Operations here are automatically validated
    result = find_duplicates(["/path"])
```

## Examples

### Complete File Cleanup Workflow

```python
from swiss_knife.file_management import find_duplicates, bulk_rename
from swiss_knife.system_utilities import analyze_disk_usage

# 1. Analyze disk usage
usage = analyze_disk_usage("/home/user/Downloads")
print(f"Total size: {usage['total_size']} bytes")

# 2. Find duplicates
duplicates = find_duplicates(["/home/user/Downloads"])
print(f"Found {len(duplicates)} duplicate groups")

# 3. Rename files for organization
renamed = bulk_rename(
    pattern=r"download_(\d+)",
    replacement=r"file_\1",
    directory="/home/user/Downloads",
    dry_run=True
)
print(f"Would rename {renamed} files")
```

### Batch Text Processing

```python
from swiss_knife.text_processing import convert_csv, merge_text_files
import glob

# Convert all CSV files to JSON
for csv_file in glob.glob("*.csv"):
    json_file = csv_file.replace(".csv", ".json")
    convert_csv(csv_file, "json", json_file, pretty=True)

# Merge all log files
log_files = glob.glob("*.log")
merge_text_files(log_files, "combined.log", delimiter="\n---\n")
```
