import re
import argparse
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from collections import defaultdict
from tqdm import tqdm
import json


class BulkRenamer:
    
    def __init__(
        self,
        pattern: str,
        replacement: str,
        paths: List[str],
        recursive: bool = False,
        extensions: Optional[List[str]] = None,
        case_sensitive: bool = True,
        dry_run: bool = False,
        interactive: bool = False,
        rename_extension: bool = False,
        sequence_start: int = 1,
        sequence_padding: int = 0
    ):
        self.pattern = pattern
        self.replacement = replacement
        self.paths = [Path(p) for p in paths]
        self.recursive = recursive
        self.extensions = [ext.lower().lstrip('.') for ext in extensions] if extensions else None
        self.case_sensitive = case_sensitive
        self.dry_run = dry_run
        self.interactive = interactive
        self.rename_extension = rename_extension
        self.sequence_start = sequence_start
        self.sequence_padding = sequence_padding
        
        # Compile regex pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            self.regex = re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        
        self.sequence_counter = sequence_start
        self.stats = {
            'total_files': 0,
            'renamed': 0,
            'skipped': 0,
            'errors': 0,
            'collisions': 0
        }
        self.rename_map: List[Tuple[Path, Path]] = []
        self.errors: List[Tuple[Path, str]] = []
    
    def collect_files(self) -> List[Path]:
        files = []
        
        for path in self.paths:
            if not path.exists():
                print(f"Warning: Path does not exist: {path}")
                continue
            
            if path.is_file():
                if self._should_process_file(path):
                    files.append(path)
            elif path.is_dir():
                pattern = "**/*" if self.recursive else "*"
                for file_path in path.glob(pattern):
                    if file_path.is_file() and self._should_process_file(file_path):
                        files.append(file_path)
        
        return sorted(files)
    
    def _should_process_file(self, path: Path) -> bool:
        if self.extensions is None:
            return True
        return path.suffix.lower().lstrip('.') in self.extensions
    
    def _get_sequence_string(self) -> str:
        seq = str(self.sequence_counter)
        if self.sequence_padding > 0:
            seq = seq.zfill(self.sequence_padding)
        self.sequence_counter += 1
        return seq
    
    def _expand_replacement(self, match: re.Match, original_path: Path) -> str:
        replacement = self.replacement
        
        # Replace standard regex groups
        replacement = match.expand(replacement)
        
        # Custom placeholders
        replacement = replacement.replace('{seq}', self._get_sequence_string())
        replacement = replacement.replace('{parent}', original_path.parent.name)
        replacement = replacement.replace('{ext}', original_path.suffix)
        
        return replacement
    
    def generate_rename_map(self, files: List[Path]) -> None:
        self.rename_map = []
        self.sequence_counter = self.sequence_start
        
        for file_path in files:
            self.stats['total_files'] += 1
            
            # Determine what to rename (full name or just stem)
            if self.rename_extension:
                target = file_path.name
            else:
                target = file_path.stem
            
            # Apply regex substitution
            match = self.regex.search(target)
            if not match:
                self.stats['skipped'] += 1
                continue
            
            new_name = self.regex.sub(
                lambda m: self._expand_replacement(m, file_path),
                target
            )
            
            # Reconstruct full filename
            if self.rename_extension:
                new_path = file_path.parent / new_name
            else:
                new_path = file_path.parent / f"{new_name}{file_path.suffix}"
            
            # Skip if name unchanged
            if file_path == new_path:
                self.stats['skipped'] += 1
                continue
            
            self.rename_map.append((file_path, new_path))
    
    def check_collisions(self) -> Dict[Path, List[Path]]:
        target_map = defaultdict(list)
        
        for old_path, new_path in self.rename_map:
            target_map[new_path].append(old_path)
        
        # Find collisions (multiple files renaming to same target)
        collisions = {k: v for k, v in target_map.items() if len(v) > 1}
        
        # Also check if target already exists in filesystem
        for old_path, new_path in self.rename_map:
            if new_path.exists() and new_path != old_path:
                if new_path not in collisions:
                    collisions[new_path] = [old_path]
        
        self.stats['collisions'] = len(collisions)
        return collisions
    
    def execute_renames(self) -> None:
        if not self.rename_map:
            print("No files to rename.")
            return
        
        # Check for collisions
        collisions = self.check_collisions()
        if collisions:
            print(f"\n⚠️  Warning: {len(collisions)} naming collision(s) detected:")
            for target, sources in list(collisions.items())[:5]:
                print(f"  → {target.name}")
                for src in sources[:3]:
                    print(f"      ← {src.name}")
                if len(sources) > 3:
                    print(f"      ... and {len(sources) - 3} more")
            
            if not self.dry_run:
                response = input("\nContinue anyway? Collisions will be skipped. (y/N): ")
                if response.lower() != 'y':
                    print("Operation cancelled.")
                    return
        
        # Execute renames
        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Renaming files...")
        
        for old_path, new_path in tqdm(self.rename_map, desc="Renaming"):
            # Skip if collision
            if new_path in collisions:
                self.stats['skipped'] += 1
                continue
            
            # Interactive confirmation
            if self.interactive and not self.dry_run:
                print(f"\n{old_path.name} → {new_path.name}")
                response = input("Rename? (y/N/q): ").lower()
                if response == 'q':
                    print("Operation cancelled.")
                    break
                if response != 'y':
                    self.stats['skipped'] += 1
                    continue
            
            # Perform rename
            try:
                if not self.dry_run:
                    old_path.rename(new_path)
                self.stats['renamed'] += 1
            except Exception as e:
                self.stats['errors'] += 1
                self.errors.append((old_path, str(e)))
    
    def print_preview(self) -> None:
        if not self.rename_map:
            print("No files match the pattern.")
            return
        
        print(f"\nPreview: {len(self.rename_map)} file(s) will be renamed\n")
        print(f"{'Old Name':<50} → {'New Name'}")
        print("-" * 105)
        
        for old_path, new_path in self.rename_map[:20]:
            old_name = old_path.name
            new_name = new_path.name
            if len(old_name) > 48:
                old_name = old_name[:45] + "..."
            if len(new_name) > 48:
                new_name = new_name[:45] + "..."
            print(f"{old_name:<50} → {new_name}")
        
        if len(self.rename_map) > 20:
            print(f"... and {len(self.rename_map) - 20} more")
    
    def print_stats(self) -> None:
        print("\n" + "=" * 50)
        print("Rename Statistics")
        print("=" * 50)
        print(f"Total files scanned: {self.stats['total_files']}")
        print(f"Files renamed:       {self.stats['renamed']}")
        print(f"Files skipped:       {self.stats['skipped']}")
        print(f"Naming collisions:   {self.stats['collisions']}")
        print(f"Errors:              {self.stats['errors']}")
        
        if self.errors:
            print("\nErrors:")
            for path, error in self.errors[:10]:
                print(f"  {path.name}: {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")
    
    def export_results(self, output_file: str, format: str = 'json') -> None:
        data = {
            'pattern': self.pattern,
            'replacement': self.replacement,
            'stats': self.stats,
            'renames': [
                {'old': str(old), 'new': str(new)}
                for old, new in self.rename_map
            ],
            'errors': [
                {'file': str(path), 'error': error}
                for path, error in self.errors
            ]
        }
        
        output_path = Path(output_file)
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:  # text
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Pattern: {self.pattern}\n")
                f.write(f"Replacement: {self.replacement}\n\n")
                f.write("Statistics:\n")
                for key, value in self.stats.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\nRenames:\n")
                for old, new in self.rename_map:
                    f.write(f"  {old} → {new}\n")
                if self.errors:
                    f.write("\nErrors:\n")
                    for path, error in self.errors:
                        f.write(f"  {path}: {error}\n")
        
        print(f"Results exported to: {output_path}")


def parse_size(size_str: str) -> int:
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
    size_str = size_str.upper().strip()
    
    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            return int(float(size_str[:-len(unit)]) * multiplier)
    
    return int(size_str)


def main():
    parser = argparse.ArgumentParser(
        description="Bulk file renamer with regex pattern matching",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Replace spaces with underscores
  python bulk_renamer.py "\\s+" "_" ~/Documents
  
  # Add sequence numbers to files
  python bulk_renamer.py "^" "photo_{seq}_" ~/Pictures --seq-padding 3
  
  # Remove dates from filenames
  python bulk_renamer.py "\\d{4}-\\d{2}-\\d{2}_" "" .
  
  # Rename with regex groups
  python bulk_renamer.py "(\\d+)_(.+)" "\\2_\\1" .
  
  # Case-insensitive replacement
  python bulk_renamer.py "IMG" "photo" . --ignore-case
  
  # Recursive with extension filter
  python bulk_renamer.py "old" "new" ~/Projects -r --ext py,js,ts
  
  # Preview before renaming
  python bulk_renamer.py "test" "prod" . --preview
  
Special placeholders in replacement:
  {seq}    - Sequential number (use --seq-start and --seq-padding)
  {parent} - Parent directory name
  {ext}    - File extension
  \\1, \\2  - Regex capture groups
        """
    )
    
    parser.add_argument('pattern', help='Regex pattern to match')
    parser.add_argument('replacement', help='Replacement string (supports regex groups and placeholders)')
    parser.add_argument('paths', nargs='+', help='Files or directories to process')
    
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Process directories recursively')
    parser.add_argument('--ext', '--extensions', dest='extensions',
                        help='Filter by file extensions (comma-separated, e.g., jpg,png,gif)')
    parser.add_argument('-i', '--ignore-case', action='store_true',
                        help='Case-insensitive pattern matching')
    parser.add_argument('--rename-ext', '--rename-extension', action='store_true',
                        help='Apply pattern to file extension as well')
    
    parser.add_argument('--seq-start', type=int, default=1,
                        help='Starting number for {seq} placeholder (default: 1)')
    parser.add_argument('--seq-padding', type=int, default=0,
                        help='Zero-padding for {seq} placeholder (e.g., 3 → 001)')
    
    parser.add_argument('--preview', action='store_true',
                        help='Preview changes without renaming')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be renamed without making changes')
    parser.add_argument('-I', '--interactive', action='store_true',
                        help='Confirm each rename operation')
    
    parser.add_argument('--output', choices=['json', 'text'],
                        help='Export results to file')
    parser.add_argument('--output-file', default='rename_results',
                        help='Output filename (without extension)')
    
    args = parser.parse_args()
    
    # Parse extensions
    extensions = None
    if args.extensions:
        extensions = [ext.strip() for ext in args.extensions.split(',')]
    
    try:
        # Initialize renamer
        renamer = BulkRenamer(
            pattern=args.pattern,
            replacement=args.replacement,
            paths=args.paths,
            recursive=args.recursive,
            extensions=extensions,
            case_sensitive=not args.ignore_case,
            dry_run=args.dry_run or args.preview,
            interactive=args.interactive,
            rename_extension=args.rename_ext,
            sequence_start=args.seq_start,
            sequence_padding=args.seq_padding
        )
        
        # Collect files
        print("Scanning for files...")
        files = renamer.collect_files()
        
        if not files:
            print("No files found matching criteria.")
            return
        
        print(f"Found {len(files)} file(s)")
        
        # Generate rename map
        renamer.generate_rename_map(files)
        
        # Show preview
        if args.preview or args.dry_run:
            renamer.print_preview()
            
            if args.preview:
                renamer.print_stats()
                return
        
        # Execute renames
        if not args.preview:
            renamer.execute_renames()
        
        # Print statistics
        renamer.print_stats()
        
        # Export results
        if args.output:
            output_file = f"{args.output_file}.{args.output}"
            renamer.export_results(output_file, args.output)
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
