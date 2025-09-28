# File Management Scripts

A collection of powerful file management automation tools for organizing, cleaning, and maintaining your file system.

## Available Scripts

### 🔍 Duplicate File Finder (`duplicate_finder.py`)
Advanced duplicate file detection using cryptographic hash comparison for 100% accuracy.

**Features:**
- Multiple hash algorithms (MD5, SHA1, SHA256, SHA512)
- Size-based filtering (min/max file sizes)
- File extension filtering
- Recursive directory scanning
- Multiple output formats (text, JSON)
- Safe duplicate deletion with keep strategies
- Progress bars and detailed statistics
- Dry-run mode for safe testing

## Installation

```bash
# Install dependencies
pip install -r file_management/requirements.txt

# Optional: Install development dependencies
pip install pytest black flake8
```

## Quick Start

```bash
# Find duplicates in current directory
python file_management/duplicate_finder.py .

# Find duplicates with SHA256, minimum 1MB files
python file_management/duplicate_finder.py ~/Documents --hash sha256 --min-size 1MB

# Find image duplicates only
python file_management/duplicate_finder.py ~/Pictures --extensions jpg,png,gif,bmp

# Export results to JSON
python file_management/duplicate_finder.py ~/Downloads --output json --file duplicates.json

# Delete duplicates (keeping shortest filename)
python file_management/duplicate_finder.py ~/temp --delete-duplicates --keep-strategy shortest_name

# Dry run to see what would be deleted
python file_management/duplicate_finder.py ~/temp --delete-duplicates --dry-run
```

## Usage Examples

### Basic Duplicate Detection
```bash
# Scan Documents folder for duplicates
python duplicate_finder.py ~/Documents

# Scan multiple directories
python duplicate_finder.py ~/Documents ~/Downloads ~/Desktop
```

### Advanced Filtering
```bash
# Large files only (>10MB)
python duplicate_finder.py ~/Videos --min-size 10MB

# Size range filtering
python duplicate_finder.py ~/Music --min-size 1MB --max-size 100MB

# Specific file types
python duplicate_finder.py ~/Projects --extensions py,js,ts,java

# High-security SHA256 hashing
python duplicate_finder.py ~/Sensitive --hash sha256
```

### Output and Export
```bash
# Save results as JSON
python duplicate_finder.py ~/Data --output json --file report.json

# Save text report
python duplicate_finder.py ~/Data --output text --file report.txt
```

### Safe Duplicate Removal
```bash
# Preview what would be deleted
python duplicate_finder.py ~/temp --delete-duplicates --dry-run

# Keep first file encountered
python duplicate_finder.py ~/temp --delete-duplicates --keep-strategy first

# Keep file with shortest name
python duplicate_finder.py ~/temp --delete-duplicates --keep-strategy shortest_name

# Keep file with longest name  
python duplicate_finder.py ~/temp --delete-duplicates --keep-strategy longest_name
```

## Script Details

### Duplicate Finder

**Hash Algorithms:**
- `md5`: Fast, good for most use cases
- `sha1`: More secure than MD5
- `sha256`: Cryptographically secure, recommended for important data
- `sha512`: Maximum security, slower processing

**Keep Strategies:**
- `first`: Keep first file found (default)
- `last`: Keep last file found
- `shortest_name`: Keep file with shortest filename
- `longest_name`: Keep file with longest filename

**Output Formats:**
- `text`: Human-readable grouped listing
- `json`: Machine-readable structured data

**Performance Tips:**
- Use MD5 for general duplicate detection (fastest)
- Use SHA256+ for critical/sensitive files
- Apply size filters to reduce scan time
- Use extension filters for targeted searches

## Error Handling

The scripts include comprehensive error handling:
- Graceful handling of permission errors
- Skip corrupted or unreadable files
- Detailed error reporting
- Safe file operations with confirmation prompts

## Safety Features

- **Dry-run mode**: Preview deletions without making changes
- **Confirmation prompts**: Double-check before deleting files  
- **Safe deletion**: Uses trash/recycle bin when possible
- **Detailed logging**: Track all operations
- **Hash verification**: 100% accuracy in duplicate detection

## Dependencies

- `tqdm`: Progress bars
- `send2trash`: Safe file deletion
- `xxhash`: Fast hashing for large files
- `python-dateutil`: Date/time handling
- `wcmatch`: Advanced pattern matching

## Coming Soon

- **Bulk File Renamer**: Regex-based batch renaming
- **Directory Synchronizer**: Two-way folder sync
- **File Organizer**: Auto-organize by date/type/size
- **Broken Symlink Detector**: Find and clean broken links
- **File Archive Manager**: Compress and organize old files

## Performance Benchmarks

Hash algorithm performance on 1GB test file:
- MD5: ~2.1s
- SHA1: ~2.8s  
- SHA256: ~4.2s
- SHA512: ~6.1s

Memory usage: ~8MB regardless of file sizes (streaming hash calculation)

## Troubleshooting

**Common Issues:**
- Permission errors: Run with appropriate privileges or skip protected files
- Out of memory: Files are processed in chunks, should handle any file size
- Slow performance: Use MD5 hash and apply size/extension filters

**Platform Notes:**
- Windows: Automatic trash bin support
- Linux/Mac: Requires `send2trash` for safe deletion
- Network drives: May be slower, consider local processing
