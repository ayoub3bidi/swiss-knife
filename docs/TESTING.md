# Testing Guide for Swiss Knife

This guide explains how to test Swiss Knife functionality both automatically and manually.

## Automated Testing

### Running Unit Tests

```bash
# Install development dependencies
pip install -e .[dev,all]

# Run all tests
pytest

# Run tests with coverage
pytest --cov=swiss_knife --cov-report=html

# Run specific test file
pytest tests/test_duplicate_finder.py

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest --maxfail=1
```

### Test Coverage Requirements

- **Overall Coverage**: 80% minimum
- **Core Modules**: 95% minimum (duplicate_finder, csv_converter, password_generator)
- **CLI Modules**: 60% minimum (focused on argument parsing)

### Code Quality Checks

```bash
# Linting with ruff
ruff check swiss_knife/

# Linting with flake8
flake8 swiss_knife/

# Type checking with mypy
mypy swiss_knife/

# Security scanning with bandit
bandit -r swiss_knife/
```

## Manual Testing

### File Management Tools

#### Duplicate Finder

```bash
# Create test files
mkdir -p /tmp/test_duplicates
echo "content1" > /tmp/test_duplicates/file1.txt
echo "content1" > /tmp/test_duplicates/file2.txt
echo "content2" > /tmp/test_duplicates/file3.txt

# Test duplicate detection
sk-duplicates /tmp/test_duplicates

# Expected output: Should find file1.txt and file2.txt as duplicates

# Test with different algorithms
sk-duplicates /tmp/test_duplicates --algorithm md5
sk-duplicates /tmp/test_duplicates --algorithm sha1

# Test deletion (with confirmation)
sk-duplicates /tmp/test_duplicates --delete-duplicates

# Test force deletion (no confirmation)
sk-duplicates /tmp/test_duplicates --delete-duplicates --yes
```

#### Bulk Renamer

```bash
# Create test files
mkdir -p /tmp/test_rename
touch /tmp/test_rename/IMG_001.jpg
touch /tmp/test_rename/IMG_002.jpg
touch /tmp/test_rename/IMG_003.jpg

# Test dry run (safe)
sk-rename "IMG_(\d+)" "photo_\1" /tmp/test_rename --dry-run

# Expected output: Shows what would be renamed without actually doing it

# Test actual rename
sk-rename "IMG_(\d+)" "photo_\1" /tmp/test_rename

# Verify files are renamed to photo_001.jpg, photo_002.jpg, etc.
ls /tmp/test_rename/
```

### Text Processing Tools

#### CSV Converter

```bash
# Create test CSV
cat > /tmp/test.csv << EOF
name,age,active,score
John,25,true,85.5
Jane,30,false,92.0
Bob,35,true,78.5
EOF

# Test JSON conversion
sk-csv /tmp/test.csv --format json --pretty

# Test XML conversion
sk-csv /tmp/test.csv --format xml --root-tag users --row-tag user

# Test with custom output file
sk-csv /tmp/test.csv --format json --output /tmp/output.json

# Verify output file exists and contains valid JSON
cat /tmp/output.json | python -m json.tool
```

### Security Tools

#### Password Generator

```bash
# Generate basic password
sk-password

# Generate with specific length
sk-password --length 20

# Generate with symbols
sk-password --length 16 --symbols

# Generate without ambiguous characters
sk-password --length 16 --exclude-ambiguous

# Generate multiple passwords
sk-password --count 5 --length 12

# Test password strength checking
sk-password --check "mypassword123"
sk-password --check "MyStr0ng!P@ssw0rd"
```

## Integration Testing

### End-to-End Workflows

#### File Organization Workflow

```bash
# Create a messy directory structure
mkdir -p /tmp/file_test/{photos,documents,downloads}
echo "photo1" > /tmp/file_test/photos/IMG_001.jpg
echo "photo1" > /tmp/file_test/downloads/IMG_001.jpg  # duplicate
echo "doc1" > /tmp/file_test/documents/report.txt
echo "doc2" > /tmp/file_test/downloads/document.txt

# 1. Find duplicates
sk-duplicates /tmp/file_test --export-json /tmp/duplicates.json

# 2. Clean up duplicates
sk-duplicates /tmp/file_test --delete-duplicates --keep-strategy shortest_name --yes

# 3. Rename files in downloads
sk-rename "IMG_(\d+)" "download_\1" /tmp/file_test/downloads

# 4. Verify results
find /tmp/file_test -type f
```

#### Data Processing Workflow

```bash
# Create sample data
cat > /tmp/sales.csv << EOF
date,product,quantity,price
2023-01-01,Widget A,10,25.50
2023-01-02,Widget B,5,30.00
2023-01-03,Widget A,8,25.50
EOF

# 1. Convert to JSON
sk-csv /tmp/sales.csv --format json --output /tmp/sales.json

# 2. Verify conversion
python -c "import json; print(json.load(open('/tmp/sales.json')))"

# 3. Convert to XML
sk-csv /tmp/sales.csv --format xml --output /tmp/sales.xml

# 4. Verify XML structure
cat /tmp/sales.xml
```

## Performance Testing

### Large File Handling

```bash
# Create large CSV file (adjust size as needed)
python -c "
import csv
with open('/tmp/large.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'name', 'value'])
    for i in range(100000):
        writer.writerow([i, f'item_{i}', i * 1.5])
"

# Test CSV conversion performance
time sk-csv /tmp/large.csv --format json --output /tmp/large.json

# Test duplicate finder on many files
mkdir -p /tmp/many_files
for i in {1..1000}; do
    echo "content_$((i % 100))" > /tmp/many_files/file_$i.txt
done

time sk-duplicates /tmp/many_files
```

### Memory Usage Testing

```bash
# Monitor memory usage during operations
# Install psutil if not available: pip install psutil

python -c "
import psutil
import subprocess
import time

# Start monitoring
process = subprocess.Popen(['sk-duplicates', '/tmp/many_files'])
p = psutil.Process(process.pid)

max_memory = 0
while process.poll() is None:
    try:
        memory = p.memory_info().rss / 1024 / 1024  # MB
        max_memory = max(max_memory, memory)
        time.sleep(0.1)
    except psutil.NoSuchProcess:
        break

print(f'Max memory usage: {max_memory:.2f} MB')
"
```

## Error Handling Testing

### Invalid Input Testing

```bash
# Test with non-existent files
sk-duplicates /nonexistent/path
# Expected: Error message about path not existing

# Test with invalid regex
sk-rename "[invalid" "replacement" /tmp/test_rename
# Expected: Error message about invalid regex

# Test with invalid CSV
echo "invalid,csv,data" > /tmp/invalid.csv
echo "missing,columns" >> /tmp/invalid.csv
sk-csv /tmp/invalid.csv --format json
# Expected: Should handle gracefully or show clear error

# Test password generation with impossible constraints
sk-password --length 5 --min-uppercase 3 --min-lowercase 3 --min-digits 3
# Expected: Error about impossible constraints
```

### Permission Testing

```bash
# Test with read-only directory
mkdir -p /tmp/readonly_test
echo "test" > /tmp/readonly_test/file.txt
chmod -w /tmp/readonly_test

sk-duplicates /tmp/readonly_test --delete-duplicates --yes
# Expected: Should handle permission errors gracefully

# Restore permissions
chmod +w /tmp/readonly_test
```

## Cleanup

```bash
# Clean up test files
rm -rf /tmp/test_duplicates /tmp/test_rename /tmp/file_test
rm -f /tmp/test.csv /tmp/output.json /tmp/sales.* /tmp/large.*
rm -rf /tmp/many_files /tmp/readonly_test
```

## Continuous Integration Testing

The CI pipeline runs these tests automatically:

1. **Unit Tests**: All pytest tests across Python 3.7-3.12
2. **Code Quality**: ruff, flake8, mypy checks
3. **Security**: bandit security scanning
4. **Coverage**: Minimum 80% coverage requirement
5. **Build**: Package building and installation testing

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure package is installed with `pip install -e .`
2. **Permission Errors**: Run tests in directories you have write access to
3. **Missing Dependencies**: Install optional dependencies with `pip install swiss-knife[all]`
4. **Path Issues**: Use absolute paths or ensure working directory is correct

### Debug Mode

```bash
# Run with verbose output
sk-duplicates /path --verbose

# Run with debug logging
SWISS_KNIFE_DEBUG=1 sk-duplicates /path

# Run Python API with debugging
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from swiss_knife.file_management import find_duplicates
result = find_duplicates(['/path'])
print(result)
"
```
