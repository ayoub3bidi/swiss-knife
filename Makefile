install: ## Install all dependencies
	./$(VENV)/bin/pip install -r convert/requirements.txt
	./$(VENV)/bin/pip install -r file_management/requirements.txt
	./$(VENV)/bin/pip install -r text_processing/requirements.txt
	./$(VENV)/bin/pip install -r system_utilities/requirements.txt
	./$(VENV)/bin/pip install -r network_web/requirements.txt
	./$(VENV)/bin/pip install -r automation/requirements.txt || true
	./$(VENV)/bin/pip install -r utilities/requirements.txt || true

validate-network: ## Validate network/web dependencies
	@echo "Checking network/web dependencies..."
	@$(VENV)/bin/python -c "import requests; print('✓ requests installed')" 2>/dev/null || echo "✗ requests missing"
	@$(VENV)/bin/python -c "import urllib3; print('✓ urllib3 installed')" 2>/dev/null || echo "✗ urllib3 missing"
	@$(VENV)/bin/python -c "import tqdm; print('✓ tqdm installed')" 2>/dev/null || echo "✗ tqdm missing"
	@$(VENV)/bin/python -c "import certifi; print('✓ certifi installed')" 2>/dev/null || echo "✗ certifi missing"
	@$(VENV)/bin/python -c "import qrcode; print('✓ qrcode installed')" 2>/dev/null || echo "✗ qrcode missing"
	@$(VENV)/bin/python -c "from PIL import Image; print('✓ Pillow installed')" 2>/dev/null || echo "✗ Pillow missing"
	@$(VENV)/bin/python -c "import ssl; print('✓ ssl available')"

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
	@echo "  • Word frequency: python text_processing/word_frequency.py document.txt"
	@echo ""
	@echo "System Utilities:"
	@echo "  • System monitor: python system_utilities/system_monitor.py"
	@echo "  • Process killer: python system_utilities/process_killer.py --min-memory 1024 --dry-run"
	@echo "  • Disk analyzer: python system_utilities/disk_analyzer.py ~/Documents"
	@echo ""
	@echo "Network/Web Tools:"
	@echo "  • Website checker: python network_web/website_checker.py https://example.com"
	@echo "  • Bulk URL check: python network_web/website_checker.py --file urls.txt"
	@echo "  • SSL monitoring: python network_web/website_checker.py --file urls.txt --ssl-warning-days 30"
	@echo ""
	@echo "Run 'make validate-audio', 'make validate-files', 'make validate-text',"
	@echo "'make validate-network', or 'make validate-system' to check dependencies"

# Network/Web specific targets
network-demo: ## Show network/web usage examples
	@echo "Network/Web Tools Examples:"
	@echo "  Single URL check:       python network_web/website_checker.py https://example.com"
	@echo "  Multiple URLs:          python network_web/website_checker.py https://google.com https://github.com"
	@echo "  From file:              python network_web/website_checker.py --file urls.txt"
	@echo "  Verbose SSL info:       python network_web/website_checker.py https://example.com --verbose"
	@echo "  Export JSON:            python network_web/website_checker.py --file urls.txt --export-json report.json"
	@echo "  Export CSV:             python network_web/website_checker.py --file urls.txt --export-csv status.csv"
	@echo "  Custom timeout:         python network_web/website_checker.py https://example.com --timeout 30"
	@echo "  Disable SSL verify:     python network_web/website_checker.py https://internal.com --no-verify-ssl"
	@echo "  Rate limiting:          python network_web/website_checker.py --file urls.txt --delay 2"
	@echo "  Expected status:        python network_web/website_checker.py https://example.com --expected-status 200,301"
	@echo "  SSL expiry warning:     python network_web/website_checker.py --file urls.txt --ssl-warning-days 60"
	@echo ""
	@echo "URL file format: One URL per line, comments start with #"

test-network: ## Test network/web functionality  
	@echo "Testing network/web tools..."
	@$(VENV)/bin/python -c "from network_web.website_checker import WebsiteChecker; print('✓ Website checker imports OK')" || echo "✗ Network/web test failed"

test-all: test-audio test-files test-text test-network test-system ## Run all functionality tests

# Add validate-system if not present
validate-system: ## Validate system utilities dependencies
	@echo "Checking system utilities dependencies..."
	@$(VENV)/bin/python -c "import psutil; print('✓ psutil installed')" 2>/dev/null || echo "✗ psutil missing"
	@$(VENV)/bin/python -c "import tqdm; print('✓ tqdm installed')" 2>/dev/null || echo "✗ tqdm missing"

test-system: ## Test system utilities functionality
	@echo "Testing system utilities tools..."
	@$(VENV)/bin/python -c "from system_utilities.system_monitor import ResourceMonitor; print('✓ System monitor imports OK')" || echo "✗ System utilities test failed"
