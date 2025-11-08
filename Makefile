install: ## Install all dependencies
	./$(VENV)/bin/pip install -r convert/requirements.txt
	./$(VENV)/bin/pip install -r file_management/requirements.txt
	./$(VENV)/bin/pip install -r text_processing/requirements.txt
	./$(VENV)/bin/pip install -r system_utilities/requirements.txt
	./$(VENV)/bin/pip install -r network_web/requirements.txt
	./$(VENV)/bin/pip install -r development_tools/requirements.txt
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
	@echo "  • QR generator: python network_web/qr_generator.py --url https://example.com -o qr.png"
	@echo "  • WiFi QR: python network_web/qr_generator.py --wifi --ssid Net --password pass -o wifi.png"
	@echo "  • Batch QR: python network_web/qr_generator.py --batch urls.txt --output-dir qr_codes/"
	@echo "  • Network scan: python network_web/network_scanner.py --network 192.168.1.0/24 --quick"
	@echo "  • Host scan: python network_web/network_scanner.py --host 192.168.1.1"
	@echo ""
	@echo "Run 'make validate-audio', 'make validate-files', 'make validate-text',"
	@echo "'make validate-network', or 'make validate-system' to check dependencies"

# Network/Web specific targets
network-demo: ## Show network/web usage examples
	@echo "Network/Web Tools Examples:"
	@echo "  Website Checker:"
	@echo "    Single URL:           python network_web/website_checker.py https://example.com"
	@echo "    Multiple URLs:        python network_web/website_checker.py https://google.com https://github.com"
	@echo "    From file:            python network_web/website_checker.py --file urls.txt"
	@echo "    Verbose SSL:          python network_web/website_checker.py https://example.com --verbose"
	@echo "    Export JSON:          python network_web/website_checker.py --file urls.txt --export-json report.json"
	@echo "    Custom timeout:       python network_web/website_checker.py https://example.com --timeout 30"
	@echo ""
	@echo "  QR Code Generator:"
	@echo "    URL:                  python network_web/qr_generator.py --url https://example.com -o qr.png"
	@echo "    WiFi:                 python network_web/qr_generator.py --wifi --ssid Net --password pass -o wifi.png"
	@echo "    Contact card:         python network_web/qr_generator.py --vcard --name 'John' --vcard-phone '+123' -o contact.png"
	@echo "    With label:           python network_web/qr_generator.py --url https://example.com -o qr.png --label 'Visit Us'"
	@echo "    Custom style:         python network_web/qr_generator.py --url https://example.com -o qr.png --style rounded"
	@echo "    Custom colors:        python network_web/qr_generator.py --url https://example.com -o qr.png --fill-color blue"
	@echo "    Batch from file:      python network_web/qr_generator.py --batch urls.txt --output-dir qr_codes/"
	@echo "    Batch from JSON:      python network_web/qr_generator.py --batch-json config.json --output-dir qr_codes/"
	@echo ""
	@echo "QR Styles: square, circle, rounded, vertical, horizontal, gapped"
	@echo "QR Types: url, text, wifi, vcard, email, sms, phone, geo"

test-network: ## Test network/web functionality  
	@echo "Testing network/web tools..."
	@$(VENV)/bin/python -c "from network_web.website_checker import WebsiteChecker; print('✓ Website checker imports OK')" || echo "✗ Website checker test failed"
	@$(VENV)/bin/python -c "from network_web.qr_generator import QRGenerator; print('✓ QR generator imports OK')" || echo "✗ QR generator test failed"
	@$(VENV)/bin/python -c "from network_web.network_scanner import NetworkScanner; print('✓ Network scanner imports OK')" || echo "✗ Network scanner test failed"

test-all: test-audio test-files test-text test-network test-system ## Run all functionality tests

# Add validate-system if not present
validate-system: ## Validate system utilities dependencies
	@echo "Checking system utilities dependencies..."
	@$(VENV)/bin/python -c "import psutil; print('✓ psutil installed')" 2>/dev/null || echo "✗ psutil missing"
	@$(VENV)/bin/python -c "import tqdm; print('✓ tqdm installed')" 2>/dev/null || echo "✗ tqdm missing"

test-system: ## Test system utilities functionality
	@echo "Testing system utilities tools..."
	@$(VENV)/bin/python -c "from system_utilities.system_monitor import ResourceMonitor; print('✓ System monitor imports OK')" || echo "✗ System utilities test failed"

# Development tools targets
dev-demo: ## Show development tools examples
	@echo "Development Tools Examples:"
	@echo "  Code Formatter:"
	@echo "    python development_tools/code_formatter.py src/ --recursive"
	@echo "    python development_tools/code_formatter.py . --check --recursive"
	@echo ""
	@echo "  License Header Injector:"
	@echo "    python development_tools/license_header_injector.py -l mit -a 'Your Name' src/ -r"
	@echo "    python development_tools/license_header_injector.py -l apache -a 'Company' . -r --update"
	@echo "    python development_tools/license_header_injector.py src/ --remove -r"

validate-dev: ## Validate development tools dependencies
	@echo "Checking development tools dependencies..."
	@$(VENV)/bin/python -c "import tqdm; print('✓ tqdm installed')" 2>/dev/null || echo "✗ tqdm missing"

test-dev: ## Test development tools functionality
	@echo "Testing development tools..."
	@$(VENV)/bin/python -c "from development_tools.code_formatter import CodeFormatter; print('✓ Code formatter imports OK')" || echo "✗ Code formatter test failed"
	@$(VENV)/bin/python -c "from development_tools.license_header_injector import LicenseHeaderInjector; print('✓ License injector imports OK')" || echo "✗ License injector test failed"
