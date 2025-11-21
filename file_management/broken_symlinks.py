import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

try:
    from send2trash import send2trash

    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False


class BrokenSymlinkDetector:
    def __init__(
        self,
        follow_symlinks: bool = False,
        check_circular: bool = True,
        max_depth: Optional[int] = None,
    ):
        """
        Args:
            follow_symlinks: Whether to follow symlinks during directory traversal
            check_circular: Check for circular symlink references
            max_depth: Maximum recursion depth (None for unlimited)
        """
        self.follow_symlinks = follow_symlinks
        self.check_circular = check_circular
        self.max_depth = max_depth

        self.stats = {
            "total_symlinks": 0,
            "broken_symlinks": 0,
            "circular_symlinks": 0,
            "valid_symlinks": 0,
            "errors": 0,
        }

        self.broken_links: List[Dict] = []
        self.circular_links: List[Dict] = []
        self.valid_links: List[Dict] = []
        self.errors: List[Dict] = []

    def _is_circular(
        self, symlink_path: Path, visited: Optional[Set[Path]] = None
    ) -> bool:
        if visited is None:
            visited = set()

        if symlink_path in visited:
            return True

        visited.add(symlink_path)

        try:
            target = symlink_path.resolve()
            if target.is_symlink():
                return self._is_circular(target, visited)
        except (OSError, RuntimeError):
            return True

        return False

    def _get_symlink_info(self, symlink_path: Path) -> Dict:
        info = {
            "path": str(symlink_path),
            "name": symlink_path.name,
            "parent": str(symlink_path.parent),
            "target": None,
            "target_exists": False,
            "is_broken": False,
            "is_circular": False,
            "error": None,
        }

        try:
            # Get the raw target path (what the symlink points to)
            target = symlink_path.readlink()
            info["target"] = str(target)

            # Check if target exists
            try:
                resolved = symlink_path.resolve(strict=True)
                info["target_exists"] = True
                info["resolved_target"] = str(resolved)
            except (OSError, FileNotFoundError):
                info["target_exists"] = False
                info["is_broken"] = True

            # Check for circular references
            if self.check_circular and not info["is_broken"]:
                if self._is_circular(symlink_path):
                    info["is_circular"] = True
                    self.stats["circular_symlinks"] += 1

        except OSError as e:
            info["error"] = str(e)
            info["is_broken"] = True
            self.stats["errors"] += 1

        return info

    def _scan_directory(self, path: Path, current_depth: int = 0) -> None:
        if self.max_depth is not None and current_depth > self.max_depth:
            return

        try:
            items = list(path.iterdir())
        except (PermissionError, OSError) as e:
            self.errors.append(
                {"path": str(path), "error": f"Cannot access directory: {e}"}
            )
            self.stats["errors"] += 1
            return

        for item in items:
            try:
                # Check if it's a symlink
                if item.is_symlink():
                    self.stats["total_symlinks"] += 1
                    info = self._get_symlink_info(item)

                    if info["is_circular"]:
                        self.circular_links.append(info)
                    elif info["is_broken"]:
                        self.broken_links.append(info)
                        self.stats["broken_symlinks"] += 1
                    else:
                        self.valid_links.append(info)
                        self.stats["valid_symlinks"] += 1

                # Recurse into directories
                if item.is_dir() and not (
                    item.is_symlink() and not self.follow_symlinks
                ):
                    self._scan_directory(item, current_depth + 1)

            except (PermissionError, OSError) as e:
                self.errors.append({"path": str(item), "error": str(e)})
                self.stats["errors"] += 1

    def scan(self, paths: List[Path]) -> None:
        print("Scanning for symbolic links...")

        all_paths = []
        for path in paths:
            if path.is_symlink():
                all_paths.append(path)
            elif path.is_dir():
                all_paths.append(path)
            elif path.is_file():
                print(f"Warning: {path} is not a symlink or directory, skipping")

        if HAS_TQDM:
            pbar = tqdm(all_paths, desc="Scanning", unit="paths")
        else:
            pbar = all_paths

        for path in pbar:
            if path.is_symlink():
                self.stats["total_symlinks"] += 1
                info = self._get_symlink_info(path)

                if info["is_circular"]:
                    self.circular_links.append(info)
                elif info["is_broken"]:
                    self.broken_links.append(info)
                    self.stats["broken_symlinks"] += 1
                else:
                    self.valid_links.append(info)
                    self.stats["valid_symlinks"] += 1
            else:
                self._scan_directory(path)

    def print_results(
        self, show_valid: bool = False, show_circular: bool = True
    ) -> None:
        print("\n" + "=" * 70)
        print("Symlink Analysis Results")
        print("=" * 70)
        print(f"Total symlinks found:    {self.stats['total_symlinks']}")
        print(f"Valid symlinks:          {self.stats['valid_symlinks']}")
        print(f"Broken symlinks:         {self.stats['broken_symlinks']}")

        if self.check_circular:
            print(f"Circular symlinks:       {self.stats['circular_symlinks']}")

        if self.stats["errors"] > 0:
            print(f"Errors:                  {self.stats['errors']}")

        # Show broken symlinks
        if self.broken_links:
            print("\n" + "-" * 70)
            print("BROKEN SYMLINKS:")
            print("-" * 70)
            for link in self.broken_links:
                print(f"\n  Path: {link['path']}")
                print(f"  Target: {link['target']}")
                if link.get("error"):
                    print(f"  Error: {link['error']}")

        # Show circular symlinks
        if show_circular and self.circular_links:
            print("\n" + "-" * 70)
            print("CIRCULAR SYMLINKS:")
            print("-" * 70)
            for link in self.circular_links:
                print(f"\n  Path: {link['path']}")
                print(f"  Target: {link['target']}")

        # Show valid symlinks
        if show_valid and self.valid_links:
            print("\n" + "-" * 70)
            print("VALID SYMLINKS:")
            print("-" * 70)
            for link in self.valid_links[:20]:
                print(f"\n  Path: {link['path']}")
                print(f"  Target: {link['resolved_target']}")

            if len(self.valid_links) > 20:
                print(f"\n  ... and {len(self.valid_links) - 20} more valid symlinks")

        # Show errors
        if self.errors:
            print("\n" + "-" * 70)
            print("ERRORS:")
            print("-" * 70)
            for error in self.errors[:10]:
                print(f"\n  Path: {error['path']}")
                print(f"  Error: {error['error']}")

            if len(self.errors) > 10:
                print(f"\n  ... and {len(self.errors) - 10} more errors")

    def export_results(self, output_file: str, format: str = "json") -> None:
        data = {
            "stats": self.stats,
            "broken_symlinks": self.broken_links,
            "circular_symlinks": self.circular_links,
            "valid_symlinks": self.valid_links,
            "errors": self.errors,
        }

        output_path = Path(output_file)

        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:  # text
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("Symlink Analysis Report\n")
                f.write("=" * 70 + "\n\n")
                f.write("Statistics:\n")
                for key, value in self.stats.items():
                    f.write(f"  {key}: {value}\n")

                f.write("\n" + "=" * 70 + "\n")
                f.write("BROKEN SYMLINKS:\n")
                f.write("=" * 70 + "\n")
                for link in self.broken_links:
                    f.write(f"\nPath: {link['path']}\n")
                    f.write(f"Target: {link['target']}\n")
                    if link.get("error"):
                        f.write(f"Error: {link['error']}\n")

                if self.circular_links:
                    f.write("\n" + "=" * 70 + "\n")
                    f.write("CIRCULAR SYMLINKS:\n")
                    f.write("=" * 70 + "\n")
                    for link in self.circular_links:
                        f.write(f"\nPath: {link['path']}\n")
                        f.write(f"Target: {link['target']}\n")

        print(f"Results exported to: {output_path}")

    def delete_broken(self, use_trash: bool = True, dry_run: bool = False) -> None:
        if not self.broken_links:
            print("No broken symlinks to delete.")
            return

        if not HAS_SEND2TRASH and use_trash:
            print(
                "Warning: send2trash not installed. Files will be permanently deleted."
            )
            use_trash = False

        print(f"\n{'[DRY RUN] ' if dry_run else ''}Deleting broken symlinks...")

        deleted_count = 0
        error_count = 0

        links_to_delete = self.broken_links + (
            self.circular_links if self.check_circular else []
        )

        for link in links_to_delete:
            link_path = Path(link["path"])

            try:
                if not dry_run:
                    if use_trash:
                        send2trash(str(link_path))
                    else:
                        link_path.unlink()

                print(f"{'Would delete' if dry_run else 'Deleted'}: {link_path}")
                deleted_count += 1

            except OSError as e:
                print(f"Error deleting {link_path}: {e}")
                error_count += 1

        print(
            f"\n{'Would delete' if dry_run else 'Deleted'} {deleted_count} broken symlink(s)"
        )
        if error_count > 0:
            print(f"Errors: {error_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Find and manage broken symbolic links",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find broken symlinks in home directory
  python broken_symlinks.py ~

  # Find and delete broken symlinks (dry run)
  python broken_symlinks.py /path/to/check --delete --dry-run

  # Export results to JSON
  python broken_symlinks.py /path/to/check --output json --file report.json

  # Check specific depth with circular reference detection
  python broken_symlinks.py /path/to/check --max-depth 3 --check-circular

  # Delete broken symlinks (move to trash)
  python broken_symlinks.py /path/to/check --delete --use-trash
        """,
    )

    parser.add_argument(
        "paths", nargs="+", type=Path, help="Directories or symlinks to check"
    )

    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symlinks during directory traversal",
    )
    parser.add_argument(
        "--check-circular",
        action="store_true",
        default=True,
        help="Check for circular symlink references (default: True)",
    )
    parser.add_argument("--max-depth", type=int, help="Maximum recursion depth")

    parser.add_argument(
        "--show-valid", action="store_true", help="Display valid symlinks in output"
    )
    parser.add_argument(
        "--hide-circular",
        action="store_true",
        help="Hide circular symlinks from output",
    )

    parser.add_argument("--delete", action="store_true", help="Delete broken symlinks")
    parser.add_argument(
        "--use-trash",
        action="store_true",
        default=True,
        help="Move to trash instead of permanent deletion (default: True)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )

    parser.add_argument(
        "--output", choices=["json", "text"], help="Export results to file"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="broken_symlinks_report",
        help="Output filename (without extension)",
    )

    args = parser.parse_args()

    # Validate paths
    for path in args.paths:
        if not path.exists():
            print(f"Warning: Path does not exist: {path}")

    try:
        # Initialize detector
        detector = BrokenSymlinkDetector(
            follow_symlinks=args.follow_symlinks,
            check_circular=args.check_circular,
            max_depth=args.max_depth,
        )

        # Scan for broken symlinks
        start_time = time.time()
        detector.scan(args.paths)
        elapsed_time = time.time() - start_time

        # Display results
        detector.print_results(
            show_valid=args.show_valid, show_circular=not args.hide_circular
        )

        print(f"\nScan completed in {elapsed_time:.2f}s")

        # Export results
        if args.output:
            output_file = f"{args.file}.{args.output}"
            detector.export_results(output_file, args.output)

        # Handle deletion
        if args.delete:
            if not args.dry_run and detector.broken_links:
                confirm = input(
                    f"\nDelete {len(detector.broken_links)} broken symlink(s)? (y/N): "
                )
                if confirm.lower() != "y":
                    print("Deletion cancelled.")
                    return

            detector.delete_broken(use_trash=args.use_trash, dry_run=args.dry_run)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
