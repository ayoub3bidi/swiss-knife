# Swiss Knife Architecture

## Overview

Swiss Knife is designed as a modular Python package that provides automation tools through both programmatic APIs and command-line interfaces. The architecture emphasizes security, testability, and extensibility.

## Package Structure

```
swiss_knife/
├── __init__.py              # Package metadata and version
├── core.py                  # Core utilities and safety functions
├── automation/              # Security and automation tools
│   ├── __init__.py
│   └── password_generator.py
├── file_management/         # File operation tools
│   ├── __init__.py
│   ├── duplicate_finder.py
│   └── bulk_renamer.py
├── text_processing/         # Text manipulation tools
│   ├── __init__.py
│   └── csv_converter.py
└── cli/                     # Command-line interfaces
    ├── __init__.py
    └── duplicate_finder.py
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
3. **Atomic Operations**: Operations are atomic where possible
4. **Rollback Capability**: Failed operations don't leave partial state

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

### Concurrency
- Thread-safe operations where needed
- Async support for I/O-bound operations (future)
- Process-based parallelism for CPU-intensive tasks

### Caching
- Intelligent caching of computed results
- Cache invalidation strategies
- Memory-bounded caches

## Dependencies

### Core Dependencies
- **Standard Library**: Minimal external dependencies
- **Type Hints**: `typing` module for Python < 3.9

### Optional Dependencies
- **Media Processing**: Pillow, pydub (media extras)
- **Network Operations**: requests, qrcode (network extras)
- **System Monitoring**: psutil (system extras)

### Development Dependencies
- **Testing**: pytest, pytest-cov
- **Linting**: ruff, flake8, mypy
- **Security**: bandit
- **Building**: build, twine

## Testing Strategy

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Cover edge cases and error conditions
- Achieve 95%+ coverage for core modules

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
- Shell completion support (future)
- Man page generation (future)
- Docker image (future)

## Future Architecture Considerations

### Scalability
- Plugin architecture for third-party extensions
- Configuration file support
- Distributed processing capabilities
- Web API interface

### Monitoring
- Metrics collection
- Performance monitoring
- Error tracking
- Usage analytics (opt-in)

### Compatibility
- Backward compatibility guarantees
- Migration tools for breaking changes
- Version compatibility matrix
- Deprecation policies
