#!/usr/bin/env python3

import sys
import argparse
import socket
import json
import ipaddress
import platform
import subprocess
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import struct

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class NetworkScanner:
    
    # Common ports and services
    COMMON_PORTS = {
        20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
        25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3',
        143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 3306: 'MySQL',
        3389: 'RDP', 5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis',
        8080: 'HTTP-Alt', 8443: 'HTTPS-Alt', 27017: 'MongoDB'
    }
    
    def __init__(self,
                 timeout: float = 1.0,
                 max_workers: int = 100,
                 ping_timeout: float = 1.0):
        """
        Args:
            timeout: Socket connection timeout
            max_workers: Thread pool size
            ping_timeout: Ping timeout in seconds
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.ping_timeout = ping_timeout
        
        self.stats = {
            'hosts_scanned': 0,
            'hosts_alive': 0,
            'ports_scanned': 0,
            'ports_open': 0,
            'scan_start': None,
            'scan_end': None
        }
        
        self.discovered_hosts: List[Dict] = []
    
    def _ping_host(self, ip: str) -> bool:
        """Check if host is alive using ping."""
        try:
            system = platform.system().lower()
            
            if system == 'windows':
                cmd = ['ping', '-n', '1', '-w', str(int(self.ping_timeout * 1000)), ip]
            else:
                cmd = ['ping', '-c', '1', '-W', str(int(self.ping_timeout)), ip]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=self.ping_timeout + 1
            )
            return result.returncode == 0
        
        except (subprocess.TimeoutExpired, Exception):
            return False
    
    def _scan_port(self, ip: str, port: int) -> bool:
        """Check if port is open."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((ip, port))
                return result == 0
        except (socket.timeout, socket.error):
            return False
    
    def _get_service_name(self, port: int) -> str:
        """Get service name for port."""
        if port in self.COMMON_PORTS:
            return self.COMMON_PORTS[port]
        
        try:
            return socket.getservbyport(port)
        except OSError:
            return 'unknown'
    
    def _try_grab_banner(self, ip: str, port: int) -> Optional[str]:
        """Attempt to grab service banner."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2.0)
                sock.connect((ip, port))
                
                # Try to get banner
                try:
                    sock.send(b'\r\n')
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    return banner[:100] if banner else None
                except:
                    return None
        except:
            return None
    
    def _get_hostname(self, ip: str) -> Optional[str]:
        """Get hostname for IP."""
        try:
            return socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror):
            return None
    
    def _get_mac_address(self, ip: str) -> Optional[str]:
        """Get MAC address (Linux/macOS only)."""
        try:
            system = platform.system().lower()
            
            if system == 'linux':
                cmd = ['arp', '-n', ip]
            elif system == 'darwin':
                cmd = ['arp', '-n', ip]
            elif system == 'windows':
                cmd = ['arp', '-a', ip]
            else:
                return None
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ip in line:
                        parts = line.split()
                        for part in parts:
                            if ':' in part and len(part) == 17:
                                return part
                            if '-' in part and len(part) == 17:
                                return part.replace('-', ':')
        except:
            pass
        
        return None
    
    def scan_host(self, ip: str, ports: List[int], 
                  check_hostname: bool = True,
                  check_mac: bool = True,
                  grab_banners: bool = False) -> Optional[Dict]:
        """Scan single host for open ports."""
        # Check if host is alive
        if not self._ping_host(ip):
            return None
        
        self.stats['hosts_alive'] += 1
        
        host_info = {
            'ip': ip,
            'hostname': None,
            'mac': None,
            'ports': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Get hostname
        if check_hostname:
            host_info['hostname'] = self._get_hostname(ip)
        
        # Get MAC address
        if check_mac:
            host_info['mac'] = self._get_mac_address(ip)
        
        # Scan ports
        open_ports = []
        for port in ports:
            self.stats['ports_scanned'] += 1
            
            if self._scan_port(ip, port):
                self.stats['ports_open'] += 1
                
                port_info = {
                    'port': port,
                    'service': self._get_service_name(port),
                    'banner': None
                }
                
                # Grab banner if requested
                if grab_banners:
                    port_info['banner'] = self._try_grab_banner(ip, port)
                
                open_ports.append(port_info)
        
        host_info['ports'] = open_ports
        host_info['port_count'] = len(open_ports)
        
        return host_info if open_ports else host_info
    
    def scan_network(self, network: str, ports: List[int],
                    check_hostname: bool = True,
                    check_mac: bool = True,
                    grab_banners: bool = False,
                    only_alive: bool = False) -> List[Dict]:
        """Scan network range for hosts and ports."""
        try:
            net = ipaddress.ip_network(network, strict=False)
        except ValueError as e:
            raise ValueError(f"Invalid network: {e}")
        
        hosts = list(net.hosts())
        
        print(f"Scanning {len(hosts)} host(s) on {network}")
        print(f"Checking {len(ports)} port(s) per host")
        print(f"Workers: {self.max_workers}, Timeout: {self.timeout}s")
        
        self.stats['scan_start'] = datetime.now().isoformat()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self.scan_host, str(ip), ports, 
                    check_hostname, check_mac, grab_banners
                ): str(ip) for ip in hosts
            }
            
            iterator = concurrent.futures.as_completed(futures)
            if HAS_TQDM:
                iterator = tqdm(iterator, total=len(futures), desc="Scanning", unit="host")
            
            for future in iterator:
                self.stats['hosts_scanned'] += 1
                
                try:
                    result = future.result()
                    if result:
                        if not only_alive or result['port_count'] > 0:
                            self.discovered_hosts.append(result)
                except Exception as e:
                    print(f"Error scanning {futures[future]}: {e}")
        
        self.stats['scan_end'] = datetime.now().isoformat()
        
        return self.discovered_hosts
    
    def quick_scan(self, network: str) -> List[Dict]:
        """Quick scan using only common ports."""
        common_ports = [21, 22, 23, 80, 443, 445, 3389, 8080]
        return self.scan_network(network, common_ports, check_mac=False, grab_banners=False)
    
    def full_scan(self, network: str) -> List[Dict]:
        """Full scan of common ports with banners."""
        ports = list(self.COMMON_PORTS.keys())
        return self.scan_network(network, ports, check_hostname=True, 
                               check_mac=True, grab_banners=True)
    
    def scan_single_host(self, ip: str, port_range: Tuple[int, int] = (1, 1024)) -> Optional[Dict]:
        """Scan all ports on single host."""
        ports = list(range(port_range[0], port_range[1] + 1))
        print(f"Scanning {ip} for {len(ports)} ports...")
        
        self.stats['scan_start'] = datetime.now().isoformat()
        result = self.scan_host(ip, ports, check_hostname=True, 
                               check_mac=True, grab_banners=True)
        self.stats['scan_end'] = datetime.now().isoformat()
        
        if result:
            self.discovered_hosts.append(result)
        
        return result
    
    def print_results(self, verbose: bool = False):
        """Print scan results."""
        print("\n" + "=" * 80)
        print("NETWORK SCAN RESULTS")
        print("=" * 80)
        
        if not self.discovered_hosts:
            print("No hosts discovered.")
            return
        
        for host in sorted(self.discovered_hosts, key=lambda x: x['ip']):
            ip_display = f"📍 {host['ip']}"
            
            if host['hostname']:
                ip_display += f" ({host['hostname']})"
            
            print(f"\n{ip_display}")
            
            if host['mac']:
                print(f"   MAC: {host['mac']}")
            
            if host['ports']:
                print(f"   Open Ports: {host['port_count']}")
                
                for port_info in sorted(host['ports'], key=lambda x: x['port']):
                    service = port_info['service']
                    print(f"      {port_info['port']:5d}/tcp  {service:20s}", end='')
                    
                    if verbose and port_info.get('banner'):
                        print(f"  [{port_info['banner'][:50]}]")
                    else:
                        print()
            else:
                print("   No open ports found")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Hosts Scanned:    {self.stats['hosts_scanned']}")
        print(f"Hosts Alive:      {self.stats['hosts_alive']}")
        print(f"Ports Scanned:    {self.stats['ports_scanned']:,}")
        print(f"Ports Open:       {self.stats['ports_open']}")
        
        if self.stats['scan_start'] and self.stats['scan_end']:
            start = datetime.fromisoformat(self.stats['scan_start'])
            end = datetime.fromisoformat(self.stats['scan_end'])
            duration = (end - start).total_seconds()
            print(f"Duration:         {duration:.2f}s")
    
    def export_json(self, output_path: Path):
        """Export results to JSON."""
        data = {
            'scan_info': {
                'timestamp': datetime.now().isoformat(),
                'statistics': self.stats
            },
            'hosts': self.discovered_hosts
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults exported to: {output_path}")
    
    def export_csv(self, output_path: Path):
        """Export results to CSV."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['IP', 'Hostname', 'MAC', 'Port', 'Service', 'Banner'])
            
            for host in self.discovered_hosts:
                ip = host['ip']
                hostname = host['hostname'] or ''
                mac = host['mac'] or ''
                
                if host['ports']:
                    for port_info in host['ports']:
                        writer.writerow([
                            ip, hostname, mac,
                            port_info['port'],
                            port_info['service'],
                            port_info.get('banner', '')
                        ])
                else:
                    writer.writerow([ip, hostname, mac, '', '', ''])
        
        print(f"CSV exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Scan local network for devices and open ports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick scan of local network
  python network_scanner.py --network 192.168.1.0/24 --quick
  
  # Scan specific ports
  python network_scanner.py --network 192.168.1.0/24 --ports 22,80,443
  
  # Full scan with banners
  python network_scanner.py --network 192.168.1.0/24 --full --banners
  
  # Scan single host (all ports 1-1024)
  python network_scanner.py --host 192.168.1.1
  
  # Scan single host custom port range
  python network_scanner.py --host 192.168.1.1 --port-range 1 65535
  
  # Fast scan (more threads, shorter timeout)
  python network_scanner.py --network 192.168.1.0/24 --quick --workers 200 --timeout 0.5
  
  # Export results
  python network_scanner.py --network 192.168.1.0/24 --quick --export-json scan.json

COMMON NETWORKS:
  - Class C: 192.168.1.0/24 (254 hosts)
  - Class B: 172.16.0.0/16 (65,534 hosts)
  - Smaller: 192.168.1.0/28 (14 hosts)
"""
    )
    
    # Scan target
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--network', type=str, help='Network to scan (CIDR notation)')
    target.add_argument('--host', type=str, help='Single host to scan')
    
    # Scan mode
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--quick', action='store_true', 
                     help='Quick scan (common ports only)')
    mode.add_argument('--full', action='store_true',
                     help='Full scan (all common ports with banners)')
    mode.add_argument('--ports', type=str,
                     help='Specific ports (comma-separated or range)')
    
    # Single host options
    parser.add_argument('--port-range', nargs=2, type=int, metavar=('START', 'END'),
                       default=(1, 1024),
                       help='Port range for single host scan (default: 1-1024)')
    
    # Scan options
    parser.add_argument('--timeout', type=float, default=1.0,
                       help='Socket timeout in seconds (default: 1.0)')
    parser.add_argument('--ping-timeout', type=float, default=1.0,
                       help='Ping timeout in seconds (default: 1.0)')
    parser.add_argument('--workers', type=int, default=100,
                       help='Number of concurrent threads (default: 100)')
    
    parser.add_argument('--no-hostname', dest='check_hostname', action='store_false',
                       help='Skip hostname resolution')
    parser.add_argument('--no-mac', dest='check_mac', action='store_false',
                       help='Skip MAC address lookup')
    parser.add_argument('--banners', action='store_true',
                       help='Attempt to grab service banners')
    parser.add_argument('--only-alive', action='store_true',
                       help='Only show hosts with open ports')
    
    # Output options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output with banners')
    parser.add_argument('--export-json', type=Path,
                       help='Export results to JSON')
    parser.add_argument('--export-csv', type=Path,
                       help='Export results to CSV')
    
    args = parser.parse_args()
    
    # Parse ports
    ports = None
    if args.ports:
        try:
            if '-' in args.ports:
                start, end = map(int, args.ports.split('-'))
                ports = list(range(start, end + 1))
            else:
                ports = [int(p.strip()) for p in args.ports.split(',')]
        except ValueError:
            print("Error: Invalid port specification")
            sys.exit(1)
    
    try:
        scanner = NetworkScanner(
            timeout=args.timeout,
            max_workers=args.workers,
            ping_timeout=args.ping_timeout
        )
        
        # Execute scan
        if args.host:
            scanner.scan_single_host(args.host, tuple(args.port_range))
        elif args.quick:
            scanner.quick_scan(args.network)
        elif args.full:
            scanner.full_scan(args.network)
        else:
            if not ports:
                ports = [22, 80, 443]  # Default ports
            
            scanner.scan_network(
                args.network, ports,
                check_hostname=args.check_hostname,
                check_mac=args.check_mac,
                grab_banners=args.banners,
                only_alive=args.only_alive
            )
        
        # Print results
        scanner.print_results(verbose=args.verbose)
        
        # Export
        if args.export_json:
            scanner.export_json(args.export_json)
        
        if args.export_csv:
            scanner.export_csv(args.export_csv)
        
        sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\nScan cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
