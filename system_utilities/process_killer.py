#!/usr/bin/env python3
"""
Process Killer by Memory/CPU Usage
Terminates processes based on resource consumption thresholds with safety features.
"""

import sys
import argparse
import signal
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime
import time

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Error: psutil not installed. Run: pip install psutil")
    sys.exit(1)

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class ProcessKiller:
    
    # Protected processes that should never be killed
    PROTECTED_NAMES = {
        'systemd', 'init', 'kernel', 'kthreadd', 'launchd',
        'sshd', 'System', 'csrss.exe', 'wininit.exe', 'services.exe',
        'lsass.exe', 'winlogon.exe', 'explorer.exe'
    }
    
    def __init__(self,
                 memory_threshold: Optional[float] = None,
                 cpu_threshold: Optional[float] = None,
                 min_memory_mb: Optional[float] = None,
                 process_names: Optional[List[str]] = None,
                 exclude_names: Optional[List[str]] = None,
                 exclude_users: Optional[List[str]] = None,
                 force_kill: bool = False,
                 dry_run: bool = False):
        """
        Args:
            memory_threshold: Kill if memory % exceeds this (0-100)
            cpu_threshold: Kill if CPU % exceeds this (0-100+)
            min_memory_mb: Kill if memory MB exceeds this
            process_names: Only target these process names
            exclude_names: Never kill these process names
            exclude_users: Never kill processes owned by these users
            force_kill: Use SIGKILL instead of SIGTERM
            dry_run: Show what would be killed without killing
        """
        self.memory_threshold = memory_threshold
        self.cpu_threshold = cpu_threshold
        self.min_memory_mb = min_memory_mb
        self.process_names = set(process_names) if process_names else None
        self.exclude_names = set(exclude_names) if exclude_names else set()
        self.exclude_names.update(self.PROTECTED_NAMES)
        self.exclude_users = set(exclude_users) if exclude_users else set()
        self.force_kill = force_kill
        self.dry_run = dry_run
        
        self.stats = {
            'scanned': 0,
            'matched': 0,
            'killed': 0,
            'failed': 0,
            'protected': 0
        }
        
        self.killed_processes: List[Dict] = []
        self.failed_kills: List[Dict] = []
    
    def _format_bytes(self, bytes_val: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.2f} TB"
    
    def _is_protected(self, proc: psutil.Process) -> bool:
        """Check if process should be protected from termination."""
        try:
            # Check process name
            if proc.name().lower() in (name.lower() for name in self.exclude_names):
                return True
            
            # Check user
            if proc.username() in self.exclude_users:
                return True
            
            # Protect PID 1 and very low PIDs (system critical)
            if proc.pid <= 3:
                return True
            
            # Protect parent of current process
            if proc.pid == psutil.Process().ppid():
                return True
            
            return False
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return True  # If we can't check, protect it
    
    def _should_kill(self, proc: psutil.Process) -> bool:
        """Determine if process meets kill criteria."""
        try:
            # Check protection first
            if self._is_protected(proc):
                self.stats['protected'] += 1
                return False
            
            # Filter by process name if specified
            if self.process_names and proc.name() not in self.process_names:
                return False
            
            # Get resource usage
            mem_info = proc.memory_info()
            mem_percent = proc.memory_percent()
            cpu_percent = proc.cpu_percent(interval=0.1)
            mem_mb = mem_info.rss / (1024 * 1024)
            
            # Check thresholds
            meets_criteria = False
            
            if self.memory_threshold and mem_percent >= self.memory_threshold:
                meets_criteria = True
            
            if self.cpu_threshold and cpu_percent >= self.cpu_threshold:
                meets_criteria = True
            
            if self.min_memory_mb and mem_mb >= self.min_memory_mb:
                meets_criteria = True
            
            return meets_criteria
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False
    
    def _get_process_info(self, proc: psutil.Process) -> Dict:
        """Extract detailed process information."""
        try:
            mem_info = proc.memory_info()
            
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'cmdline': ' '.join(proc.cmdline()[:3]) if proc.cmdline() else '',
                'username': proc.username(),
                'memory_mb': mem_info.rss / (1024 * 1024),
                'memory_percent': proc.memory_percent(),
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'num_threads': proc.num_threads(),
                'status': proc.status(),
                'create_time': datetime.fromtimestamp(proc.create_time()).isoformat()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def scan_processes(self) -> List[psutil.Process]:
        """Scan all processes and identify targets."""
        targets = []
        
        processes = list(psutil.process_iter())
        self.stats['scanned'] = len(processes)
        
        print(f"Scanning {len(processes)} processes...")
        
        iterator = tqdm(processes, desc="Scanning") if HAS_TQDM else processes
        
        for proc in iterator:
            try:
                if self._should_kill(proc):
                    targets.append(proc)
                    self.stats['matched'] += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return targets
    
    def kill_process(self, proc: psutil.Process) -> bool:
        """Terminate a single process."""
        if self.dry_run:
            return True
        
        try:
            if self.force_kill:
                proc.kill()  # SIGKILL
            else:
                proc.terminate()  # SIGTERM
                
                # Wait for graceful termination
                try:
                    proc.wait(timeout=3)
                except psutil.TimeoutExpired:
                    # Force kill if graceful termination failed
                    proc.kill()
            
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return False
    
    def execute(self) -> None:
        """Main execution: scan and kill matching processes."""
        print(f"\n{'='*80}")
        print(f"Process Killer - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Kill Signal: {'SIGKILL' if self.force_kill else 'SIGTERM'}")
        
        if self.memory_threshold:
            print(f"Memory Threshold: {self.memory_threshold}%")
        if self.cpu_threshold:
            print(f"CPU Threshold: {self.cpu_threshold}%")
        if self.min_memory_mb:
            print(f"Minimum Memory: {self.min_memory_mb} MB")
        if self.process_names:
            print(f"Target Processes: {', '.join(self.process_names)}")
        if self.exclude_names:
            print(f"Protected: {len(self.exclude_names)} process names")
        
        # Scan for targets
        targets = self.scan_processes()
        
        if not targets:
            print(f"\n✓ No processes matched kill criteria")
            self._print_stats()
            return
        
        # Display targets
        print(f"\n⚠️  Found {len(targets)} process(es) matching criteria:")
        print(f"\n{'PID':<8} {'Name':<25} {'User':<15} {'Memory':<12} {'CPU':<8}")
        print("-" * 80)
        
        targets_info = []
        for proc in targets:
            info = self._get_process_info(proc)
            if info:
                targets_info.append((proc, info))
                print(f"{info['pid']:<8} {info['name'][:24]:<25} {info['username'][:14]:<15} "
                      f"{info['memory_mb']:>8.1f} MB {info['cpu_percent']:>6.1f}%")
        
        # Confirm before killing
        if not self.dry_run:
            print(f"\n{'⚠️ '*20}")
            response = input(f"\nKill {len(targets)} process(es)? This cannot be undone! (yes/NO): ")
            if response.lower() != 'yes':
                print("Operation cancelled.")
                return
        
        # Kill processes
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Terminating processes...")
        
        iterator = tqdm(targets_info, desc="Killing") if HAS_TQDM else targets_info
        
        for proc, info in iterator:
            if self.kill_process(proc):
                self.stats['killed'] += 1
                self.killed_processes.append(info)
                status = "[WOULD KILL]" if self.dry_run else "✓ Killed"
                print(f"{status} {info['name']} (PID {info['pid']}) - "
                      f"{info['memory_mb']:.1f} MB")
            else:
                self.stats['failed'] += 1
                self.failed_kills.append(info)
                print(f"✗ Failed to kill {info['name']} (PID {info['pid']})")
        
        self._print_stats()
    
    def _print_stats(self) -> None:
        """Print execution statistics."""
        print(f"\n{'='*80}")
        print("Statistics")
        print(f"{'='*80}")
        print(f"Processes scanned:  {self.stats['scanned']}")
        print(f"Matched criteria:   {self.stats['matched']}")
        print(f"Protected:          {self.stats['protected']}")
        print(f"Successfully killed: {self.stats['killed']}")
        print(f"Failed to kill:     {self.stats['failed']}")
        
        if self.killed_processes:
            total_mem = sum(p['memory_mb'] for p in self.killed_processes)
            print(f"Total memory freed: {total_mem:.1f} MB")


def main():
    parser = argparse.ArgumentParser(
        description="Kill processes by resource usage with safety features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Kill processes using >1GB memory (dry run)
  python process_killer.py --min-memory 1024 --dry-run
  
  # Kill processes using >80% memory
  python process_killer.py --memory-threshold 80
  
  # Kill specific process by name if using >500MB
  python process_killer.py --name chrome --min-memory 500
  
  # Kill high CPU processes
  python process_killer.py --cpu-threshold 90
  
  # Combined: Kill memory hogs excluding specific users
  python process_killer.py --min-memory 2048 --exclude-user root,postgres
  
  # Force kill immediately (SIGKILL)
  python process_killer.py --memory-threshold 90 --force

SAFETY FEATURES:
  - Protected system processes (init, systemd, kernel threads, etc.)
  - Confirmation prompt before killing
  - Dry-run mode to preview actions
  - User exclusion to protect specific accounts
  - Graceful termination (SIGTERM) by default

WARNING: Use with extreme caution! Killing processes can cause data loss.
        """
    )
    
    parser.add_argument('--memory-threshold', type=float,
                       help='Kill if memory percent exceeds this (0-100)')
    parser.add_argument('--cpu-threshold', type=float,
                       help='Kill if CPU percent exceeds this (0-100+)')
    parser.add_argument('--min-memory', type=float,
                       help='Kill if memory usage exceeds this (MB)')
    
    parser.add_argument('--name', '--process-name', dest='names', action='append',
                       help='Target specific process name(s), can specify multiple')
    parser.add_argument('--exclude-name', dest='exclude_names', action='append',
                       help='Never kill these process names')
    parser.add_argument('--exclude-user', dest='exclude_users', action='append',
                       help='Never kill processes owned by these users')
    
    parser.add_argument('--force', '-f', action='store_true',
                       help='Use SIGKILL instead of SIGTERM (immediate kill)')
    parser.add_argument('--dry-run', '-n', action='store_true',
                       help='Show what would be killed without actually killing')
    
    parser.add_argument('--top', type=int, metavar='N',
                       help='Kill top N processes by memory usage')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.memory_threshold, args.cpu_threshold, args.min_memory]):
        parser.error("Must specify at least one threshold: --memory-threshold, --cpu-threshold, or --min-memory")
    
    if not HAS_PSUTIL:
        print("Error: psutil library required. Install: pip install psutil")
        sys.exit(1)
    
    try:
        killer = ProcessKiller(
            memory_threshold=args.memory_threshold,
            cpu_threshold=args.cpu_threshold,
            min_memory_mb=args.min_memory,
            process_names=args.names,
            exclude_names=args.exclude_names,
            exclude_users=args.exclude_users,
            force_kill=args.force,
            dry_run=args.dry_run
        )
        
        killer.execute()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
