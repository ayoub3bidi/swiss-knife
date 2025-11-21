import re
from collections import Counter
from pathlib import Path
from typing import List, Tuple

from ..core import SafetyError, confirm_destructive_action, safe_filename, validate_path


class BulkRenamer:

    def __init__(self, dry_run: bool = False):
        """

        Args:
            dry_run: If True, only show what would be renamed
        """
        self.dry_run = dry_run
        self.operations = []

    def add_pattern(
        self, pattern: str, replacement: str, target_dir: Path, recursive: bool = False
    ) -> List[Tuple[Path, Path]]:
        """

        Args:
            pattern: Regex pattern to match
            replacement: Replacement string (can use regex groups)
            target_dir: Directory to process
            recursive: Process subdirectories

        Returns:
            List of (old_path, new_path) tuples
        """
        target_dir = validate_path(target_dir)

        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise SafetyError(f"Invalid regex pattern: {e}")

        operations = []

        if recursive:
            files = target_dir.rglob("*")
        else:
            files = target_dir.iterdir()

        for file_path in files:
            if not file_path.is_file():
                continue

            old_name = file_path.name
            match = regex.search(old_name)

            if match:
                try:
                    new_name = regex.sub(replacement, old_name)
                    new_name = safe_filename(new_name)

                    if new_name != old_name:
                        new_path = file_path.parent / new_name
                        operations.append((file_path, new_path))

                except re.error as e:
                    raise SafetyError(f"Replacement error for {old_name}: {e}")

        # Check for collisions
        new_names = [op[1].name for op in operations]
        duplicates = [name for name, count in Counter(new_names).items() if count > 1]

        if duplicates:
            raise SafetyError(f"Name collisions detected: {duplicates}")

        # Check for existing files
        existing = [op[1] for op in operations if op[1].exists()]
        if existing:
            raise SafetyError(
                f"Target files already exist: {[str(p) for p in existing]}"
            )

        self.operations.extend(operations)
        return operations

    def execute(self, force: bool = False) -> int:
        """

        Args:
            force: Skip confirmation prompts

        Returns:
            Number of files renamed
        """
        if not self.operations:
            return 0

        if self.dry_run:
            print("DRY RUN - No files will be renamed:")
            for old_path, new_path in self.operations:
                print(f"  {old_path.name} -> {new_path.name}")
            return 0

        if not confirm_destructive_action(
            f"Rename {len(self.operations)} files?", force
        ):
            return 0

        renamed = 0
        for old_path, new_path in self.operations:
            try:
                old_path.rename(new_path)
                renamed += 1
            except OSError as e:
                print(f"Failed to rename {old_path}: {e}")
                continue

        self.operations.clear()
        return renamed


def bulk_rename(
    pattern: str,
    replacement: str,
    target_dir: str,
    recursive: bool = False,
    dry_run: bool = False,
) -> int:
    """

    Args:
        pattern: Regex pattern to match
        replacement: Replacement string
        target_dir: Directory to process
        recursive: Process subdirectories
        dry_run: Only show what would be renamed

    Returns:
        Number of files renamed (0 for dry run)
    """
    renamer = BulkRenamer(dry_run=dry_run)
    operations = renamer.add_pattern(pattern, replacement, Path(target_dir), recursive)

    if dry_run:
        print(f"Would rename {len(operations)} files:")
        for old_path, new_path in operations:
            print(f"  {old_path.name} -> {new_path.name}")
        return 0

    return renamer.execute()
