#!/usr/bin/env python3

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from tqdm import tqdm  # noqa: F401

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


@dataclass
class FileStats:
    path: str
    size: int
    is_dir: bool
    file_count: int = 0
    dir_count: int = 0
    largest_file: Optional[str] = None
    largest_file_size: int = 0
    extension_stats: Dict[str, Dict] = None

    def __post_init__(self):
        if self.extension_stats is None:
            self.extension_stats = {}


class DiskAnalyzer:
    def __init__(
        self,
        min_size: int = 0,
        max_depth: Optional[int] = None,
        include_hidden: bool = False,
        follow_symlinks: bool = False,
    ):
        """
        Args:
            min_size: Minimum size in bytes to include
            max_depth: Maximum directory depth (None = unlimited)
            include_hidden: Include hidden files/directories
            follow_symlinks: Follow symbolic links
        """
        self.min_size = min_size
        self.max_depth = max_depth
        self.include_hidden = include_hidden
        self.follow_symlinks = follow_symlinks

        self.total_size = 0
        self.total_files = 0
        self.total_dirs = 0
        self.extension_stats = defaultdict(lambda: {"count": 0, "size": 0})
        self.largest_files: List[Tuple[int, str]] = []
        self.errors: List[Tuple[str, str]] = []

    def _format_size(self, bytes_val: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_val < 1024:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.2f} PB"

    def _should_include(self, path: Path) -> bool:
        if not self.include_hidden and path.name.startswith("."):
            return False
        return True

    def _get_directory_size(self, path: Path, current_depth: int = 0) -> FileStats:
        total_size = 0
        file_count = 0
        dir_count = 0
        largest_file = None
        largest_size = 0
        extension_stats = defaultdict(lambda: {"count": 0, "size": 0})

        try:
            items = list(path.iterdir())
        except (PermissionError, OSError) as e:
            self.errors.append((str(path), str(e)))
            return FileStats(str(path), 0, True, 0, 0)

        for item in items:
            try:
                # Skip hidden files if needed
                if not self._should_include(item):
                    continue

                # Handle symlinks
                if item.is_symlink():
                    if not self.follow_symlinks:
                        continue
                    try:
                        item = item.resolve()
                    except (OSError, RuntimeError):
                        continue

                if item.is_file():
                    size = item.stat().st_size
                    total_size += size
                    file_count += 1
                    self.total_files += 1

                    # Track largest file
                    if size > largest_size:
                        largest_size = size
                        largest_file = str(item)

                    # Track by extension
                    ext = item.suffix.lower() or "[no extension]"
                    extension_stats[ext]["count"] += 1
                    extension_stats[ext]["size"] += size
                    self.extension_stats[ext]["count"] += 1
                    self.extension_stats[ext]["size"] += size

                    # Track globally largest files
                    self.largest_files.append((size, str(item)))

                elif item.is_dir():
                    dir_count += 1
                    self.total_dirs += 1

                    # Recurse if within depth limit
                    if self.max_depth is None or current_depth < self.max_depth:
                        subdir_stats = self._get_directory_size(item, current_depth + 1)
                        total_size += subdir_stats.size
                        file_count += subdir_stats.file_count
                        dir_count += subdir_stats.dir_count

                        # Merge extension stats
                        for ext, stats in subdir_stats.extension_stats.items():
                            extension_stats[ext]["count"] += stats["count"]
                            extension_stats[ext]["size"] += stats["size"]

                        # Update largest file
                        if subdir_stats.largest_file_size > largest_size:
                            largest_size = subdir_stats.largest_file_size
                            largest_file = subdir_stats.largest_file

            except (PermissionError, OSError) as e:
                self.errors.append((str(item), str(e)))
                continue

        self.total_size += total_size

        return FileStats(
            path=str(path),
            size=total_size,
            is_dir=True,
            file_count=file_count,
            dir_count=dir_count,
            largest_file=largest_file,
            largest_file_size=largest_size,
            extension_stats=dict(extension_stats),
        )

    def analyze_directory(self, path: Path) -> FileStats:
        print(f"Analyzing: {path}")

        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")

        if path.is_file():
            size = path.stat().st_size
            self.total_size = size
            self.total_files = 1
            return FileStats(str(path), size, False, 1, 0)

        return self._get_directory_size(path)

    def get_subdirectory_sizes(
        self, path: Path, top_n: int = 20
    ) -> List[Tuple[str, int]]:
        subdir_sizes = []

        try:
            for item in path.iterdir():
                if not self._should_include(item):
                    continue

                if item.is_dir():
                    try:
                        size = sum(
                            f.stat().st_size
                            for f in item.rglob("*")
                            if f.is_file() and self._should_include(f)
                        )
                        subdir_sizes.append((str(item.name), size))
                    except (PermissionError, OSError) as e:
                        self.errors.append((str(item), str(e)))
        except (PermissionError, OSError) as e:
            self.errors.append((str(path), str(e)))

        return sorted(subdir_sizes, key=lambda x: x[1], reverse=True)[:top_n]

    def print_tree_view(
        self,
        stats: FileStats,
        indent: int = 0,
        max_items: int = 10,
        size_threshold: float = 0.01,
    ):
        prefix = "  " * indent
        size_str = self._format_size(stats.size)
        percent = (stats.size / self.total_size * 100) if self.total_size > 0 else 0

        print(
            f"{prefix}├── {Path(stats.path).name or stats.path} ({size_str}, {percent:.1f}%)"
        )

        # Show subdirectories if they're significant
        path = Path(stats.path)
        if path.is_dir() and indent < 3:  # Limit depth for readability
            try:
                subdirs = self.get_subdirectory_sizes(path, top_n=max_items)
                significant = [
                    (n, s) for n, s in subdirs if s / self.total_size > size_threshold
                ]

                for name, size in significant[:max_items]:
                    percent = (
                        (size / self.total_size * 100) if self.total_size > 0 else 0
                    )
                    print(
                        f"{prefix}  ├── {name} ({self._format_size(size)}, {percent:.1f}%)"
                    )
            except Exception:
                pass

    def print_bar_chart(
        self,
        data: List[Tuple[str, int]],
        title: str,
        max_width: int = 50,
        top_n: int = 15,
    ):
        if not data:
            return

        print(f"\n{title}")
        print("=" * 80)

        # Take top N and calculate percentages
        top_items = data[:top_n]
        max_size = max(size for _, size in top_items)

        for name, size in top_items:
            # Truncate long names
            display_name = name if len(name) <= 40 else name[:37] + "..."

            # Calculate bar length
            if max_size > 0:
                bar_length = int((size / max_size) * max_width)
            else:
                bar_length = 0

            bar = "█" * bar_length
            size_str = self._format_size(size)
            percent = (size / self.total_size * 100) if self.total_size > 0 else 0

            print(
                f"{display_name:<42} {bar:<{max_width}} {size_str:>12} ({percent:>5.1f}%)"
            )

    def print_summary(self, stats: FileStats):
        print("\n" + "=" * 80)
        print("DISK SPACE ANALYSIS SUMMARY")
        print("=" * 80)

        print(f"\nPath: {stats.path}")
        print(f"Total Size: {self._format_size(self.total_size)}")
        print(f"Files: {self.total_files:,}")
        print(f"Directories: {self.total_dirs:,}")

        if self.errors:
            print(f"Errors: {len(self.errors)}")

        # Extension breakdown
        if self.extension_stats:
            ext_list = [
                (ext, data["size"], data["count"])
                for ext, data in self.extension_stats.items()
            ]
            ext_list.sort(key=lambda x: x[1], reverse=True)

            self.print_bar_chart(
                [(f"{ext} ({count:,} files)", size) for ext, size, count in ext_list],
                "TOP FILE TYPES BY SIZE",
                top_n=15,
            )

        # Largest files
        if self.largest_files:
            self.largest_files.sort(reverse=True)
            largest = [
                (Path(path).name, size) for size, path in self.largest_files[:20]
            ]
            self.print_bar_chart(largest, "LARGEST FILES", top_n=20)

        # Subdirectories
        path = Path(stats.path)
        if path.is_dir():
            subdirs = self.get_subdirectory_sizes(path, top_n=20)
            if subdirs:
                self.print_bar_chart(subdirs, "SUBDIRECTORIES BY SIZE", top_n=20)

        # Errors
        if self.errors:
            print(f"\n⚠️  ERRORS ({len(self.errors)}):")
            for path, error in self.errors[:10]:
                print(f"  {path}: {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")

    def export_json(self, stats: FileStats, output_file: str):
        data = {
            "summary": {
                "path": stats.path,
                "total_size": self.total_size,
                "total_size_formatted": self._format_size(self.total_size),
                "total_files": self.total_files,
                "total_directories": self.total_dirs,
                "errors": len(self.errors),
            },
            "extension_stats": {
                ext: {
                    "count": data["count"],
                    "size": data["size"],
                    "size_formatted": self._format_size(data["size"]),
                    "percentage": (data["size"] / self.total_size * 100)
                    if self.total_size > 0
                    else 0,
                }
                for ext, data in sorted(
                    self.extension_stats.items(),
                    key=lambda x: x[1]["size"],
                    reverse=True,
                )
            },
            "largest_files": [
                {
                    "path": path,
                    "size": size,
                    "size_formatted": self._format_size(size),
                    "percentage": (size / self.total_size * 100)
                    if self.total_size > 0
                    else 0,
                }
                for size, path in sorted(self.largest_files, reverse=True)[:100]
            ],
            "subdirectories": [
                {
                    "name": name,
                    "size": size,
                    "size_formatted": self._format_size(size),
                    "percentage": (size / self.total_size * 100)
                    if self.total_size > 0
                    else 0,
                }
                for name, size in self.get_subdirectory_sizes(
                    Path(stats.path), top_n=100
                )
            ],
            "errors": [
                {"path": path, "error": error} for path, error in self.errors[:100]
            ],
        }

        output_path = Path(output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nReport exported to: {output_path}")


def parse_size(size_str: str) -> int:
    size_str = size_str.upper().strip()

    multipliers = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}

    for unit, multiplier in multipliers.items():
        if size_str.endswith(unit):
            number = float(size_str[: -len(unit)])
            return int(number * multiplier)

    return int(size_str)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze disk space usage with visual reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current directory
  python disk_analyzer.py .

  # Analyze with depth limit
  python disk_analyzer.py /home/user --max-depth 3

  # Include hidden files
  python disk_analyzer.py /home/user --include-hidden

  # Analyze large directories only
  python disk_analyzer.py /var --min-size 100MB

  # Export detailed report
  python disk_analyzer.py /home/user --export report.json

  # Follow symbolic links
  python disk_analyzer.py /usr --follow-symlinks
        """,
    )

    parser.add_argument("path", type=Path, help="Directory or file to analyze")

    parser.add_argument(
        "--min-size",
        type=str,
        default="0",
        help="Minimum size to include (e.g., 10MB, 1GB)",
    )
    parser.add_argument(
        "--max-depth", type=int, help="Maximum directory depth to analyze"
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories",
    )
    parser.add_argument(
        "--follow-symlinks", action="store_true", help="Follow symbolic links"
    )

    parser.add_argument(
        "--export", type=str, help="Export detailed report to JSON file"
    )
    parser.add_argument(
        "--top", type=int, default=20, help="Number of top items to show (default: 20)"
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}")
        sys.exit(1)

    try:
        # Parse min size
        min_size = parse_size(args.min_size)

        # Initialize analyzer
        analyzer = DiskAnalyzer(
            min_size=min_size,
            max_depth=args.max_depth,
            include_hidden=args.include_hidden,
            follow_symlinks=args.follow_symlinks,
        )

        # Analyze
        stats = analyzer.analyze_directory(args.path)

        # Print results
        analyzer.print_summary(stats)

        # Export if requested
        if args.export:
            analyzer.export_json(stats, args.export)

    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
