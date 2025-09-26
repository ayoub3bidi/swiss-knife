# Default Python version
PYTHON := python3
VENV := venv
SCRIPTS_DIR := .

.PHONY: help setup install test clean lint format demo validate-audio

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	./$(VENV)/bin/pip install --upgrade pip

install: ## Install all dependencies
	./$(VENV)/bin/pip install -r convert/requirements.txt
	./$(VENV)/bin/pip install -r automation/requirements.txt || true
	./$(VENV)/bin/pip install -r utilities/requirements.txt || true

test: ## Run all tests and validation
	@echo "Validating Python syntax..."
	find . -name "*.py" -exec $(PYTHON) -m py_compile {} \;
	@echo "Testing audio converter imports..."
	$(VENV)/bin/python -c "from pydub import AudioSegment; print('✓ Audio dependencies OK')"

validate-audio: ## Validate audio conversion dependencies
	@echo "Checking audio format support..."
	@$(VENV)/bin/python -c "import pydub.utils; print('✓ pydub installed')" 2>/dev/null || echo "✗ pydub missing"
	@$(VENV)/bin/python -c "import numpy; print('✓ numpy installed')" 2>/dev/null || echo "✗ numpy missing"
	@$(VENV)/bin/python -c "import tqdm; print('✓ tqdm installed')" 2>/dev/null || echo "✗ tqdm missing"
	@which ffmpeg > /dev/null && echo "✓ FFmpeg found" || echo "✗ FFmpeg not found (recommended for best format support)"

demo: ## Run demonstration of audio conversion tools
	@echo "Sacred Scripts Audio Conversion Demo"
	@echo "===================================="
	@echo "Available converters:"
	@echo "  • WAV to MP3: python convert/wav_to_mp3.py <file.wav>"
	@echo "  • Audio visualization: python convert/sound_to_video.py <audio_file>"
	@echo "  • Batch converter: python convert/batch_audio_converter.py --format mp3 *.wav"
	@echo ""
	@echo "Run 'make validate-audio' to check audio dependencies"

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

install-ffmpeg: ## Install FFmpeg (Ubuntu/Debian)
	@echo "Installing FFmpeg for enhanced audio format support..."
	@which apt-get > /dev/null && sudo apt-get update && sudo apt-get install -y ffmpeg || echo "Please install FFmpeg manually for your system"
