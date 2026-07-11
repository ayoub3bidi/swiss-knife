# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | Yes                |
| < 0.1.0 | No                 |

## Reporting a Vulnerability

If you discover a security vulnerability in Swiss Knife, please report it responsibly.

**Do not** open a public GitHub issue for security vulnerabilities.

Instead, email the maintainer directly at **contact@ayoub3bidi.me** with:

- A description of the vulnerability
- Steps to reproduce the issue
- The potential impact
- Any suggested fixes (optional)

You should receive an acknowledgment within 48 hours. We will work with you to understand and address the issue before any public disclosure.

## Security Measures

### Package Level
- Uses Python's `secrets` module for cryptographically secure random generation
- Path traversal attack prevention via `validate_path()`
- Input sanitization and validation at all entry points
- Optional `defusedxml` integration for XML parsing safety
- Configurable file size limits to prevent resource exhaustion

### CI/CD Pipeline
- Bandit security linting on every push
- Semgrep static analysis via GitHub Actions
- CodeQL code scanning for vulnerability detection
- Dependency review for pull requests

### Best Practices for Users
- Always install from PyPI using `pip install swiss-knife-py`
- Use a virtual environment for installation
- Keep the package updated to the latest version
- Review CLI tool output before using `--delete-duplicates` or similar destructive flags
