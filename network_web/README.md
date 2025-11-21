# Network/Web Tools

Network and web utilities for monitoring, testing, and automation.

## Available Scripts

### Website Availability Checker (`website_checker.py`)
Monitor website availability, response times, SSL certificate expiration, and HTTP status codes.

**Features:**
- HTTP/HTTPS availability checking
- Response time measurement
- SSL certificate expiration monitoring
- Redirect tracking
- Custom User-Agent support
- Configurable timeout and retry logic
- Bulk URL checking from files
- JSON/CSV export for reporting
- Success rate statistics

### QR Code Generator (`qr_generator.py`)
Generate QR codes for URLs, WiFi credentials, contact cards, and various data types.

**Features:**
- Multiple QR code types (URL, WiFi, vCard, Email, SMS, Phone, Geo)
- 6 visual styles (square, circle, rounded, vertical bars, horizontal bars, gapped)
- Custom colors and error correction levels
- Text labels below QR codes
- Batch generation from text files or JSON
- High-resolution output
- Configurable size and border

### Local Network Scanner (`network_scanner.py`)
Discover devices, open ports, and services on local networks with concurrent scanning.

**Features:**
- Network range scanning (CIDR notation)
- Single host comprehensive scanning
- Port scanning with service detection
- Hostname and MAC address resolution
- Service banner grabbing
- Quick, full, and custom scan modes
- Concurrent multi-threaded scanning
- JSON/CSV export

## Installation

```bash
# Install dependencies
pip install -r network_web/requirements.txt

# Verify installation
python -c "import requests; print('✓ requests installed')"
```

## Quick Start

### QR Code Generator

```bash
# URL QR code
python network_web/qr_generator.py --url https://example.com -o qr.png

# WiFi credentials
python network_web/qr_generator.py --wifi --ssid MyNetwork --password pass123 -o wifi.png

# Contact card
python network_web/qr_generator.py --vcard --name "John Doe" --vcard-phone "+1234567890" -o contact.png

# Batch generation
python network_web/qr_generator.py --batch urls.txt --output-dir qr_codes/

# Network scanning
python network_web/network_scanner.py --network 192.168.1.0/24 --quick
python network_web/network_scanner.py --host 192.168.1.1 --port-range 1 1024
```

## Usage Examples

### Website Availability Checks

```bash
# Single site check
python website_checker.py https://example.com

# Multiple sites
python website_checker.py https://google.com https://github.com https://stackoverflow.com

# From URL list file (one per line)
python website_checker.py --file urls.txt
```

### SSL Certificate Monitoring

```bash
# Check SSL expiration (default: warn if < 30 days)
python website_checker.py https://example.com

# Custom warning threshold
python website_checker.py https://example.com --ssl-warning-days 60

# Verbose SSL details
python website_checker.py https://example.com --verbose

# Disable SSL checking
python website_checker.py https://example.com --no-ssl-check
```

### Custom Configuration

```bash
# Longer timeout for slow sites
python website_checker.py https://slow-site.com --timeout 30

# Disable SSL verification (for self-signed certs)
python website_checker.py https://internal.example.com --no-verify-ssl

# Custom User-Agent
python website_checker.py https://example.com --user-agent "MyBot/1.0"

# Don't follow redirects
python website_checker.py https://example.com --no-redirects

# Delay between requests (rate limiting)
python website_checker.py --file urls.txt --delay 2
```

### Expected Status Codes

```bash
# Accept specific status codes as success
python website_checker.py https://example.com --expected-status 200,301,302

# Check API endpoints (accept 200-204)
python website_checker.py https://api.example.com/health --expected-status 200,201,202,203,204
```

### Export and Reporting

```bash
# Export to JSON with full details
python website_checker.py --file urls.txt --export-json report.json

# Export to CSV for spreadsheets
python website_checker.py --file urls.txt --export-csv status.csv

# Both formats
python website_checker.py --file urls.txt --export-json report.json --export-csv status.csv

# Verbose output with SSL details
python website_checker.py --file urls.txt --verbose --export-json detailed_report.json
```

### Real-World Scenarios

#### Production Monitoring
```bash
# Monitor production sites with detailed reporting
python website_checker.py --file production_urls.txt \
  --timeout 15 \
  --ssl-warning-days 14 \
  --export-json monitoring_report.json \
  --verbose
```

#### API Health Checks
```bash
# Check API endpoints
python website_checker.py \
  https://api.example.com/health \
  https://api.example.com/status \
  --expected-status 200,204 \
  --timeout 5
```

#### SSL Certificate Audit
```bash
# Audit SSL certificates across domains
python website_checker.py --file domains.txt \
  --ssl-warning-days 60 \
  --export-csv ssl_audit.csv \
  --verbose
```

#### Rate-Limited Checking
```bash
# Check sites with delay to avoid rate limits
python website_checker.py --file urls.txt \
  --delay 3 \
  --timeout 20 \
  --export-json results.json
```

#### CI/CD Integration
```bash
# Check deployment URLs (exits with error code if any fail)
python website_checker.py \
  https://staging.example.com \
  https://production.example.com \
  --expected-status 200 \
  --timeout 10

# Use exit code in scripts
if python website_checker.py --file critical_urls.txt; then
  echo "All sites available"
else
  echo "Some sites failed" >&2
  exit 1
fi
```

### URL List File Format

Create a text file with URLs (one per line):

```text
# Production Sites
https://example.com
https://www.example.com
https://api.example.com

# Staging
https://staging.example.com

# External Dependencies
https://cdn.example.com
https://analytics.example.com
```

Comments (lines starting with `#`) are ignored.

### QR Code Generator

#### Basic QR Codes

```bash
# URL
python qr_generator.py --url https://example.com -o url_qr.png

# Plain text
python qr_generator.py --text "Hello World" -o text_qr.png

# URL with label
python qr_generator.py --url https://example.com -o qr.png --label "Visit our website"
```

#### WiFi QR Codes

```bash
# WPA/WPA2 network
python qr_generator.py --wifi --ssid MyNetwork --password mypass123 -o wifi.png

# WEP network
python qr_generator.py --wifi --ssid OldNetwork --password pass --security WEP -o wifi_wep.png

# Hidden network
python qr_generator.py --wifi --ssid HiddenNet --password secret --hidden -o hidden_wifi.png

# Open network (no password)
python qr_generator.py --wifi --ssid FreeWiFi --password "" --security nopass -o open_wifi.png
```

#### Contact Cards (vCard)

```bash
# Basic contact
python qr_generator.py --vcard --name "John Doe" --vcard-phone "+1234567890" -o contact.png

# Full contact with all fields
python qr_generator.py --vcard \
  --name "Jane Smith" \
  --vcard-phone "+1234567890" \
  --vcard-email jane@example.com \
  --organization "Acme Corp" \
  --vcard-url https://example.com \
  -o full_contact.png
```

#### Communication QR Codes

```bash
# Email (opens email client)
python qr_generator.py --email contact@example.com -o email.png

# Email with subject and body
python qr_generator.py --email support@example.com \
  --subject "Support Request" \
  --body "I need help with..." \
  -o email_prefilled.png

# Phone call
python qr_generator.py --phone "+1234567890" -o phone.png

# SMS
python qr_generator.py --sms "+1234567890" -o sms.png

# SMS with message
python qr_generator.py --sms "+1234567890" --message "Hello from QR" -o sms_msg.png
```

#### Geolocation QR Codes

```bash
# Specific coordinates
python qr_generator.py --geo 40.7128 -74.0060 -o nyc_location.png

# With label
python qr_generator.py --geo 51.5074 -0.1278 --label "London" -o london.png
```

#### Custom Styling

```bash
# Different styles
python qr_generator.py --url https://example.com -o square.png --style square
python qr_generator.py --url https://example.com -o circle.png --style circle
python qr_generator.py --url https://example.com -o rounded.png --style rounded
python qr_generator.py --url https://example.com -o vertical.png --style vertical
python qr_generator.py --url https://example.com -o horizontal.png --style horizontal
python qr_generator.py --url https://example.com -o gapped.png --style gapped

# Custom colors
python qr_generator.py --url https://example.com -o blue_qr.png \
  --fill-color blue --back-color white

# Hex colors
python qr_generator.py --url https://example.com -o custom_qr.png \
  --fill-color "#FF5733" --back-color "#FFFFFF"

# Larger QR code
python qr_generator.py --url https://example.com -o large_qr.png --box-size 15 --border 2

# High error correction (for damaged/partially obscured codes)
python qr_generator.py --url https://example.com -o robust_qr.png --error-correction H
```

#### Batch Generation

**From text file** (urls.txt):
```text
https://example.com
https://github.com
https://stackoverflow.com
```

```bash
python qr_generator.py --batch urls.txt --output-dir qr_codes/
```

**From JSON file** (config.json):
```json
[
  {
    "type": "url",
    "data": "https://example.com",
    "output": "website.png",
    "label": "Visit Us"
  },
  {
    "type": "wifi",
    "ssid": "MyNetwork",
    "password": "password123",
    "security": "WPA",
    "output": "wifi_guest.png",
    "label": "Guest WiFi"
  },
  {
    "type": "vcard",
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john@example.com",
    "output": "john_contact.png"
  },
  {
    "type": "email",
    "email": "support@example.com",
    "subject": "Feedback",
    "output": "feedback.png",
    "label": "Send Feedback"
  }
]
```

```bash
python qr_generator.py --batch-json config.json --output-dir qr_codes/
```

#### Real-World Scenarios

**Restaurant Menu:**
```bash
python qr_generator.py --url https://restaurant.com/menu -o menu_qr.png \
  --style rounded --label "View Menu" --box-size 12
```

**Event WiFi:**
```bash
python qr_generator.py --wifi --ssid "EventWiFi" --password "welcome2024" \
  -o event_wifi.png --label "Free WiFi" --style circle
```

**Business Card:**
```bash
python qr_generator.py --vcard \
  --name "Alice Johnson" \
  --vcard-phone "+1234567890" \
  --vcard-email alice@company.com \
  --organization "Tech Corp" \
  --vcard-url https://company.com \
  -o business_card.png --style rounded --fill-color "#2C3E50"
```

**Product Links (batch):**
```bash
# products.txt
https://shop.com/product/123
https://shop.com/product/456
https://shop.com/product/789

python qr_generator.py --batch products.txt --output-dir product_qr/ \
  --style rounded --fill-color blue
```

**App Download Links:**
```bash
python qr_generator.py --url https://play.google.com/store/apps/details?id=com.app \
  -o android_qr.png --label "Download on Google Play"

python qr_generator.py --url https://apps.apple.com/app/id123456 \
  -o ios_qr.png --label "Download on App Store"
```

### Local Network Scanner

#### Quick Network Discovery

```bash
# Quick scan (common ports only)
python network_scanner.py --network 192.168.1.0/24 --quick

# Quick scan with JSON export
python network_scanner.py --network 192.168.1.0/24 --quick --export-json scan.json

# Only show hosts with open ports
python network_scanner.py --network 192.168.1.0/24 --quick --only-alive
```

#### Comprehensive Scanning

```bash
# Full scan with all common ports
python network_scanner.py --network 192.168.1.0/24 --full

# Full scan with service banners
python network_scanner.py --network 192.168.1.0/24 --full --banners --verbose

# Scan specific ports
python network_scanner.py --network 192.168.1.0/24 --ports 22,80,443,3306,5432

# Scan port range
python network_scanner.py --network 192.168.1.0/24 --ports 8000-9000
```

#### Single Host Scanning

```bash
# Scan all ports 1-1024 on single host
python network_scanner.py --host 192.168.1.1

# Scan all ports (1-65535)
python network_scanner.py --host 192.168.1.1 --port-range 1 65535

# Scan with banners
python network_scanner.py --host 192.168.1.1 --banners --verbose

# Quick check specific host
python network_scanner.py --host 192.168.1.100 --port-range 80 80
```

#### Performance Tuning

```bash
# Fast scan (more threads, shorter timeout)
python network_scanner.py --network 192.168.1.0/24 --quick --workers 200 --timeout 0.5

# Slow but thorough
python network_scanner.py --network 192.168.1.0/24 --full --workers 50 --timeout 3.0

# Custom timeouts
python network_scanner.py --network 192.168.1.0/24 --quick --timeout 2.0 --ping-timeout 2.0
```

#### Output Options

```bash
# Export to JSON
python network_scanner.py --network 192.168.1.0/24 --quick --export-json results.json

# Export to CSV
python network_scanner.py --network 192.168.1.0/24 --full --export-csv scan.csv

# Both formats
python network_scanner.py --network 192.168.1.0/24 --full --export-json scan.json --export-csv scan.csv

# Minimal output (skip hostname/MAC lookup)
python network_scanner.py --network 192.168.1.0/24 --quick --no-hostname --no-mac
```

#### Real-World Scenarios

**Home Network Audit:**
```bash
python network_scanner.py --network 192.168.1.0/24 --full --export-json home_scan.json
```

**Find All Web Servers:**
```bash
python network_scanner.py --network 192.168.1.0/24 --ports 80,443,8080,8443 --only-alive
```

**Database Server Discovery:**
```bash
python network_scanner.py --network 10.0.0.0/24 --ports 3306,5432,27017,6379 --banners
```

**Security Audit (common vulnerable ports):**
```bash
python network_scanner.py --network 192.168.1.0/24 --ports 21,23,445,3389 --banners
```

**IoT Device Discovery:**
```bash
python network_scanner.py --network 192.168.1.0/24 --ports 80,443,554,8080 --banners --verbose
```

**Check if specific service is running:**
```bash
python network_scanner.py --network 192.168.1.0/24 --ports 22 --only-alive
```

### Output Examples

**Network Scanner Console Output:**
```
Scanning 254 host(s) on 192.168.1.0/24
Checking 8 port(s) per host
Workers: 100, Timeout: 1.0s
Scanning: 100%|████████████████| 254/254 [00:12<00:00, 20.33host/s]

================================================================================
NETWORK SCAN RESULTS
================================================================================

📍 192.168.1.1 (router.local)
   MAC: aa:bb:cc:dd:ee:ff
   Open Ports: 2
         80/tcp  HTTP
        443/tcp  HTTPS

📍 192.168.1.100 (desktop.local)
   MAC: 11:22:33:44:55:66
   Open Ports: 1
         22/tcp  SSH

================================================================================
SUMMARY
================================================================================
Hosts Scanned:    254
Hosts Alive:      5
Ports Scanned:    2,032
Ports Open:       8
Duration:         12.45s
```

## Output Format

### Console Output
```
================================================================================
WEBSITE AVAILABILITY RESULTS
================================================================================

✓ https://example.com
  Status: 200
  Response Time: 145.23ms
  SSL: Valid (365 days remaining)

⚠ https://expired-ssl.example.com
  Status: 200
  Response Time: 234.56ms
  SSL: ⚠️  Expires in 15 days

✗ https://down-site.example.com
  Error: Connection failed: [Errno 111] Connection refused

================================================================================
SUMMARY
================================================================================
Total Checked:    3
Successful:       2
Failed:           1
SSL Warnings:     1
Avg Response:     189.90ms
Success Rate:     66.7%
```

### JSON Export Structure
```json
{
  "timestamp": "2025-11-05T10:30:00",
  "statistics": {
    "total_checked": 3,
    "successful": 2,
    "failed": 1,
    "ssl_warnings": 1,
    "total_response_time": 379.79
  },
  "results": [
    {
      "url": "https://example.com",
      "timestamp": "2025-11-05T10:30:00",
      "status": "success",
      "status_code": 200,
      "response_time": 145.23,
      "ssl_info": {
        "days_until_expiry": 365,
        "expired": false,
        "issuer": {...}
      }
    }
  ]
}
```

## Performance

- **Small checks** (< 10 URLs): < 10 seconds
- **Medium checks** (10-100 URLs): 10-60 seconds
- **Large checks** (100+ URLs): 1-10 minutes

Response time depends on:
- Network latency
- Server response speed
- Timeout settings
- Delay between requests

## Security Notes

- By default, SSL certificates are verified
- Use `--no-verify-ssl` only for trusted internal sites
- SSL certificate details are not logged in verbose mode
- No sensitive data is stored or transmitted

## Troubleshooting

### SSL Certificate Errors
```bash
# For self-signed certificates
python website_checker.py https://internal.example.com --no-verify-ssl

# Check what's wrong with SSL
python website_checker.py https://example.com --verbose
```

### Timeout Issues
```bash
# Increase timeout for slow sites
python website_checker.py https://slow-site.com --timeout 60

# Check without redirects (faster)
python website_checker.py https://example.com --no-redirects
```

### Rate Limiting
```bash
# Add delay between requests
python website_checker.py --file urls.txt --delay 5

# Use custom User-Agent
python website_checker.py --file urls.txt --user-agent "MyMonitor/1.0"
```
