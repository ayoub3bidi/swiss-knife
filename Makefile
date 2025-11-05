# Default Python version
PYTHON := python3
VENV := venv
SCRIPTS_DIR := .

.PHONY: help setup install test clean lint format demo validate-audio validate-files

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	./$(VENV)/bin/pip install --upgrade pip

install: ## Install all dependencies
	./$(VENV)/bin/pip install -r convert/requirements.txt
	./$(VENV)/bin/pip install -r file_management/requirements.txt
	./$(VENV)/bin/pip install -r text_processing/requirements.txt
	./$(VENV)/bin/pip install -r automation/requirements.txt || true
	./$(VENV)/bin/pip install -r utilities/requirements.txt || true
	./$(VENV)/bin/pip install -r system_utilities/requirements.txt || true

test: ## Run all tests and validation
	@echo "Validating Python syntax..."
	find . -name "*.py" -exec $(PYTHON) -m py_compile {} \;
	@echo "Testing audio converter imports..."
	$(VENV)/bin/python -c "from pydub import AudioSegment; print('✓ Audio dependencies OK')"
	@echo "Testing file management imports..."
	$(VENV)/bin/python -c "import tqdm, hashlib; print('✓ File management dependencies OK')"
	@echo "Testing text processing imports..."
	$(VENV)/bin/python -c "import csv, json; print('✓ Text processing dependencies OK')"

validate-audio: ## Validate audio conversion dependencies
	@echo "Checking audio format support..."
	@$(VENV)/bin/python -c "import pydub.utils; print('✓ pydub installed')" 2>/dev/null || echo "✗ pydub missing"
	@$(VENV)/bin/python -c "import numpy; print('✓ numpy installed')" 2>/dev/null || echo "✗ numpy missing"
	@$(VENV)/bin/python -c "import tqdm; print('✓ tqdm installed')" 2>/dev/null || echo "✗ tqdm missing"
	@which ffmpeg > /dev/null && echo "✓ FFmpeg found" || echo "✗ FFmpeg not found (recommended for best format support)"

validate-files: ## Validate file management dependencies
	@echo "Checking file management dependencies..."
	@$(VENV)/bin/python -c "import tqdm; print('✓ tqdm installed')" 2>/dev/null || echo "✗ tqdm missing"
	@$(VENV)/bin/python -c "import send2trash; print('✓ send2trash installed')" 2>/dev/null || echo "✗ send2trash missing"
	@$(VENV)/bin/python -c "import xxhash; print('✓ xxhash installed')" 2>/dev/null || echo "✗ xxhash missing (optional)"
	@$(VENV)/bin/python -c "import hashlib; print('✓ hashlib available')"

validate-text: ## Validate text processing dependencies
	@echo "Checking text processing dependencies..."
	@$(VENV)/bin/python -c "import csv; print('✓ csv available')"
	@$(VENV)/bin/python -c "import json; print('✓ json available')"
	@$(VENV)/bin/python -c "import xml.etree.ElementTree; print('✓ xml available')"
	@$(VENV)/bin/python -c "import tqdm; print('✓ tqdm installed')" 2>/dev/null || echo "✗ tqdm missing"
	@$(VENV)/bin/python -c "import markdown; print('✓ markdown installed')" 2>/dev/null || echo "✗ markdown missing"

demo: ## Run demonstration of available tools
	@echo "Sacred Scripts Automation Tools Demo"
	@echo "===================================="
	@echo ""
	@echo "Audio/Video Processing:"
	@echo "  • WAV to MP3: python convert/wav_to_mp3.py <file.wav>"
	@echo "  • Audio visualization: python convert/sound_to_video.py <audio_file>"
	@echo "  • Batch converter: python convert/batch_audio_converter.py --format mp3 *.wav"
	@echo "  • Image converter: python convert/batch_image_converter.py --format jpeg *.png"
	@echo ""
	@echo "File Management:"
	@echo "  • Duplicate finder: python file_management/duplicate_finder.py /path/to/search"
	@echo "  • Bulk renamer: python file_management/bulk_renamer.py '\\s+' '_' ~/Documents"
	@echo "  • Broken symlinks: python file_management/broken_symlinks.py ~/Projects"
	@echo ""
	@echo "Text Processing:"
	@echo "  • CSV to JSON: python text_processing/csv_converter.py data.csv -f json"
	@echo "  • CSV to XML: python text_processing/csv_converter.py data.csv -f xml"
	@echo "  • Markdown to HTML: python text_processing/markdown_converter.py README.md"
	@echo "  • Text merger: python text_processing/text_merger.py *.txt -o merged.txt"
	@echo ""
	@echo "System Utilities:"
	@echo "  • System monitor: python system_utilities/system_monitor.py"
	@echo "  • Process killer: python system_utilities/process_killer.py --min-memory 1024 --dry-run"
	@echo "  • Disk analyzer: python system_utilities/disk_analyzer.py ~/Documents"
	@echo ""
	@echo "Run 'make validate-audio', 'make validate-files', or 'make validate-text' to check dependencies"

lint: ## Lint all Python files
	./$(VENV)/bin/python -m flake8 --max-line-length=100 --exclude=$(VENV) . || echo "flake8 not installed, skipping lint"

format: ## Format Python files with black
	./$(VENV)/bin/python -m black --line-length=100 . || echo "black not installed, skipping format"

clean: ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "temp_*.mp4" -delete
	find . -type f -name "temp_audio_conversion.wav" -delete
	rm -rf $(VENV)
	rm -rf dist/
	rm -rf build/

install-dev: ## Install development dependencies
	./$(VENV)/bin/pip install flake8 black pytest

package: ## Create distribution package
	mkdir -p dist/
	tar -czf dist/sacred-scripts.tar.gz \
		--exclude='.git' \
		--exclude='venv' \
		--exclude='*.pyc' \
		--exclude='__pycache__' \
		--exclude='temp_*' \
		.

# Audio-specific targets
convert-demo: ## Show batch converter usage examples
	@echo "Batch Audio Converter Examples:"
	@echo "  Convert WAV to MP3:     python convert/batch_audio_converter.py --format mp3 *.wav"
	@echo "  High-quality FLAC:     python convert/batch_audio_converter.py --format flac --quality high ~/Music/"
	@echo "  Parallel processing:   python convert/batch_audio_converter.py --format mp3 --workers 8 audio/"
	@echo "  Custom output dir:     python convert/batch_audio_converter.py --format ogg --output ./converted *.mp3"
	@echo ""
	@echo "Quality options: low, medium, high, lossless"
	@echo "Formats: mp3, wav, ogg, flac"

# File management specific targets  
files-demo: ## Show file management usage examples
	@echo "File Management Examples:"
	@echo "  Find duplicates:        python file_management/duplicate_finder.py ~/Documents"
	@echo "  Large files only:       python file_management/duplicate_finder.py --min-size 10MB ~/Videos"
	@echo "  Image duplicates:       python file_management/duplicate_finder.py --extensions jpg,png,gif ~/Pictures"
	@echo "  Export to JSON:         python file_management/duplicate_finder.py --output json --file report.json ~/Data"
	@echo "  Safe removal (dry-run): python file_management/duplicate_finder.py --delete-duplicates --dry-run ~/temp"
	@echo "  Delete duplicates:      python file_management/duplicate_finder.py --delete-duplicates --keep-strategy shortest_name ~/temp"
	@echo ""
	@echo "Hash algorithms: md5, sha1, sha256, sha512"
	@echo "Keep strategies: first, last, shortest_name, longest_name"

# Text processing specific targets
text-demo: ## Show text processing usage examples
	@echo "Text Processing Examples:"
	@echo "  CSV to JSON:            python text_processing/csv_converter.py data.csv -f json"
	@echo "  CSV to XML:             python text_processing/csv_converter.py data.csv -f xml"
	@echo "  Markdown to HTML:       python text_processing/markdown_converter.py README.md"
	@echo "  Merge text files:       python text_processing/text_merger.py *.txt -o merged.txt"
	@echo "  Merge with timestamps:  python text_processing/text_merger.py logs/*.log -o combined.log --timestamp"
	@echo "  Merge with line nums:   python text_processing/text_merger.py *.py -o all_code.py --line-numbers"
	@echo "  Word frequency:         python text_processing/word_frequency.py document.txt"
	@echo "  Frequency with stops:   python text_processing/word_frequency.py article.txt --remove-stop-words --top 30"
	@echo "  Analyze directory:      python text_processing/word_frequency.py docs/ -r --ext txt,md --contexts"
	@echo "  Custom delimiter:       python text_processing/csv_converter.py data.tsv -f json -d 

# System utilities specific targets
system-demo: ## Show system utilities usage examples
	@echo "System Utilities Examples:"
	@echo "  Monitor system:         python system_utilities/system_monitor.py"
	@echo "  Quick status:           python system_utilities/system_monitor.py --once"
	@echo "  Kill memory hogs:       python system_utilities/process_killer.py --min-memory 1024 --dry-run"
	@echo "  Analyze disk:           python system_utilities/disk_analyzer.py ~/Documents"
	@echo "  Export report:          python system_utilities/system_monitor.py --export-report report.json"

install-ffmpeg: ## Install FFmpeg (Ubuntu/Debian)
	@echo "Installing FFmpeg for enhanced audio format support..."
	@which apt-get > /dev/null && sudo apt-get update && sudo apt-get install -y ffmpeg || echo "Please install FFmpeg manually for your system"

# System utilities
install-system-deps: ## Install system dependencies (Ubuntu/Debian)
	@echo "Installing system dependencies..."
	@which apt-get > /dev/null && sudo apt-get update && sudo apt-get install -y ffmpeg python3-dev || echo "Please install system dependencies manually"

# Testing targets
test-audio: ## Test audio conversion functionality
	@echo "Testing audio conversion tools..."
	@$(VENV)/bin/python -c "from convert.batch_audio_converter import AudioConverter; print('✓ Audio converter imports OK')" || echo "✗ Audio converter test failed"

test-files: ## Test file management functionality  
	@echo "Testing file management tools..."
	@$(VENV)/bin/python -c "from file_management.duplicate_finder import DuplicateFinder; print('✓ Duplicate finder imports OK')" || echo "✗ File management test failed"

test-text: ## Test text processing functionality
	@echo "Testing text processing tools..."
	@$(VENV)/bin/python -c "from text_processing.csv_converter import CSVConverter; print('✓ CSV converter imports OK')" || echo "✗ Text processing test failed"

test-all: test-audio test-files test-text ## Run all functionality tests
\\t'"
	@echo "  Compact JSON:           python text_processing/csv_converter.py data.csv -f json --no-pretty"
	@echo "  MD with theme:          python text_processing/markdown_converter.py doc.md --theme monokai"
	@echo "  Batch MD conversion:    python text_processing/markdown_converter.py docs/ -o html/ --recursive"
	@echo ""
	@echo "CSV formats: json, xml"
	@echo "MD themes: default, github, monokai, dracula, solarized-dark, solarized-light"
	@echo "Merger delimiters: line, double, hash, star, dash, blank, minimal, section"

# System utilities specific targets
system-demo: ## Show system utilities usage examples
	@echo "System Utilities Examples:"
	@echo "  Monitor system:         python system_utilities/system_monitor.py"
	@echo "  Quick status:           python system_utilities/system_monitor.py --once"
	@echo "  Kill memory hogs:       python system_utilities/process_killer.py --min-memory 1024 --dry-run"
	@echo "  Analyze disk:           python system_utilities/disk_analyzer.py ~/Documents"
	@echo "  Export report:          python system_utilities/system_monitor.py --export-report report.json"

install-ffmpeg: ## Install FFmpeg (Ubuntu/Debian)
	@echo "Installing FFmpeg for enhanced audio format support..."
	@which apt-get > /dev/null && sudo apt-get update && sudo apt-get install -y ffmpeg || echo "Please install FFmpeg manually for your system"

# System utilities
install-system-deps: ## Install system dependencies (Ubuntu/Debian)
	@echo "Installing system dependencies..."
	@which apt-get > /dev/null && sudo apt-get update && sudo apt-get install -y ffmpeg python3-dev || echo "Please install system dependencies manually"

# Testing targets
test-audio: ## Test audio conversion functionality
	@echo "Testing audio conversion tools..."
	@$(VENV)/bin/python -c "from convert.batch_audio_converter import AudioConverter; print('✓ Audio converter imports OK')" || echo "✗ Audio converter test failed"

test-files: ## Test file management functionality  
	@echo "Testing file management tools..."
	@$(VENV)/bin/python -c "from file_management.duplicate_finder import DuplicateFinder; print('✓ Duplicate finder imports OK')" || echo "✗ File management test failed"

test-text: ## Test text processing functionality
	@echo "Testing text processing tools..."
	@$(VENV)/bin/python -c "from text_processing.csv_converter import CSVConverter; print('✓ CSV converter imports OK')" || echo "✗ Text processing test failed"

test-all: test-audio test-files test-text ## Run all functionality tests
