# Contributing to Swiss Knife

Thank you for your interest in contributing to Swiss Knife! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to ayoub3bidi@gmail.com.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of command-line tools

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/swiss-knife.git
   cd swiss-knife
   ```
3. **Set up the development environment**:
   ```bash
   make dev-setup
   ```
4. **Verify the setup**:
   ```bash
   make validate
   make test
   ```

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Implement features or fix bugs
- **Documentation**: Improve or add documentation
- **Testing**: Add or improve tests
- **Performance**: Optimize existing code

### Before You Start

1. **Check existing issues** to avoid duplicate work
2. **Discuss major changes** by opening an issue first
3. **Read the documentation** to understand the project structure
4. **Review recent pull requests** to understand the contribution style

## Development Process

### Workflow

1. **Create an issue** (for bugs/features) or find an existing one
2. **Fork and clone** the repository
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/issue-123-add-new-tool
   ```
4. **Make your changes** following our coding standards
5. **Add tests** for new functionality
6. **Update documentation** as needed
7. **Run quality checks**:
   ```bash
   make quality
   make test-cov
   ```
8. **Commit your changes** with a descriptive message
9. **Push to your fork** and create a pull request

### Branch Naming

Use descriptive branch names:
- `feature/issue-123-add-csv-tool`
- `bugfix/issue-456-fix-memory-leak`
- `docs/update-installation-guide`
- `refactor/improve-error-handling`

### Commit Messages

Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(automation): add password strength analyzer

Add comprehensive password strength analysis with detailed feedback
including entropy calculation and common pattern detection.

Closes #123
```

## Coding Standards

### Python Style Guide

- **PEP 8** compliance (enforced by ruff)
- **Line length**: 88 characters
- **Type hints**: Required for all public APIs
- **Docstrings**: Google style for all public functions/classes

### Code Quality

All code must pass:
- **Linting**: `ruff check`
- **Formatting**: `ruff format`
- **Type checking**: `mypy` (recommended)
- **Security**: `bandit`

### Architecture Principles

- **Security first**: All operations must be safe by default
- **Modularity**: Keep modules independent and focused
- **Testability**: Write testable code with clear interfaces
- **Documentation**: Document all public APIs

### Example Code Style

```python
from typing import List, Dict, Optional
from pathlib import Path

def process_files(
    file_paths: List[Path],
    algorithm: str = "sha256",
    min_size: Optional[int] = None,
) -> Dict[str, List[Path]]:
    """Process files and return grouped results.
    
    Args:
        file_paths: List of file paths to process
        algorithm: Hash algorithm to use for processing
        min_size: Minimum file size filter (bytes)
        
    Returns:
        Dictionary mapping hash values to file path lists
        
    Raises:
        ValidationError: If file paths are invalid
        SafetyError: If operation would be unsafe
    """
    # Implementation here
    pass
```

## Testing Guidelines

### Test Requirements

- **Coverage**: Minimum 65% overall, 95% for core modules
- **Types**: Unit tests, integration tests, CLI tests
- **Mocking**: Mock external dependencies and I/O operations
- **Fixtures**: Use pytest fixtures for test data

### Writing Tests

```python
import pytest
from pathlib import Path
from swiss_knife.file_management import DuplicateFinder

class TestDuplicateFinder:
    """Test duplicate file finder functionality."""
    
    def test_find_duplicates_basic(self, tmp_path):
        """Test basic duplicate detection."""
        # Arrange
        content = "test content"
        (tmp_path / "file1.txt").write_text(content)
        (tmp_path / "file2.txt").write_text(content)
        
        finder = DuplicateFinder()
        
        # Act
        result = finder.find_duplicates([tmp_path])
        
        # Assert
        assert len(result) == 1
        duplicate_files = list(result.values())[0]
        assert len(duplicate_files) == 2
```

### Running Tests

```bash
# All tests
make test

# With coverage
make test-cov

# Specific test file
pytest tests/test_duplicate_finder.py

# Specific test
pytest tests/test_duplicate_finder.py::TestDuplicateFinder::test_find_duplicates_basic
```

## Documentation

### Types of Documentation

- **API Documentation**: Docstrings for all public functions/classes
- **User Documentation**: README, usage examples
- **Developer Documentation**: Architecture, development guide
- **CLI Documentation**: Help text and examples

### Documentation Standards

- **Clear and concise**: Easy to understand
- **Examples**: Include practical examples
- **Up-to-date**: Keep documentation current with code changes
- **Accessible**: Use simple language and clear structure

### Updating Documentation

When making changes:
1. Update relevant docstrings
2. Update README if adding new features
3. Update CLI help text
4. Add examples for new functionality
5. Update architecture docs for structural changes

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** on multiple platforms
4. **Documentation review**
5. **Final approval** and merge

### Review Criteria

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it well-written and maintainable?
- **Testing**: Are there adequate tests?
- **Documentation**: Is it properly documented?
- **Security**: Are there any security concerns?
- **Performance**: Does it impact performance?

## Issue Reporting

### Bug Reports

Use the bug report template and include:
- **Description**: Clear description of the bug
- **Steps to reproduce**: Detailed reproduction steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, package version
- **Additional context**: Screenshots, logs, etc.

### Feature Requests

Use the feature request template and include:
- **Problem**: What problem does this solve?
- **Solution**: Proposed solution
- **Alternatives**: Alternative solutions considered
- **Additional context**: Use cases, examples

### Security Issues

For security vulnerabilities:
1. **Do not** create a public issue
2. **Email** ayoub3bidi@gmail.com directly
3. **Include** detailed information about the vulnerability
4. **Wait** for acknowledgment before public disclosure

## Community

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code contributions
- **Email**: ayoub3bidi@gmail.com for sensitive issues

### Getting Help

- **Documentation**: Check docs/ directory first
- **Issues**: Search existing issues
- **Discussions**: Ask questions in GitHub Discussions
- **Code**: Review existing code for examples

### Recognition

Contributors are recognized through:
- **Contributors file**: Listed in CONTRIBUTORS.md
- **Release notes**: Mentioned in changelog
- **GitHub**: Contributor statistics
- **Community**: Recognition in discussions

## License

By contributing to Swiss Knife, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing, please:
1. Check this document and other documentation
2. Search existing issues and discussions
3. Create a new discussion or issue
4. Contact maintainers directly if needed

Thank you for contributing to Swiss Knife! 🛠️
