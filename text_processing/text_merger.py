#!/usr/bin/env python3

import argparse
import glob
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class TextMerger:
    DELIMITER_PRESETS = {
        "line": "-" * 80,
        "double": "=" * 80,
        "hash": "#" * 80,
        "star": "*" * 80,
        "dash": "- " * 40,
        "blank": "",
        "minimal": "---",
        "section": "\n" + "=" * 80 + "\n",
    }

    def __init__(
        self,
        delimiter: str = "line",
        add_filename: bool = True,
        add_timestamp: bool = False,
        add_file_stats: bool = False,
        sort_files: bool = False,
        sort_by: str = "name",
        reverse_sort: bool = False,
        remove_empty_lines: bool = False,
        strip_whitespace: bool = False,
        add_line_numbers: bool = False,
        encoding: str = "utf-8",
        error_handling: str = "skip",
    ):
        """
        Args:
            delimiter: Delimiter preset name or custom string
            add_filename: Add filename header before each file
            add_timestamp: Add timestamp to filename header
            add_file_stats: Add file statistics (lines, size)
            sort_files: Sort files before merging
            sort_by: Sort criterion ('name', 'size', 'date', 'extension')
            reverse_sort: Reverse sort order
            remove_empty_lines: Remove empty lines from output
            strip_whitespace: Strip leading/trailing whitespace from lines
            add_line_numbers: Add line numbers to output
            encoding: File encoding
            error_handling: How to handle read errors ('skip', 'stop', 'replace')
        """
        self.delimiter = self.DELIMITER_PRESETS.get(delimiter, delimiter)
        self.add_filename = add_filename
        self.add_timestamp = add_timestamp
        self.add_file_stats = add_file_stats
        self.sort_files = sort_files
        self.sort_by = sort_by
        self.reverse_sort = reverse_sort
        self.remove_empty_lines = remove_empty_lines
        self.strip_whitespace = strip_whitespace
        self.add_line_numbers = add_line_numbers
        self.encoding = encoding
        self.error_handling = error_handling

        self.stats = {
            "files_processed": 0,
            "files_failed": 0,
            "total_lines": 0,
            "total_size": 0,
            "errors": [],
        }

    def _format_bytes(self, bytes_val: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} TB"

    def _get_sort_key(self) -> Callable:
        if self.sort_by == "size":
            return lambda f: f.stat().st_size
        elif self.sort_by == "date":
            return lambda f: f.stat().st_mtime
        elif self.sort_by == "extension":
            return lambda f: (f.suffix, f.name)
        else:  # name
            return lambda f: f.name

    def _collect_files(
        self, paths: List[str], extensions: Optional[List[str]] = None
    ) -> List[Path]:
        files = []

        for path_pattern in paths:
            # Handle glob patterns
            if "*" in path_pattern or "?" in path_pattern:
                matched = glob.glob(path_pattern, recursive="**" in path_pattern)
                files.extend(Path(p) for p in matched if Path(p).is_file())
            else:
                path = Path(path_pattern)
                if path.is_file():
                    files.append(path)
                elif path.is_dir():
                    # Get all text files in directory
                    for file in path.rglob("*"):
                        if file.is_file():
                            files.append(file)

        # Filter by extension
        if extensions:
            ext_set = {f".{e.lstrip('.')}" for e in extensions}
            files = [f for f in files if f.suffix.lower() in ext_set]

        # Remove duplicates
        files = list(dict.fromkeys(files))

        # Sort if requested
        if self.sort_files:
            files.sort(key=self._get_sort_key(), reverse=self.reverse_sort)

        return files

    def _read_file(self, filepath: Path) -> Optional[List[str]]:
        try:
            with open(filepath, encoding=self.encoding) as f:
                lines = f.readlines()
            return lines
        except UnicodeDecodeError:
            if self.error_handling == "replace":
                try:
                    with open(
                        filepath, encoding=self.encoding, errors="replace"
                    ) as f:
                        lines = f.readlines()
                    return lines
                except Exception as e:
                    self._handle_error(filepath, e)
                    return None
            else:
                self._handle_error(filepath, "Unicode decode error")
                return None
        except Exception as e:
            self._handle_error(filepath, e)
            return None

    def _handle_error(self, filepath: Path, error):
        error_msg = f"{filepath}: {error}"
        self.stats["errors"].append(error_msg)
        self.stats["files_failed"] += 1

        if self.error_handling == "stop":
            raise RuntimeError(f"Error reading {filepath}: {error}")
        elif self.error_handling == "skip":
            print(f"Warning: Skipping {filepath}: {error}")

    def _format_header(self, filepath: Path, line_count: int, file_size: int) -> str:
        parts = []

        if self.delimiter:
            parts.append(self.delimiter)

        # Filename
        header_line = f"File: {filepath}"

        # Timestamp
        if self.add_timestamp:
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
            header_line += f" (Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')})"

        parts.append(header_line)

        # File stats
        if self.add_file_stats:
            stats_line = f"Lines: {line_count} | Size: {self._format_bytes(file_size)}"
            parts.append(stats_line)

        if self.delimiter:
            parts.append(self.delimiter)

        return "\n".join(parts) + "\n"

    def _process_lines(self, lines: List[str], start_line_num: int = 1) -> List[str]:
        processed = []
        line_num = start_line_num

        for line in lines:
            # Strip whitespace if requested
            if self.strip_whitespace:
                line = line.strip() + "\n"

            # Skip empty lines if requested
            if self.remove_empty_lines and not line.strip():
                continue

            # Add line numbers if requested
            if self.add_line_numbers:
                line = f"{line_num:6d} | {line}"
                line_num += 1

            processed.append(line)

        return processed

    def merge_files(
        self, filepaths: List[Path], output_path: Optional[Path] = None
    ) -> str:
        if not filepaths:
            raise ValueError("No files to merge")

        merged_content = []
        global_line_num = 1

        # Progress bar
        iterator = (
            tqdm(filepaths, desc="Merging files", unit="files")
            if HAS_TQDM
            else filepaths
        )

        for i, filepath in enumerate(iterator):
            # Read file
            lines = self._read_file(filepath)
            if lines is None:
                continue

            # Add header
            if self.add_filename:
                file_size = filepath.stat().st_size
                header = self._format_header(filepath, len(lines), file_size)
                merged_content.append(header)

            # Process and add content
            processed_lines = self._process_lines(lines, global_line_num)
            merged_content.extend(processed_lines)

            global_line_num += len(processed_lines)

            # Add delimiter between files (not after last file)
            if i < len(filepaths) - 1 and self.delimiter and not self.add_filename:
                merged_content.append(self.delimiter + "\n")

            # Update stats
            self.stats["files_processed"] += 1
            self.stats["total_lines"] += len(lines)
            self.stats["total_size"] += filepath.stat().st_size

        # Join all content
        result = "".join(merged_content)

        # Write to file if output path provided
        if output_path:
            with open(output_path, "w", encoding=self.encoding) as f:
                f.write(result)
            print(f"\nMerged content written to: {output_path}")

        return result

    def merge_by_pattern(
        self, pattern: str, output_path: Path, extensions: Optional[List[str]] = None
    ) -> None:
        files = self._collect_files([pattern], extensions)

        if not files:
            print(f"No files found matching pattern: {pattern}")
            return

        print(f"Found {len(files)} file(s) to merge")
        self.merge_files(files, output_path)
        self.print_stats()

    def merge_directories(
        self,
        directories: List[Path],
        output_path: Path,
        extensions: Optional[List[str]] = None,
        recursive: bool = False,
    ) -> None:
        patterns = []
        for directory in directories:
            if recursive:
                patterns.append(str(directory / "**" / "*"))
            else:
                patterns.append(str(directory / "*"))

        files = self._collect_files(patterns, extensions)

        if not files:
            print("No files found in specified directories")
            return

        print(f"Found {len(files)} file(s) across {len(directories)} director(ies)")
        self.merge_files(files, output_path)
        self.print_stats()

    def print_stats(self):
        print("\n" + "=" * 70)
        print("Merge Statistics")
        print("=" * 70)
        print(f"Files processed:     {self.stats['files_processed']}")
        print(f"Files failed:        {self.stats['files_failed']}")
        print(f"Total lines merged:  {self.stats['total_lines']:,}")
        print(f"Total size merged:   {self._format_bytes(self.stats['total_size'])}")

        if self.stats["errors"]:
            print(f"\nErrors ({len(self.stats['errors'])}):")
            for error in self.stats["errors"][:10]:
                print(f"  {error}")
            if len(self.stats["errors"]) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")


def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple text files with customizable delimiters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge all text files in current directory
  python text_merger.py *.txt -o merged.txt

  # Merge with custom delimiter
  python text_merger.py file1.txt file2.txt -o output.txt -d "### NEXT FILE ###"

  # Merge log files with timestamps
  python text_merger.py logs/*.log -o combined.log --timestamp --stats

  # Merge sorted by date (newest first)
  python text_merger.py *.txt -o output.txt --sort date --reverse

  # Merge with line numbers
  python text_merger.py src/*.py -o all_code.py --line-numbers

  # Clean merge (no headers, remove empty lines)
  python text_merger.py *.txt -o clean.txt --no-filename --remove-empty

  # Merge directories recursively
  python text_merger.py logs/ archive/ -o all_logs.txt -r --ext log,txt

Delimiter presets: line, double, hash, star, dash, blank, minimal, section
Sort options: name, size, date, extension
        """,
    )

    parser.add_argument(
        "files", nargs="+", help="Files, directories, or glob patterns to merge"
    )
    parser.add_argument(
        "-o", "--output", type=Path, required=True, help="Output file path"
    )

    # Delimiter options
    parser.add_argument(
        "-d",
        "--delimiter",
        default="line",
        help="Delimiter between files (preset name or custom string)",
    )
    parser.add_argument(
        "--no-filename",
        dest="add_filename",
        action="store_false",
        help="Don't add filename headers",
    )
    parser.add_argument(
        "--timestamp",
        dest="add_timestamp",
        action="store_true",
        help="Add file modification timestamp to headers",
    )
    parser.add_argument(
        "--stats",
        dest="add_stats",
        action="store_true",
        help="Add file statistics (lines, size) to headers",
    )

    # Sorting options
    parser.add_argument(
        "--sort",
        choices=["name", "size", "date", "extension"],
        dest="sort_by",
        help="Sort files before merging",
    )
    parser.add_argument("--reverse", action="store_true", help="Reverse sort order")

    # Content processing
    parser.add_argument(
        "--remove-empty",
        dest="remove_empty",
        action="store_true",
        help="Remove empty lines from output",
    )
    parser.add_argument(
        "--strip",
        dest="strip_whitespace",
        action="store_true",
        help="Strip leading/trailing whitespace from lines",
    )
    parser.add_argument(
        "--line-numbers",
        dest="add_line_numbers",
        action="store_true",
        help="Add line numbers to output",
    )

    # File selection
    parser.add_argument(
        "--ext",
        "--extensions",
        dest="extensions",
        help="Filter by file extensions (comma-separated)",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Process directories recursively"
    )

    # Error handling
    parser.add_argument(
        "--encoding", default="utf-8", help="File encoding (default: utf-8)"
    )
    parser.add_argument(
        "--on-error",
        choices=["skip", "stop", "replace"],
        default="skip",
        dest="error_handling",
        help="How to handle read errors (default: skip)",
    )

    # Preview
    parser.add_argument(
        "--preview", action="store_true", help="Preview merge without writing file"
    )
    parser.add_argument(
        "--preview-lines",
        type=int,
        default=50,
        help="Number of lines to show in preview (default: 50)",
    )

    args = parser.parse_args()

    # Parse extensions
    extensions = None
    if args.extensions:
        extensions = [ext.strip() for ext in args.extensions.split(",")]

    # Check if output exists
    if args.output.exists() and not args.preview:
        response = input(f"Output file exists: {args.output}\nOverwrite? (y/N): ")
        if response.lower() != "y":
            print("Operation cancelled.")
            sys.exit(0)

    try:
        # Initialize merger
        merger = TextMerger(
            delimiter=args.delimiter,
            add_filename=args.add_filename,
            add_timestamp=args.add_timestamp,
            add_file_stats=args.add_stats,
            sort_files=bool(args.sort_by),
            sort_by=args.sort_by or "name",
            reverse_sort=args.reverse,
            remove_empty_lines=args.remove_empty,
            strip_whitespace=args.strip_whitespace,
            add_line_numbers=args.add_line_numbers,
            encoding=args.encoding,
            error_handling=args.error_handling,
        )

        # Collect files
        files = merger._collect_files(args.files, extensions)

        if not files:
            print("No files found matching criteria")
            sys.exit(1)

        print(f"Found {len(files)} file(s) to merge")

        # Preview mode
        if args.preview:
            print("\nPreview of merged content (first lines):")
            print("=" * 70)
            result = merger.merge_files(files)
            lines = result.split("\n")[: args.preview_lines]
            print("\n".join(lines))
            if len(result.split("\n")) > args.preview_lines:
                print(
                    f"\n... ({len(result.split('')) - args.preview_lines} more lines)"
                )
            merger.print_stats()
        else:
            # Actual merge
            merger.merge_files(files, args.output)
            merger.print_stats()

            print(
                f"\n✓ Successfully merged {merger.stats['files_processed']} file(s) to {args.output}"
            )

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
