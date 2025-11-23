#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from ..file_management.bulk_renamer import BulkRenamer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bulk rename files using regex patterns"
    )
    parser.add_argument("pattern", help="Regex pattern to match filenames")
    parser.add_argument("replacement", help="Replacement string (can use regex groups)")
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to process (default: current directory)",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Process subdirectories recursively",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be renamed without making changes",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompts",
    )

    args = parser.parse_args()

    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory does not exist: {args.directory}", file=sys.stderr)
        sys.exit(1)

    if not directory.is_dir():
        print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
        sys.exit(1)

    # Initialize renamer
    renamer = BulkRenamer(dry_run=args.dry_run)

    try:
        # Add rename pattern
        operations = renamer.add_pattern(
            args.pattern, args.replacement, directory, args.recursive
        )

        if not operations:
            print("No files match the pattern.")
            return

        # Show what will be renamed
        print(f"{'DRY RUN - ' if args.dry_run else ''}Found {len(operations)} file(s) to rename:")
        for old_path, new_path in operations:
            print(f"  {old_path.name} → {new_path.name}")

        if args.dry_run:
            print("\nRun without --dry-run to perform the renaming.")
            return

        # Execute rename
        renamed_count = renamer.execute(force=args.yes)
        print(f"\nSuccessfully renamed {renamed_count} file(s).")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
