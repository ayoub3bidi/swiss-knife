# Network/Web Tools

Network and web utilities for monitoring, testing, and automation.

## Available Scripts

### 🌐 Website Availability Checker (`website_checker.py`)
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

## Installation

```bash
# Install dependencies
pip install -r network_web/requirements.txt

# Verify installation
python -c "import requests; print('✓ requests installed')"
```

## Quick Start

### Website Checker

```bash
# Check single URL
python network_web/website_checker.py https://example.com

# Check multiple URLs
python network_web/website_checker.py https://google.com https://github.com

# Check from file
python network_web/website_checker.py --file urls.txt

# Export results
python network_web/website_checker.py --file urls.txt --export-json results.json
```

## Usage Examples

### Basic Availability Checks

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

## Coming Soon
- ✅ Website availability checker (COMPLETED)
- [ ] Bulk URL shortener with custom domains
- [ ] QR code generator for URLs/text
- [ ] Local network scanner and port checker
- [ ] DNS lookup and propagation checker
- [ ] HTTP header analyzer
- [ ] Website screenshot capture

## Dependencies
- `requests`: HTTP library for making web requests
- `tqdm`: Progress bars for bulk operations
- `urllib3`: HTTP client (included with requests)
