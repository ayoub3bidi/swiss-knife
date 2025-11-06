#!/usr/bin/env python3

import sys
import argparse
import json
import time
import socket
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse
import ssl
import http.client

try:
    import requests
    from requests.exceptions import RequestException, Timeout, ConnectionError
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: requests not installed. Run: pip install requests")

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class WebsiteChecker:
    
    def __init__(self,
                 timeout: int = 10,
                 verify_ssl: bool = True,
                 follow_redirects: bool = True,
                 user_agent: Optional[str] = None,
                 expected_status: List[int] = None,
                 check_ssl_expiry: bool = True,
                 ssl_warning_days: int = 30):
        """
        Args:
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
            follow_redirects: Follow HTTP redirects
            user_agent: Custom User-Agent header
            expected_status: List of expected HTTP status codes
            check_ssl_expiry: Check SSL certificate expiration
            ssl_warning_days: Warn if SSL expires within N days
        """
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects
        self.user_agent = user_agent or 'Website-Checker/1.0'
        self.expected_status = expected_status or [200, 201, 202, 203, 204]
        self.check_ssl_expiry = check_ssl_expiry
        self.ssl_warning_days = ssl_warning_days
        
        self.results: List[Dict] = []
        self.stats = {
            'total_checked': 0,
            'successful': 0,
            'failed': 0,
            'ssl_warnings': 0,
            'total_response_time': 0
        }
    
    def _get_ssl_info(self, hostname: str, port: int = 443) -> Optional[Dict]:
        """Get SSL certificate information."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse expiration date
                    not_after = cert.get('notAfter')
                    if not_after:
                        expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (expiry_date - datetime.now()).days
                    else:
                        expiry_date = None
                        days_until_expiry = None
                    
                    return {
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'version': cert.get('version'),
                        'serial_number': cert.get('serialNumber'),
                        'not_before': cert.get('notBefore'),
                        'not_after': not_after,
                        'expiry_date': expiry_date.isoformat() if expiry_date else None,
                        'days_until_expiry': days_until_expiry,
                        'expired': days_until_expiry < 0 if days_until_expiry is not None else None
                    }
        except Exception as e:
            return {'error': str(e)}
    
    def _check_url(self, url: str) -> Dict:
        """Check a single URL."""
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status': 'unknown',
            'status_code': None,
            'response_time': None,
            'error': None,
            'redirects': [],
            'ssl_info': None
        }
        
        if not HAS_REQUESTS:
            result['error'] = 'requests library not installed'
            result['status'] = 'error'
            return result
        
        # Parse URL
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f'https://{url}'
            parsed = urlparse(url)
        
        # Check SSL info if HTTPS
        if parsed.scheme == 'https' and self.check_ssl_expiry:
            hostname = parsed.hostname
            port = parsed.port or 443
            result['ssl_info'] = self._get_ssl_info(hostname, port)
            
            # Check for SSL warnings
            if result['ssl_info'] and 'days_until_expiry' in result['ssl_info']:
                days = result['ssl_info']['days_until_expiry']
                if days is not None and days <= self.ssl_warning_days:
                    self.stats['ssl_warnings'] += 1
        
        # Make HTTP request
        try:
            headers = {'User-Agent': self.user_agent}
            start_time = time.time()
            
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                allow_redirects=self.follow_redirects,
                headers=headers
            )
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            result['status_code'] = response.status_code
            result['response_time'] = round(response_time, 2)
            result['final_url'] = response.url
            
            # Track redirects
            if response.history:
                result['redirects'] = [
                    {'url': r.url, 'status_code': r.status_code}
                    for r in response.history
                ]
            
            # Determine status
            if response.status_code in self.expected_status:
                result['status'] = 'success'
                self.stats['successful'] += 1
            else:
                result['status'] = 'unexpected_status'
                result['error'] = f'Unexpected status code: {response.status_code}'
                self.stats['failed'] += 1
            
            self.stats['total_response_time'] += response_time
            
        except Timeout:
            result['status'] = 'timeout'
            result['error'] = f'Request timed out after {self.timeout}s'
            self.stats['failed'] += 1
        
        except ConnectionError as e:
            result['status'] = 'connection_error'
            result['error'] = f'Connection failed: {str(e)}'
            self.stats['failed'] += 1
        
        except RequestException as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.stats['failed'] += 1
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f'Unexpected error: {str(e)}'
            self.stats['failed'] += 1
        
        self.stats['total_checked'] += 1
        return result
    
    def check_urls(self, urls: List[str], delay: float = 0) -> List[Dict]:
        """Check multiple URLs."""
        self.results = []
        
        iterator = tqdm(urls, desc="Checking URLs", unit="url") if HAS_TQDM else urls
        
        for url in iterator:
            result = self._check_url(url)
            self.results.append(result)
            
            if delay > 0 and url != urls[-1]:
                time.sleep(delay)
        
        return self.results
    
    def check_urls_from_file(self, filepath: Path, delay: float = 0) -> List[Dict]:
        """Check URLs listed in a file (one per line)."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not urls:
                print(f"No URLs found in {filepath}")
                return []
            
            print(f"Loaded {len(urls)} URL(s) from {filepath}")
            return self.check_urls(urls, delay)
        
        except Exception as e:
            print(f"Error reading file: {e}")
            return []
    
    def print_results(self, verbose: bool = False):
        """Print check results."""
        print("\n" + "=" * 80)
        print("WEBSITE AVAILABILITY RESULTS")
        print("=" * 80)
        
        for result in self.results:
            status_icon = {
                'success': '✓',
                'timeout': '⏱',
                'connection_error': '✗',
                'unexpected_status': '⚠',
                'error': '✗',
                'unknown': '?'
            }.get(result['status'], '?')
            
            print(f"\n{status_icon} {result['url']}")
            
            if result['status_code']:
                print(f"  Status: {result['status_code']}")
            
            if result['response_time']:
                print(f"  Response Time: {result['response_time']:.2f}ms")
            
            if result.get('final_url') and result['final_url'] != result['url']:
                print(f"  Final URL: {result['final_url']}")
            
            if result.get('redirects'):
                print(f"  Redirects: {len(result['redirects'])}")
                if verbose:
                    for redirect in result['redirects']:
                        print(f"    → {redirect['url']} ({redirect['status_code']})")
            
            if result.get('ssl_info') and not result['ssl_info'].get('error'):
                ssl = result['ssl_info']
                if ssl.get('days_until_expiry') is not None:
                    days = ssl['days_until_expiry']
                    if days < 0:
                        print(f"  SSL: ⚠️  EXPIRED {abs(days)} days ago")
                    elif days <= self.ssl_warning_days:
                        print(f"  SSL: ⚠️  Expires in {days} days")
                    elif verbose:
                        print(f"  SSL: Valid ({days} days remaining)")
                
                if verbose and ssl.get('issuer'):
                    print(f"  SSL Issuer: {ssl['issuer'].get('organizationName', 'Unknown')}")
            
            if result['error']:
                print(f"  Error: {result['error']}")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total Checked:    {self.stats['total_checked']}")
        print(f"Successful:       {self.stats['successful']}")
        print(f"Failed:           {self.stats['failed']}")
        
        if self.stats['ssl_warnings'] > 0:
            print(f"SSL Warnings:     {self.stats['ssl_warnings']}")
        
        if self.stats['successful'] > 0:
            avg_time = self.stats['total_response_time'] / self.stats['successful']
            print(f"Avg Response:     {avg_time:.2f}ms")
        
        success_rate = (self.stats['successful'] / self.stats['total_checked'] * 100) if self.stats['total_checked'] > 0 else 0
        print(f"Success Rate:     {success_rate:.1f}%")
    
    def export_json(self, output_path: Path):
        """Export results to JSON."""
        data = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'results': self.results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults exported to: {output_path}")
    
    def export_csv(self, output_path: Path):
        """Export results to CSV."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'URL', 'Status', 'Status Code', 'Response Time (ms)',
                'SSL Days Until Expiry', 'Error', 'Timestamp'
            ])
            
            for result in self.results:
                ssl_days = None
                if result.get('ssl_info') and 'days_until_expiry' in result['ssl_info']:
                    ssl_days = result['ssl_info']['days_until_expiry']
                
                writer.writerow([
                    result['url'],
                    result['status'],
                    result['status_code'] or '',
                    result['response_time'] or '',
                    ssl_days if ssl_days is not None else '',
                    result['error'] or '',
                    result['timestamp']
                ])
        
        print(f"CSV exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Check website availability and monitor SSL certificates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check single URL
  python website_checker.py https://example.com
  
  # Check multiple URLs
  python website_checker.py https://google.com https://github.com https://stackoverflow.com
  
  # Check URLs from file
  python website_checker.py --file urls.txt
  
  # Export results to JSON
  python website_checker.py --file urls.txt --export-json results.json
  
  # Verbose output with SSL details
  python website_checker.py https://example.com --verbose
  
  # Custom timeout and disable SSL verification
  python website_checker.py https://example.com --timeout 30 --no-verify-ssl
  
  # Check with delay between requests
  python website_checker.py --file urls.txt --delay 2
  
  # Expect specific status codes
  python website_checker.py https://example.com --expected-status 200,301,302
"""
    )
    
    parser.add_argument('urls', nargs='*',
                       help='URLs to check')
    parser.add_argument('--file', '-f', type=Path,
                       help='File containing URLs (one per line)')
    
    parser.add_argument('--timeout', type=int, default=10,
                       help='Request timeout in seconds (default: 10)')
    parser.add_argument('--delay', type=float, default=0,
                       help='Delay between requests in seconds (default: 0)')
    parser.add_argument('--no-verify-ssl', dest='verify_ssl', action='store_false',
                       help='Disable SSL certificate verification')
    parser.add_argument('--no-redirects', dest='follow_redirects', action='store_false',
                       help='Don\'t follow HTTP redirects')
    parser.add_argument('--user-agent', type=str,
                       help='Custom User-Agent header')
    
    parser.add_argument('--expected-status', type=str,
                       help='Expected HTTP status codes (comma-separated)')
    parser.add_argument('--no-ssl-check', dest='check_ssl', action='store_false',
                       help='Disable SSL certificate expiry checking')
    parser.add_argument('--ssl-warning-days', type=int, default=30,
                       help='Warn if SSL expires within N days (default: 30)')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output with detailed information')
    parser.add_argument('--export-json', type=Path,
                       help='Export results to JSON file')
    parser.add_argument('--export-csv', type=Path,
                       help='Export results to CSV file')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.urls and not args.file:
        parser.error("Must provide URLs or --file")
    
    if not HAS_REQUESTS:
        print("Error: requests library required. Install: pip install requests")
        sys.exit(1)
    
    # Parse expected status codes
    expected_status = None
    if args.expected_status:
        try:
            expected_status = [int(s.strip()) for s in args.expected_status.split(',')]
        except ValueError:
            print("Error: Invalid status codes format")
            sys.exit(1)
    
    try:
        # Initialize checker
        checker = WebsiteChecker(
            timeout=args.timeout,
            verify_ssl=args.verify_ssl,
            follow_redirects=args.follow_redirects,
            user_agent=args.user_agent,
            expected_status=expected_status,
            check_ssl_expiry=args.check_ssl,
            ssl_warning_days=args.ssl_warning_days
        )
        
        # Check URLs
        if args.file:
            checker.check_urls_from_file(args.file, delay=args.delay)
        else:
            checker.check_urls(args.urls, delay=args.delay)
        
        # Print results
        checker.print_results(verbose=args.verbose)
        
        # Export
        if args.export_json:
            checker.export_json(args.export_json)
        
        if args.export_csv:
            checker.export_csv(args.export_csv)
        
        # Exit code based on results
        sys.exit(0 if checker.stats['failed'] == 0 else 1)
    
    except KeyboardInterrupt:
        print("\n\nCheck cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
