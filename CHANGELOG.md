# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-22

### Added

#### File Management
- **Duplicate File Finder**: Find and manage duplicate files using cryptographic hashing
  - Support for MD5, SHA1, SHA256, and SHA512 algorithms
  - Configurable minimum file size filtering
  - Multiple keep strategies (first, last, shortest/longest name)
  - Safe deletion with confirmation prompts
  - CLI tool: `sk-duplicates`

- **Bulk File Renamer**: Rename multiple files using regex patterns
  - Regex-based pattern matching and replacement
  - Safety checks for name collisions and existing files
  - Dry-run mode to preview changes
  - Recursive directory processing
  - CLI tool: `sk-rename`

#### Text Processing
- **CSV Converter**: Convert CSV files to JSON or XML formats
  - Intelligent type inference (integers, floats, booleans)
  - Configurable delimiters with auto-detection
  - Pretty-print JSON output
  - Customizable XML structure (root/row tags)
  - File size limits for safety
  - CLI tool: `sk-csv`

#### Security & Automation
- **Password Generator**: Generate cryptographically secure passwords
  - Customizable length and character sets
  - Minimum requirements enforcement (uppercase, lowercase, digits, symbols)
  - Ambiguous character exclusion option
  - Batch password generation
  - Password strength analyzer with detailed feedback
  - CLI tool: `sk-password`

#### Core Features
- **Safety-First Design**: All destructive operations require explicit confirmation
- **Input Validation**: Comprehensive path and parameter validation
- **Custom Exceptions**: `SafetyError` and `ValidationError` for clear error handling
- **Path Traversal Protection**: Built-in security against directory traversal attacks
- **defusedxml Support**: Optional XML bomb protection for CSV-to-XML conversion

#### Documentation
- Comprehensive README with examples and security highlights
- Detailed CONTRIBUTING.md with coding standards and workflow
- CODE_OF_CONDUCT.md for community guidelines
- API reference documentation
- CLI reference documentation
- Architecture and development guides

#### Development & CI/CD
- Multi-version Python testing (3.8 - 3.12)
- Automated CI pipeline with GitHub Actions
- Security scanning (Bandit, CodeQL, Semgrep, Safety)
- Code coverage reporting with Codecov
- Automated release workflow with PyPI publishing
- Dependency review and vulnerability scanning
- Development Makefile with 20+ commands

### Security
- Uses `secrets` module for cryptographically secure random generation
- Path traversal attack prevention
- Optional defusedxml integration for XML parsing safety
- Memory limits on file processing
- Input sanitization and validation throughout

### Testing
- Comprehensive test suite with pytest
- Code coverage tracking (68%+ overall)
- Tests for all core modules and CLI tools
- Mock-based testing for external I/O

### Package Information
- MIT License
- Python 3.8+ support
- Zero required dependencies (defusedxml optional)
- Development dependencies: pytest, ruff, mypy, bandit

[0.1.0]: https://github.com/ayoub3bidi/swiss-knife/releases/tag/v0.1.0
