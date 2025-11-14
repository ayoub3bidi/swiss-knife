#!/usr/bin/env python3

import sys
import argparse
import json
from pathlib import Path
from typing import Any, Optional, List
from collections import OrderedDict

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class JSONFormatter:
    
    def __init__(self, sort_keys: bool = False, ensure_ascii: bool = False):
        self.sort_keys = sort_keys
        self.ensure_ascii = ensure_ascii
        self.stats = {
            'files_processed': 0,
            'files_failed': 0,
            'total_input_size': 0,
            'total_output_size': 0
        }
    
    def _format_size(self, bytes_val: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} TB"
    
    def prettify(self, data: Any, indent: int = 2) -> str:
        """Format JSON with indentation."""
        return json.dumps(data, indent=indent, sort_keys=self.sort_keys, 
                         ensure_ascii=self.ensure_ascii)
    
    def minify(self, data: Any) -> str:
        """Minify JSON (remove whitespace)."""
        return json.dumps(data, separators=(',', ':'), sort_keys=self.sort_keys,
                         ensure_ascii=self.ensure_ascii)
    
    def validate(self, json_str: str) -> tuple[bool, Optional[str]]:
        """Validate JSON string."""
        try:
            json.loads(json_str)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"Line {e.lineno}, Column {e.colno}: {e.msg}"
    
    def read_json(self, filepath: Path) -> tuple[Optional[Any], Optional[str]]:
        """Read and parse JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Track input size
            self.stats['total_input_size'] += len(content.encode('utf-8'))
            
            data = json.loads(content)
            return data, None
        except json.JSONDecodeError as e:
            return None, f"JSON decode error at line {e.lineno}, column {e.colno}: {e.msg}"
        except Exception as e:
            return None, str(e)
    
    def write_json(self, filepath: Path, content: str) -> bool:
        """Write JSON to file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Track output size
            self.stats['total_output_size'] += len(content.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False
    
    def format_file(self, input_path: Path, output_path: Optional[Path] = None,
                   mode: str = 'prettify', indent: int = 2, 
                   backup: bool = False) -> bool:
        """Format a JSON file."""
        
        # Read input
        data, error = self.read_json(input_path)
        if error:
            print(f"Error reading {input_path}: {error}")
            self.stats['files_failed'] += 1
            return False
        
        # Format
        if mode == 'prettify':
            output = self.prettify(data, indent)
        elif mode == 'minify':
            output = self.minify(data)
        else:
            output = json.dumps(data, indent=indent, sort_keys=self.sort_keys,
                              ensure_ascii=self.ensure_ascii)
        
        # Determine output path
        if output_path is None:
            output_path = input_path
            
            # Create backup if modifying in place
            if backup:
                backup_path = input_path.with_suffix(input_path.suffix + '.bak')
                input_path.rename(backup_path)
                print(f"Backup created: {backup_path}")
        
        # Write output
        if self.write_json(output_path, output):
            self.stats['files_processed'] += 1
            return True
        
        self.stats['files_failed'] += 1
        return False
    
    def format_directory(self, directory: Path, output_dir: Optional[Path] = None,
                        mode: str = 'prettify', indent: int = 2,
                        recursive: bool = False, backup: bool = False) -> None:
        """Format all JSON files in directory."""
        
        pattern = '**/*.json' if recursive else '*.json'
        json_files = list(directory.glob(pattern))
        
        if not json_files:
            print(f"No JSON files found in {directory}")
            return
        
        print(f"Processing {len(json_files)} JSON file(s)...")
        
        iterator = tqdm(json_files, desc="Formatting", unit="files") if HAS_TQDM else json_files
        
        for filepath in iterator:
            if output_dir:
                # Preserve directory structure
                rel_path = filepath.relative_to(directory)
                output_path = output_dir / rel_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                output_path = None
            
            self.format_file(filepath, output_path, mode, indent, backup)
    
    def convert_format(self, input_path: Path, output_path: Path, 
                      input_format: str, output_format: str) -> bool:
        """Convert between JSON and other formats."""
        
        # Read data based on input format
        if input_format == 'json':
            data, error = self.read_json(input_path)
            if error:
                print(f"Error: {error}")
                return False
        else:
            print(f"Unsupported input format: {input_format}")
            return False
        
        # Write data based on output format
        if output_format == 'json':
            content = self.prettify(data)
            return self.write_json(output_path, content)
        elif output_format == 'jsonl':
            # JSON Lines format (one JSON object per line)
            if isinstance(data, list):
                lines = [json.dumps(item, ensure_ascii=self.ensure_ascii) for item in data]
                content = '\n'.join(lines)
            else:
                content = json.dumps(data, ensure_ascii=self.ensure_ascii)
            return self.write_json(output_path, content)
        else:
            print(f"Unsupported output format: {output_format}")
            return False
    
    def merge_files(self, input_files: List[Path], output_path: Path,
                   as_array: bool = True) -> bool:
        """Merge multiple JSON files."""
        
        merged_data = [] if as_array else {}
        
        print(f"Merging {len(input_files)} file(s)...")
        
        for filepath in input_files:
            data, error = self.read_json(filepath)
            if error:
                print(f"Skipping {filepath}: {error}")
                continue
            
            if as_array:
                if isinstance(data, list):
                    merged_data.extend(data)
                else:
                    merged_data.append(data)
            else:
                if isinstance(data, dict):
                    merged_data.update(data)
                else:
                    print(f"Warning: {filepath} is not a JSON object, skipping")
        
        # Write merged output
        content = self.prettify(merged_data)
        return self.write_json(output_path, content)
    
    def print_stats(self):
        """Print processing statistics."""
        print(f"\n{'='*60}")
        print("PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Files processed:   {self.stats['files_processed']}")
        print(f"Files failed:      {self.stats['files_failed']}")
        print(f"Input size:        {self._format_size(self.stats['total_input_size'])}")
        print(f"Output size:       {self._format_size(self.stats['total_output_size'])}")
        
        if self.stats['total_input_size'] > 0:
            ratio = (self.stats['total_output_size'] / self.stats['total_input_size']) * 100
            print(f"Size ratio:        {ratio:.1f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Format, validate, and manipulate JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Prettify JSON file
  python json_formatter.py data.json
  
  # Minify JSON file
  python json_formatter.py data.json --minify
  
  # Format with custom indentation
  python json_formatter.py data.json --indent 4
  
  # Sort keys alphabetically
  python json_formatter.py data.json --sort-keys
  
  # Format to different file
  python json_formatter.py input.json -o output.json
  
  # Format all JSON in directory
  python json_formatter.py data/ -r
  
  # Validate without formatting
  python json_formatter.py data.json --validate-only
  
  # Create backup before modifying
  python json_formatter.py data.json --backup
  
  # Merge multiple JSON files
  python json_formatter.py file1.json file2.json --merge -o merged.json
        """
    )
    
    parser.add_argument('input', nargs='+', type=Path,
                       help='Input JSON file(s) or directory')
    
    parser.add_argument('-o', '--output', type=Path,
                       help='Output file or directory')
    parser.add_argument('--mode', choices=['prettify', 'minify'], default='prettify',
                       help='Formatting mode (default: prettify)')
    parser.add_argument('--indent', type=int, default=2,
                       help='Indentation spaces (default: 2)')
    
    parser.add_argument('--sort-keys', action='store_true',
                       help='Sort object keys alphabetically')
    parser.add_argument('--ascii', dest='ensure_ascii', action='store_true',
                       help='Escape non-ASCII characters')
    
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Process directories recursively')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup before modifying')
    
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate, don\'t format')
    parser.add_argument('--merge', action='store_true',
                       help='Merge multiple JSON files')
    parser.add_argument('--merge-as-object', action='store_true',
                       help='Merge as object instead of array')
    
    parser.add_argument('--minify', action='store_true',
                       help='Shorthand for --mode minify')
    
    args = parser.parse_args()
    
    # Handle minify shorthand
    if args.minify:
        args.mode = 'minify'
    
    # Validate input
    for path in args.input:
        if not path.exists():
            print(f"Error: Path not found: {path}")
            sys.exit(1)
    
    try:
        formatter = JSONFormatter(
            sort_keys=args.sort_keys,
            ensure_ascii=args.ensure_ascii
        )
        
        # Validate-only mode
        if args.validate_only:
            all_valid = True
            for filepath in args.input:
                if filepath.is_file():
                    with open(filepath, 'r') as f:
                        content = f.read()
                    valid, error = formatter.validate(content)
                    if valid:
                        print(f"✓ {filepath}: Valid JSON")
                    else:
                        print(f"✗ {filepath}: {error}")
                        all_valid = False
            sys.exit(0 if all_valid else 1)
        
        # Merge mode
        if args.merge:
            if not args.output:
                print("Error: --merge requires --output")
                sys.exit(1)
            
            json_files = [p for p in args.input if p.is_file() and p.suffix == '.json']
            formatter.merge_files(json_files, args.output, not args.merge_as_object)
            formatter.print_stats()
            sys.exit(0)
        
        # Single file processing
        if len(args.input) == 1 and args.input[0].is_file():
            formatter.format_file(
                args.input[0],
                args.output,
                args.mode,
                args.indent,
                args.backup
            )
        
        # Directory processing
        elif len(args.input) == 1 and args.input[0].is_dir():
            formatter.format_directory(
                args.input[0],
                args.output,
                args.mode,
                args.indent,
                args.recursive,
                args.backup
            )
        
        # Multiple files
        else:
            for filepath in args.input:
                if filepath.is_file():
                    output_path = None
                    if args.output and args.output.is_dir():
                        output_path = args.output / filepath.name
                    
                    formatter.format_file(
                        filepath,
                        output_path,
                        args.mode,
                        args.indent,
                        args.backup
                    )
        
        formatter.print_stats()
        
        sys.exit(0 if formatter.stats['files_failed'] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
