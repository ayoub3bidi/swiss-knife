import sys
import hashlib
import argparse
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Optional
import time

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Warning: tqdm not installed. Install with 'pip install tqdm' for progress bars.")


class DuplicateFinder:
    
    def __init__(self, hash_algorithm: str = 'md5', min_size: int = 0, 
                 max_size: Optional[int] = None, extensions: Optional[Set[str]] = None):
        """
        Args:
            hash_algorithm: 'md5', 'sha1', 'sha256', or 'sha512'
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes (None for unlimited)
            extensions: Set of file extensions to include (None for all)
        """
        self.hash_algorithm = hash_algorithm.lower()
        self.min_size = min_size
        self.max_size = max_size
        self.extensions = {ext.lower().lstrip('.') for ext in extensions} if extensions else None

        if self.hash_algorithm not in ['md5', 'sha1', 'sha256', 'sha512']:
            raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")
    
    def _get_file_hash(self, filepath: Path) -> str:
        hash_func = getattr(hashlib, self.hash_algorithm)()
        
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except (OSError, IOError) as e:
            print(f"Error reading {filepath}: {e}")
            return ""
    
    def _should_include_file(self, filepath: Path) -> bool:
        try:
            stat = filepath.stat()
            
            # Size filters
            if stat.st_size < self.min_size:
                return False
            if self.max_size and stat.st_size > self.max_size:
                return False
            
            # Extension filter
            if self.extensions:
                ext = filepath.suffix.lower().lstrip('.')
                if ext not in self.extensions:
                    return False
            
            return True
        except (OSError, IOError):
            return False
    
    def find_duplicates(self, search_paths: List[Path], recursive: bool = True) -> Dict[str, List[Path]]:
        """
        Args:
            search_paths: List of directories/files to search
            recursive: Whether to search subdirectories
            
        Returns: Dictionary mapping file hashes to lists of duplicate file paths
        """
        print(f"Scanning for duplicates using {self.hash_algorithm.upper()} algorithm...")
        
        # Collect all files
        all_files = []
        for search_path in search_paths:
            if search_path.is_file():
                if self._should_include_file(search_path):
                    all_files.append(search_path)
            elif search_path.is_dir():
                pattern = "**/*" if recursive else "*"
                for filepath in search_path.glob(pattern):
                    if filepath.is_file() and self._should_include_file(filepath):
                        all_files.append(filepath)
        
        print(f"Found {len(all_files)} files to analyze")
        
        # Calculate hashes with progress bar
        hash_to_files = defaultdict(list)
        
        if HAS_TQDM:
            pbar = tqdm(all_files, desc="Calculating hashes", unit="files")
        else:
            pbar = all_files
            print("Calculating file hashes...")
        
        for filepath in pbar:
            file_hash = self._get_file_hash(filepath)
            if file_hash:  # Only add if hash calculation succeeded
                hash_to_files[file_hash].append(filepath)
        
        # Filter to only duplicates (hash appears more than once)
        duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
        
        return duplicates
    
    def get_duplicate_stats(self, duplicates: Dict[str, List[Path]]) -> Dict:
        total_files = sum(len(files) for files in duplicates.values())
        total_groups = len(duplicates)
        
        # Calculate wasted space (all but one file per group)
        wasted_space = 0
        largest_group = 0
        
        for files in duplicates.values():
            if files:
                file_size = files[0].stat().st_size
                wasted_space += file_size * (len(files) - 1)
                largest_group = max(largest_group, len(files))
        
        return {
            'duplicate_groups': total_groups,
            'duplicate_files': total_files,
            'wasted_space_bytes': wasted_space,
            'wasted_space_mb': wasted_space / (1024 * 1024),
            'largest_group': largest_group
        }


def format_size(bytes_size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f}PB"


def parse_size(size_str: str) -> int:
    size_str = size_str.upper().strip()
    
    multipliers = {
        'B': 1, 'KB': 1024, 'MB': 1024**2, 
        'GB': 1024**3, 'TB': 1024**4
    }
    
    for unit, multiplier in multipliers.items():
        if size_str.endswith(unit):
            number = float(size_str[:-len(unit)])
            return int(number * multiplier)
    
    # If no unit, assume bytes
    return int(size_str)


def output_results(duplicates: Dict[str, List[Path]], output_format: str, output_file: Optional[str] = None):
    if output_format == 'json':
        # Convert Path objects to strings for JSON serialization
        json_data = {
            hash_val: [str(path) for path in files]
            for hash_val, files in duplicates.items()
        }
        
        json_str = json.dumps(json_data, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_str)
            print(f"Results saved to {output_file}")
        else:
            print(json_str)
    
    elif output_format == 'text':
        output_lines = []
        
        for i, (hash_val, files) in enumerate(duplicates.items(), 1):
            file_size = format_size(files[0].stat().st_size)
            output_lines.append(f"\nGroup {i}: {len(files)} files ({file_size} each)")
            output_lines.append(f"Hash: {hash_val}")
            
            for file_path in files:
                output_lines.append(f"  {file_path}")
        
        output_text = '\n'.join(output_lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_text)
            print(f"Results saved to {output_file}")
        else:
            print(output_text)


def delete_duplicates(duplicates: Dict[str, List[Path]], keep_strategy: str = 'first'):
    """
    Args:
        duplicates: Dictionary of hash -> file paths
        keep_strategy: 'first', 'last', 'shortest_name', 'longest_name'
    """
    print(f"\nDeleting duplicates (keeping {keep_strategy} file in each group)...")
    
    total_deleted = 0
    total_freed = 0
    
    for files in duplicates.values():
        if len(files) <= 1:
            continue
        
        # Determine which file to keep
        if keep_strategy == 'first':
            to_keep = files[0]
        elif keep_strategy == 'last':
            to_keep = files[-1]
        elif keep_strategy == 'shortest_name':
            to_keep = min(files, key=lambda f: len(f.name))
        elif keep_strategy == 'longest_name':
            to_keep = max(files, key=lambda f: len(f.name))
        else:
            to_keep = files[0]  # Default to first
        
        # Delete other files
        for file_path in files:
            if file_path != to_keep:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    print(f"Deleted: {file_path}")
                    total_deleted += 1
                    total_freed += file_size
                except (OSError, IOError) as e:
                    print(f"Error deleting {file_path}: {e}")
    
    print(f"\nDeleted {total_deleted} duplicate files")
    print(f"Freed {format_size(total_freed)} of disk space")


def main():
    parser = argparse.ArgumentParser(
        description="Find and manage duplicate files using hash comparison",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /home/user/Documents
  %(prog)s /path/to/search --hash sha256 --min-size 1MB
  %(prog)s /path/to/search --extensions jpg,png,gif
  %(prog)s /path/to/search --output json --file results.json
  %(prog)s /path/to/search --delete-duplicates --keep-strategy shortest_name
        """
    )
    
    parser.add_argument('paths', nargs='+', type=Path,
                       help='Directories or files to search for duplicates')
    parser.add_argument('--hash', choices=['md5', 'sha1', 'sha256', 'sha512'],
                       default='md5', help='Hash algorithm to use (default: md5)')
    parser.add_argument('--min-size', type=str, default='0',
                       help='Minimum file size (e.g., 1MB, 500KB)')
    parser.add_argument('--max-size', type=str,
                       help='Maximum file size (e.g., 100MB)')
    parser.add_argument('--extensions', type=str,
                       help='Comma-separated file extensions to include')
    parser.add_argument('--recursive', action='store_true', default=True,
                       help='Search directories recursively (default: True)')
    parser.add_argument('--output', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--file', type=str,
                       help='Output file path (prints to stdout if not specified)')
    parser.add_argument('--delete-duplicates', action='store_true',
                       help='Delete duplicate files (DANGEROUS - use with caution)')
    parser.add_argument('--keep-strategy', 
                       choices=['first', 'last', 'shortest_name', 'longest_name'],
                       default='first',
                       help='Which file to keep when deleting duplicates (default: first)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    # Parse size arguments
    min_size = parse_size(args.min_size)
    max_size = parse_size(args.max_size) if args.max_size else None
    
    # Parse extensions
    extensions = None
    if args.extensions:
        extensions = {ext.strip() for ext in args.extensions.split(',')}
    
    # Validate paths
    for path in args.paths:
        if not path.exists():
            print(f"Error: Path does not exist: {path}")
            sys.exit(1)
    
    try:
        # Initialize finder
        finder = DuplicateFinder(
            hash_algorithm=args.hash,
            min_size=min_size,
            max_size=max_size,
            extensions=extensions
        )
        
        # Find duplicates
        start_time = time.time()
        duplicates = finder.find_duplicates(args.paths, recursive=args.recursive)
        elapsed_time = time.time() - start_time
        
        # Display statistics
        if duplicates:
            stats = finder.get_duplicate_stats(duplicates)
            print(f"\nDuplicate Analysis Complete ({elapsed_time:.2f}s)")
            print(f"Found {stats['duplicate_groups']} groups of duplicates")
            print(f"Total duplicate files: {stats['duplicate_files']}")
            print(f"Wasted space: {format_size(stats['wasted_space_bytes'])}")
            print(f"Largest group: {stats['largest_group']} files")
            
            # Output results
            if not args.delete_duplicates:
                output_results(duplicates, args.output, args.file)
            
            # Handle deletion
            if args.delete_duplicates:
                if args.dry_run:
                    print("\nDRY RUN - Would delete:")
                    for files in duplicates.values():
                        if len(files) > 1:
                            to_keep = files[0] if args.keep_strategy == 'first' else files[-1]
                            for file_path in files:
                                if file_path != to_keep:
                                    print(f"  {file_path}")
                else:
                    confirm = input(f"\nDelete {sum(len(files)-1 for files in duplicates.values())} duplicate files? (y/N): ")
                    if confirm.lower() == 'y':
                        delete_duplicates(duplicates, args.keep_strategy)
                    else:
                        print("Deletion cancelled")
        else:
            print(f"\nNo duplicates found ({elapsed_time:.2f}s)")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
