# Development Guide

## Getting Started

### Prerequisites
- Python 3.8+
- Git
- Make (optional, for convenience commands)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ayoub3bidi/swiss-knife.git
   cd swiss-knife
   ```

2. **Set up development environment**
   ```bash
   make dev-setup
   # Or manually:
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .[dev,all]
   ```

3. **Verify installation**
   ```bash
   make validate
   pytest --version
   ruff --version
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   make quality  # Runs linting, security, and type checks
   make test     # Runs test suite
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

### Available Make Commands

```bash
make help          # Show all available commands
make install-dev   # Install with development dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting checks
make format        # Format code
make security      # Run security checks
make quality       # Run all quality checks
make build         # Build package
make clean         # Clean build artifacts
make ci            # Run full CI pipeline locally
```

## Coding Standards

### Python Style
- **Line Length**: 88 characters (Ruff default)
- **Imports**: Sorted with isort (handled by ruff)
- **Formatting**: Handled by ruff formatter
- **Type Hints**: Required for all public APIs

### Code Quality Tools
- **Linting**: ruff
- **Formatting**: ruff format
- **Type Checking**: mypy (optional but recommended)
- **Security**: bandit

### Naming Conventions
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private Members**: `_leading_underscore`

### Documentation
- **Docstrings**: Google style for all public functions/classes
- **Type Hints**: Use modern syntax (Python 3.8+)
- **Comments**: Explain why, not what

Example:
```python
def process_files(
    paths: List[Path], 
    algorithm: str = "sha256",
    min_size: int = 0
) -> Dict[str, List[Path]]:
    """Process files and return results.
    
    Args:
        paths: List of file paths to process
        algorithm: Hash algorithm to use
        min_size: Minimum file size in bytes
        
    Returns:
        Dictionary mapping results to file lists
        
    Raises:
        ValidationError: If paths are invalid
        SafetyError: If operation is unsafe
    """
```

## Testing Guidelines

### Test Structure
```
tests/
├── __init__.py
├── test_core.py              # Core utilities tests
├── test_duplicate_finder.py  # Module-specific tests
├── test_csv_converter.py
├── test_password_generator.py
└── conftest.py               # Shared fixtures
```

### Writing Tests
- **Use pytest**: Modern testing framework
- **Fixtures**: Use `tmp_path` for file operations
- **Mocking**: Mock external dependencies
- **Coverage**: Aim for 95%+ on core modules

Example test:
```python
def test_find_duplicates_with_duplicates(tmp_path):
    """Test finding actual duplicates."""
    # Create test files
    content = "duplicate content"
    (tmp_path / "file1.txt").write_text(content)
    (tmp_path / "file2.txt").write_text(content)
    
    # Test functionality
    finder = DuplicateFinder()
    duplicates = finder.find_duplicates([tmp_path])
    
    # Assertions
    assert len(duplicates) == 1
    duplicate_files = list(duplicates.values())[0]
    assert len(duplicate_files) == 2
```

### Test Categories
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test module interactions
- **CLI Tests**: Test command-line interfaces
- **Security Tests**: Test input validation and safety

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_duplicate_finder.py

# Specific test
pytest tests/test_duplicate_finder.py::test_find_duplicates

# With coverage
pytest --cov=swiss_knife --cov-report=html

# Fast tests (no coverage)
pytest -q --disable-warnings
```

## Security Considerations

### Input Validation
- Validate all user inputs
- Sanitize file paths
- Check file sizes and limits
- Validate regex patterns

### Safe Operations
- Require confirmation for destructive operations
- Implement dry-run modes
- Use atomic operations where possible
- Provide rollback capabilities

### Dependencies
- Minimize external dependencies
- Pin dependency versions
- Regular security audits with bandit
- Monitor for vulnerabilities

## Performance Guidelines

### Memory Management
- Use generators for large datasets
- Implement streaming for file operations
- Set reasonable memory limits
- Profile memory usage for large operations

### I/O Operations
- Use efficient file reading patterns
- Implement progress indicators for long operations
- Consider async operations for I/O-bound tasks
- Batch operations where appropriate

## Release Process

### Version Management
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version in `swiss_knife/__init__.py`
- Create git tags for releases
- Maintain CHANGELOG.md

### Pre-release Checklist
- [ ] All tests pass
- [ ] Coverage requirements met
- [ ] Documentation updated
- [ ] Security scan clean
- [ ] Performance benchmarks acceptable
- [ ] Breaking changes documented

### Release Steps
1. Update version and changelog
2. Run full test suite
3. Build and test package
4. Create release PR
5. Tag release after merge
6. Build and upload to PyPI
7. Create GitHub release

## Debugging

### Common Issues
- **Import Errors**: Check package installation with `pip list`
- **Test Failures**: Run with `-v` for verbose output
- **Linting Errors**: Use `ruff check --fix` for auto-fixes
- **Coverage Issues**: Use `--cov-report=html` for detailed report

### Debug Tools
- **pytest**: Use `-s` to see print statements
- **pdb**: Python debugger for interactive debugging
- **logging**: Use logging module for debug output
- **profiling**: Use cProfile for performance analysis

### Getting Help
- Check existing issues on GitHub
- Review documentation in `docs/`
- Ask questions in discussions
- Follow contributing guidelines

## Contributing Guidelines

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines including:
- Code of conduct
- Issue reporting
- Pull request process
- Review criteria
