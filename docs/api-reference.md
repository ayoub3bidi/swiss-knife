# Python API Reference

Swiss Knife exposes APIs from the installable `swiss_knife` package for file management, CSV conversion, password generation, and utility helpers.

## Core

```python
from swiss_knife.core import (
    SafetyError,
    ValidationError,
    check_file_size_limit,
    confirm_destructive_action,
    safe_filename,
    validate_path,
)
```

`validate_path(path, must_exist=True)` returns a resolved `Path` and raises `ValidationError` when `must_exist` is true and the path is missing.

## File Management

### find_duplicates()

```python
from swiss_knife.file_management import find_duplicates

duplicates = find_duplicates(
    paths=["/path/to/search"],
    algorithm="sha256",
    min_size=1024,
)
```

Parameters:

- `paths`: List of directory or file paths to scan
- `algorithm`: One of `md5`, `sha1`, `sha256`, or `sha512`
- `min_size`: Minimum file size in bytes

Returns a dictionary mapping file hashes to lists of duplicate file paths as strings.

### bulk_rename()

```python
from swiss_knife.file_management import bulk_rename

count = bulk_rename(
    pattern=r"IMG_(\d+)",
    replacement=r"photo_\1",
    target_dir="/path/to/files",
    recursive=False,
    dry_run=True,
)
```

Parameters:

- `pattern`: Regex pattern to match filenames
- `replacement`: Replacement pattern
- `target_dir`: Directory to process
- `recursive`: Whether to process subdirectories
- `dry_run`: Preview changes without renaming files

Returns the number of files renamed. Dry runs return `0`.

## Text Processing

### convert_csv()

```python
from swiss_knife.text_processing import convert_csv

output_path = convert_csv(
    input_path="data.csv",
    output_format="json",
    output_path="data.json",
    delimiter=",",
    infer_types=True,
    pretty=True,
)
```

Parameters:

- `input_path`: Path to an input CSV file
- `output_format`: `json` or `xml`
- `output_path`: Optional output file path
- `delimiter`: CSV delimiter, or `auto` for sniffer-based detection
- `infer_types`: Convert booleans, integers, floats, and empty values
- `pretty`: Pretty-print JSON output
- `root_tag`: XML root tag name
- `row_tag`: XML row tag name

Returns the written output file path.

## Automation

### generate_password()

```python
from swiss_knife.automation import generate_password

password = generate_password(
    length=16,
    include_uppercase=True,
    include_lowercase=True,
    include_digits=True,
    include_symbols=True,
    exclude_ambiguous=True,
)
```

Parameters include `length`, character class toggles, `exclude_ambiguous`, and minimum counts such as `min_uppercase`, `min_lowercase`, `min_digits`, and `min_symbols`.

### PasswordGenerator.check_strength()

```python
from swiss_knife.automation import PasswordGenerator

analysis = PasswordGenerator().check_strength("MyStr0ng!P@ssw0rd2024")
print(analysis["strength"])
print(analysis["score"])
```

Returns a dictionary with score, strength label, character-type booleans, unique character count, and feedback.

## Utilities

```python
from swiss_knife.utilities import (
    convert_keys_to_camel_case,
    decode_base64_text,
    get_env_bool,
    get_env_float,
    get_env_int,
    get_or_default,
    is_http_status_code,
    is_uuid,
    parse_bool,
)
```

`parse_bool(value, default=None)` converts common boolean-like strings such as `yes`, `no`, `1`, and `0`.

`get_env_int`, `get_env_float`, and `get_env_bool` read environment variables and return typed values when parsing succeeds.

`convert_keys_to_camel_case(data)` recursively converts dictionary keys from `snake_case` to `camelCase`.

`decode_base64_text(encoded_data)` decodes UTF-8 base64 content into text.

`is_uuid(value, version=None)` validates UUID strings, and `is_http_status_code(status_code)` checks concrete codes and wildcard classes like `2**`.

## Examples

### File Cleanup Preview

```python
from swiss_knife.file_management import bulk_rename, find_duplicates

duplicates = find_duplicates(["/home/user/Downloads"])
print(f"Found {len(duplicates)} duplicate groups")

renamed = bulk_rename(
    pattern=r"download_(\d+)",
    replacement=r"file_\1",
    target_dir="/home/user/Downloads",
    dry_run=True,
)
print(f"Would rename {renamed} files")
```

### CSV Conversion

```python
from swiss_knife.text_processing import convert_csv

convert_csv("sales_data.csv", "json", "sales_data.json", pretty=True)
convert_csv("sales_data.csv", "xml", "sales_data.xml", root_tag="rows")
```
