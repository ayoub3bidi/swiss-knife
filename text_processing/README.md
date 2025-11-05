# Text Processing Tools

Collection of utilities for text file manipulation, conversion, and analysis.

## Available Scripts

### 📊 CSV to JSON/XML Converter (`csv_converter.py`)
Convert CSV files to JSON or XML format with intelligent type inference and flexible formatting options.

**Features:**
- Multi-format output (JSON, XML)
- Automatic type inference (numbers, booleans)
- Custom delimiters (comma, tab, pipe, etc.)
- Header normalization (spaces → underscores, lowercase)
- Empty row/field handling
- Whitespace trimming
- Multiple encoding support
- Progress tracking
- Compression statistics

### 📝 Markdown to HTML Converter (`markdown_converter.py`)
Convert Markdown files to styled HTML with syntax highlighting, themes, and table of contents.

**Features:**
- Multiple HTML templates (minimal, styled)
- Syntax highlighting with multiple themes (GitHub, Monokai, Dracula, Solarized)
- Automatic table of contents generation
- Table support
- YAML frontmatter metadata parsing
- Code block line numbers
- Custom page titles
- Batch directory conversion
- Responsive design

### 🔗 Text File Merger (`text_merger.py`)
Merge multiple text files with customizable delimiters and advanced formatting options.

**Features:**
- Multiple delimiter presets (line, double, hash, star, dash, blank, minimal, section)
- Custom delimiters support
- File headers with optional timestamps and statistics
- Flexible sorting (by name, size, date, extension)
- Content processing (line numbers, whitespace stripping, empty line removal)
- Glob patterns and recursive directory merging
- Error handling strategies (skip, stop, replace)
- Preview mode for testing

### 📈 Word Frequency Analyzer (`word_frequency.py`)
Analyze word frequency in text files with advanced filtering and pattern matching.

**Features:**
- Smart tokenization with regex patterns
- Built-in stop words removal (English) + custom stop words
- Flexible filtering (min/max length, case sensitivity, alphabetic-only)
- Context extraction (see words in actual usage)
- Search capabilities (starts-with, ends-with, contains)
- Per-file breakdown for multi-file analysis
- Word length distribution analysis
- Multiple export formats (JSON, CSV)
- ASCII bar chart visualization
- Comprehensive statistics

## Installation

```bash
# Install dependencies
pip install -r text_processing/requirements.txt
```

## Quick Start

### CSV to JSON/XML
```bash
# Convert to JSON
python text_processing/csv_converter.py data.csv -f json

# Convert to XML with custom tags
python text_processing/csv_converter.py data.csv -f xml --root-tag data --row-tag record
```

### Markdown to HTML
```bash
# Basic conversion
python text_processing/markdown_converter.py README.md

# With theme and line numbers
python text_processing/markdown_converter.py code.md --theme monokai --line-numbers
```

### Text File Merger
```bash
# Basic merge
python text_processing/text_merger.py *.txt -o merged.txt

# Merge with timestamps and line numbers
python text_processing/text_merger.py logs/*.log -o combined.log --timestamp --line-numbers
```

### Word Frequency Analyzer
```bash
# Basic analysis
python text_processing/word_frequency.py document.txt

# Remove stop words, show top 30
python text_processing/word_frequency.py article.txt --remove-stop-words --top 30

# Analyze directory with contexts
python text_processing/word_frequency.py docs/ -r --ext txt,md --contexts

# Export results
python text_processing/word_frequency.py data.txt --export-json report.json --export-csv words.csv
```

## Usage Examples

### Word Frequency Analyzer

#### Basic Analysis
```bash
# Analyze single file
python word_frequency.py document.txt

# Analyze with top 50 words
python word_frequency.py article.txt --top 50

# Show word contexts (example sentences)
python word_frequency.py story.txt --contexts --top 10
```

#### Stop Words and Filtering
```bash
# Remove common stop words
python word_frequency.py article.txt --remove-stop-words

# Custom stop words file
python word_frequency.py text.txt --remove-stop-words --stop-words-file custom_stops.txt

# Only alphabetic words, minimum length 3
python word_frequency.py doc.txt --only-alpha --min-length 3

# Words between 5-15 characters
python word_frequency.py text.txt --min-length 5 --max-length 15

# Case-sensitive analysis (distinguish Hello vs hello)
python word_frequency.py code.py --case-sensitive
```

#### Directory Analysis
```bash
# Analyze all text files in directory
python word_frequency.py docs/ --ext txt

# Recursive analysis with multiple extensions
python word_frequency.py project/ -r --ext py,js,ts,md

# Analyze source code (case-sensitive, min length 3)
python word_frequency.py src/ -r --case-sensitive --min-length 3 --ext py
```

#### Pattern Searching
```bash
# Find words starting with "pre"
python word_frequency.py text.txt --starts-with pre

# Find words ending with "tion"
python word_frequency.py article.txt --ends-with tion --top 30

# Find words containing "script"
python word_frequency.py docs/ -r --contains script

# Combine filters and search
python word_frequency.py text.txt --remove-stop-words --starts-with un --min-length 5
```

#### Export and Reporting
```bash
# Export to JSON with contexts
python word_frequency.py article.txt --export-json report.json --contexts

# Export to CSV for spreadsheet analysis
python word_frequency.py data.txt --export-csv words.csv

# Both exports
python word_frequency.py doc.txt --export-json analysis.json --export-csv frequencies.csv
```

#### Advanced Filtering
```bash
# Words appearing at least 10 times
python word_frequency.py large_doc.txt --min-frequency 10

# Exclude numbers, only letters
python word_frequency.py text.txt --no-numbers --only-alpha

# Different encoding
python word_frequency.py latin1_file.txt --encoding latin-1
```

### Real-World Scenarios

#### SEO Keyword Analysis
```bash
# Find most common keywords in blog posts
python word_frequency.py blog_posts/ -r --remove-stop-words --min-length 4 --top 50

# Export for keyword research
python word_frequency.py articles/ -r --remove-stop-words --export-csv keywords.csv
```

#### Code Analysis
```bash
# Analyze variable/function names in codebase
python word_frequency.py src/ -r --case-sensitive --min-length 3 --ext py,js,ts

# Find common patterns in code
python word_frequency.py project/ -r --starts-with get --ext py
python word_frequency.py project/ -r --contains handler --ext js
```

#### Content Writing Analysis
```bash
# Check word variety in writing
python word_frequency.py manuscript.txt --contexts --top 20

# Find overused words
python word_frequency.py essay.txt --remove-stop-words --min-frequency 10

# Analyze writing style (word length distribution)
python word_frequency.py article.txt --export-json style_analysis.json
```

#### Log File Analysis
```bash
# Find common error patterns
python word_frequency.py logs/*.log --contains error --min-frequency 5

# Analyze log keywords
python word_frequency.py server.log --remove-stop-words --export-csv log_keywords.csv
```

#### Academic/Research Analysis
```bash
# Analyze technical terminology
python word_frequency.py papers/ -r --min-length 6 --only-alpha --top 100

# Find domain-specific terms
python word_frequency.py research/ -r --remove-stop-words --min-frequency 3 --export-json terms.json
```

#### Social Media/Reviews Analysis
```bash
# Analyze customer feedback
python word_frequency.py reviews.txt --remove-stop-words --contexts --top 30

# Find sentiment indicators
python word_frequency.py feedback/ -r --starts-with good,bad,great,poor
```

### CSV Converter (Previous Examples)

#### Basic Conversions
```bash
# Convert to JSON with default settings
python csv_converter.py sales_data.csv -f json

# Tab-separated values (TSV)
python csv_converter.py data.tsv -f json -d $'\t'
```

### Markdown Converter (Previous Examples)

#### Syntax Highlighting Themes
```bash
# GitHub theme (default)
python markdown_converter.py code.md --theme github

# Dark themes
python markdown_converter.py tutorial.md --theme monokai
```

### Text File Merger (Previous Examples)

#### Basic Merging
```bash
# Merge all text files
python text_merger.py *.txt -o merged.txt

# Merge with timestamps
python text_merger.py logs/*.log -o combined.log --timestamp --stats
```

## Technical Details

### Word Frequency Implementation

**Tokenization:**
- Uses regex patterns for intelligent word extraction
- Preserves apostrophes in contractions (don't, it's)
- Handles alphanumeric tokens configurable

**Stop Words:**
- Built-in list of 100+ common English stop words
- Support for custom stop word files
- Case-insensitive matching

**Statistics Calculated:**
- Total/unique word counts
- Average word length and frequency
- Word length distribution
- Words appearing once (hapax legomena)
- Min/max/median frequencies

**Context Extraction:**
- Captures 5 words before and after target word
- Stores up to 3 example contexts per word
- Truncates long contexts to 100 characters

### Output Formats

**JSON Structure:**
```json
{
  "statistics": {
    "total_words": 5432,
    "unique_words": 1234,
    "avg_word_length": 5.67,
    "words_appearing_once": 456
  },
  "word_frequencies": {
    "python": 87,
    "code": 65,
    "function": 54
  },
  "top_50": [
    {"word": "python", "count": 87},
    {"word": "code", "count": 65}
  ],
  "words_by_length": {
    "3": 234,
    "4": 567,
    "5": 789
  }
}
```

**CSV Structure:**
```csv
Word,Frequency,Percentage,Length
python,87,1.6012,6
code,65,1.1971,4
function,54,0.9945,8
```

## Performance

### Word Frequency Analyzer
- Small files (< 1MB): < 1 second
- Medium files (1-100MB): 1-10 seconds
- Large files (100MB-1GB): 10-60 seconds
- Memory efficient: streaming tokenization

### CSV Converter
- Small files (< 1MB): < 1 second
- Medium files (1-100MB): 1-30 seconds

### Text Merger
- Small merges (< 100 files): < 1 second
- Large merges (1000+ files): 10-60 seconds

## Troubleshooting

### Word Frequency Issues
```bash
# If analysis seems wrong, try case-sensitive
python word_frequency.py text.txt --case-sensitive

# If too many short words, set minimum length
python word_frequency.py text.txt --min-length 4

# If too many common words, use stop words
python word_frequency.py text.txt --remove-stop-words

# For code analysis, keep case and numbers
python word_frequency.py code.py --case-sensitive --include-numbers
```

### Encoding Issues
```bash
# Try different encodings for international text
python word_frequency.py text.txt --encoding latin-1
python word_frequency.py text.txt --encoding utf-16
```

### Memory Issues
```bash
# For very large files, increase minimum frequency
python word_frequency.py huge_file.txt --min-frequency 5

# Disable context storage for large corpora
python word_frequency.py big_data/ -r  # Don't use --contexts
```

## Coming Soon
- ✅ CSV to JSON/XML converter (COMPLETED)
- ✅ Markdown to HTML converter (COMPLETED)
- ✅ Text file merger with delimiters (COMPLETED)
- ✅ Word frequency analyzer (COMPLETED)
- [ ] Email extractor from text files
- [ ] N-gram analyzer (bigrams, trigrams)
- [ ] Sentiment analysis tool
- [ ] Text summarization
- [ ] Readability score calculator

## Dependencies
- `tqdm`: Progress bars
- `python-dateutil`: Date/time utilities
- `markdown`: Markdown parsing and conversion
- `Pygments`: Syntax highlighting for code blocks
