# Swiss Knife Architecture

## Overview

Swiss Knife is designed as a modular Python package that provides automation tools through both programmatic APIs and command-line interfaces. The architecture emphasizes security, testability, and extensibility.

## Package Structure

```
swiss_knife/
├── __init__.py              # Package metadata, version, top-level re-exports
├── core.py                  # Core utilities and safety functions
├── utilities/
│   └── common.py            # General-purpose helpers (env parsing, camelCase, etc.)
├── automation/
│   └── password_generator.py
├── file_management/
│   ├── duplicate_finder.py
│   └── bulk_renamer.py
├── text_processing/
│   └── csv_converter.py
└── cli/
    ├── _common.py           # Shared CLI helpers (e.g. --version)
    ├── main.py              # sk (umbrella: version + tool listing)
    ├── duplicate_finder.py  # sk-duplicates
    ├── csv_cli.py           # sk-csv
    ├── password_cli.py      # sk-password
    └── rename_cli.py        # sk-rename
```

## Design Principles

### 1. Security First
- All destructive operations require explicit confirmation
- Input validation and sanitization at all entry points
- Safe defaults for all operations
- Protection against path traversal and injection attacks

### 2. Modular Design
- Each module is self-contained with minimal dependencies
- Clear separation between API and CLI layers
- Consistent error handling patterns across modules

### 3. Memory Safety
- Streaming processing for large files
- Configurable memory limits
- Efficient algorithms for resource-intensive operations

### 4. Testability
- Dependency injection for external resources
- Comprehensive mocking of I/O operations
- Clear separation of concerns for unit testing

## Core Components

### Core Module (`core.py`)
Provides foundational utilities used across all modules:

- **Safety Functions**: `confirm_destructive_action()`, `check_file_size_limit()`
- **Validation**: `validate_path()`, `safe_filename()`
- **Exception Classes**: `SafetyError`, `ValidationError`

### Utilities Module (`utilities/`)
General-purpose helpers re-exported at the top level for convenience:

- **Type checks**: `parse_bool()`, `is_empty()`, `is_not_empty()`, `is_numeric()`, `is_true()`, `is_false()`
- **Environment**: `get_env_int()`, `get_env_float()`, `get_env_bool()`
- **Data transforms**: `convert_keys_to_camel_case()`, `to_camel_case()`
- **Sanitizers**: `sanitize_metric_name()`, `sanitize_header_name()`
- **Validators**: `is_uuid()`, `is_http_status_code()`
- **Encoding**: `decode_base64_text()`
- **Mapping helpers**: `has_value()`, `get_or_default()`, `delete_if_present()`

### API Layer
Each functional module exposes:
- **Classes**: Main functionality encapsulated in classes
- **Functions**: Convenience functions for common operations
- **Type Hints**: Full type annotations for better IDE support

### CLI Layer
Thin wrappers around the API layer:
- **Argument Parsing**: Consistent argparse usage
- **Error Handling**: User-friendly error messages
- **Output Formatting**: Human-readable output

## Data Flow

```
User Input → CLI Parser → API Layer → Core Utilities → External Resources
     ↓           ↓           ↓            ↓              ↓
Error Handling ← Validation ← Safety ← Exception ← I/O Operations
```

## Security Architecture

### Input Validation
1. **Path Validation**: All file paths are resolved and validated
2. **Size Limits**: Configurable limits for file processing
3. **Pattern Validation**: Regex patterns are compiled and validated
4. **Type Checking**: Runtime type validation for critical operations

### Safe Operations
1. **Confirmation Prompts**: All destructive operations require confirmation
2. **Dry Run Mode**: Preview operations before execution
3. **Atomic Operations**: Operations are atomic where possible (best-effort; not all I/O can be made atomic on every filesystem)
4. **Failure Isolation**: Operations are designed to fail cleanly — partial results are not silently committed, and error paths avoid leaving orphaned state where feasible

### Error Handling
1. **Structured Exceptions**: Custom exception hierarchy
2. **Context Preservation**: Error messages include relevant context
3. **Graceful Degradation**: Partial failures don't crash the application
4. **Logging**: Comprehensive logging for debugging

## Extension Points

### Adding New Modules
1. Create module directory under `swiss_knife/`
2. Implement API classes and functions
3. Add CLI wrapper in `swiss_knife/cli/`
4. Update `pyproject.toml` console scripts
5. Add comprehensive tests

### Adding New CLI Tools
1. Create CLI module in `swiss_knife/cli/`
2. Follow existing argument parsing patterns
3. Add console script entry point
4. Include help text and examples

## Performance Considerations

### Memory Management
- Streaming I/O for large files
- Generator-based processing where applicable
- Configurable memory limits
- Efficient data structures

## Dependencies

### Core Package
- **Zero runtime dependencies** (base install)
- **Optional**: `defusedxml` for hardened XML handling (`[xml]` / `[all]` extras)

### Development Dependencies
- **Testing**: pytest, pytest-cov
- **Linting**: ruff, mypy
- **Security**: bandit

### Standalone Scripts (`scripts/`)
The `scripts/` directory contains standalone script trees (`scripts/automation/`, `scripts/convert/`, `scripts/file_management/`, `scripts/network_web/`, `scripts/system_utilities/`, `scripts/text_processing/`, `scripts/utilities/`, `scripts/development_tools/`) that are **not** part of the installable package. These may have their own `requirements.txt` files with heavier dependencies (e.g. Pillow, pydub, psutil, qrcode). They are not installed by `pip install swiss-knife-py`.

These scripts predate the packaged modules and have **not been audited for divergence**. Some (e.g. `scripts/file_management/`, `scripts/text_processing/`, `scripts/utilities/`) overlap with or duplicate functionality now provided by `swiss_knife.*`. They are retained for reference and standalone use; the packaged modules are the maintained, tested, and recommended APIs. CI does not enforce that standalone scripts avoid importing `swiss_knife` internals — treat them as independent artifacts.

## Testing Strategy

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Cover edge cases and error conditions

### Integration Tests
- Test module interactions
- Use temporary directories for file operations
- Test CLI interfaces end-to-end
- Validate error handling paths

### Security Tests
- Test input validation
- Verify safe defaults
- Test permission handling
- Validate against common attack vectors

## Deployment Architecture

### Package Distribution
- PyPI distribution with semantic versioning
- Multiple installation options (core, extras, all)
- Wheel and source distributions
- Cross-platform compatibility

### CLI Integration
- Console script entry points
