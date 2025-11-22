#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from ..file_management.duplicate_finder import DuplicateFinder


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find and optionally delete duplicate files"
    )
    parser.add_argument("paths", nargs="+", help="Directories or files to scan")
    parser.add_argument(
        "--algorithm",
        choices=DuplicateFinder.ALGORITHMS,
        default="sha256",
        help="Hash algorithm to use (default: sha256)",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=0,
        help="Minimum file size in bytes (default: 0)",
    )
    parser.add_argument(
        "--delete-duplicates",
        action="store_true",
        help="Delete duplicate files (keeps one per group)",
    )
    parser.add_argument(
        "--keep-strategy",
        choices=["first", "last", "shortest_name", "longest_name"],
        default="first",
        help="Strategy for choosing which file to keep",
    )
    parser.add_argument("--export-json", help="Export results to JSON file")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompts")

    args = parser.parse_args()

    # Initialize finder
    finder = DuplicateFinder(args.algorithm, args.min_size)

    # Find duplicates
    paths = [Path(p) for p in args.paths]
    duplicates = finder.find_duplicates(paths)

    if not duplicates:
        print("No duplicates found.")
        return

    # Display results
    total_files = sum(len(files) for files in duplicates.values())
    total_groups = len(duplicates)
    print(f"Found {total_files} duplicate files in {total_groups} groups:")

    for i, (hash_val, files) in enumerate(duplicates.items(), 1):
        print(f"\nGroup {i} ({len(files)} files, hash: {hash_val[:16]}...):")
        for file_path in files:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"  {file_path} ({size_mb:.2f} MB)")

    # Export to JSON if requested
    if args.export_json:
        export_data = {h: [str(f) for f in files] for h, files in duplicates.items()}
        with open(args.export_json, "w") as f:
            json.dump(export_data, f, indent=2)
        print(f"\nResults exported to {args.export_json}")

    # Delete duplicates if requested
    if args.delete_duplicates:
        deleted = finder.delete_duplicates(duplicates, args.keep_strategy, args.yes)
        print(f"\nDeleted {deleted} duplicate files.")


if __name__ == "__main__":
    main()
