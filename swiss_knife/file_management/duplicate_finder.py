import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from ..core import SafetyError, confirm_destructive_action, validate_path


class DuplicateFinder:
    ALGORITHMS = ["md5", "sha1", "sha256", "sha512"]

    def __init__(self, algorithm: str = "sha256", min_size: int = 0):
        """
        Args:
            algorithm: Hash algorithm to use
            min_size: Minimum file size in bytes
        """
        if algorithm not in self.ALGORITHMS:
            raise ValueError(f"Algorithm must be one of {self.ALGORITHMS}")

        self.algorithm = algorithm
        self.min_size = min_size
        self._hash_func = getattr(hashlib, algorithm)

    def _calculate_hash(self, file_path: Path) -> str:
        hash_obj = self._hash_func()

        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except OSError as e:
            raise SafetyError(f"Cannot read file {file_path}: {e}")

    def find_duplicates(self, paths: List[Path]) -> Dict[str, List[Path]]:
        """

        Args:
            paths: List of directories or files to scan

        Returns:
            Dictionary mapping hash to list of duplicate files
        """
        file_hashes = defaultdict(list)

        for path in paths:
            path = validate_path(path)

            if path.is_file():
                files = [path]
            else:
                files = path.rglob("*")

            for file_path in files:
                if not file_path.is_file():
                    continue

                try:
                    size = file_path.stat().st_size
                    if size < self.min_size:
                        continue

                    file_hash = self._calculate_hash(file_path)
                    file_hashes[file_hash].append(file_path)

                except (OSError, SafetyError):
                    continue  # Skip files we can't read

        # Return only groups with duplicates
        return {h: files for h, files in file_hashes.items() if len(files) > 1}

    def delete_duplicates(
        self,
        duplicates: Dict[str, List[Path]],
        keep_strategy: str = "first",
        force: bool = False,
    ) -> int:
        """

        Args:
            duplicates: Result from find_duplicates()
            keep_strategy: 'first', 'last', 'shortest_name', 'longest_name'
            force: Skip confirmation prompts

        Returns:
            Number of files deleted
        """
        if not duplicates:
            return 0

        total_files = sum(len(files) for files in duplicates.values())
        groups = len(duplicates)

        if not confirm_destructive_action(
            f"Delete {total_files - groups} duplicate files from {groups} groups?",
            force,
        ):
            return 0

        deleted = 0
        for files in duplicates.values():
            if len(files) <= 1:
                continue

            # Choose file to keep based on strategy
            if keep_strategy == "first":
                keep = files[0]
            elif keep_strategy == "last":
                keep = files[-1]
            elif keep_strategy == "shortest_name":
                keep = min(files, key=lambda f: len(f.name))
            elif keep_strategy == "longest_name":
                keep = max(files, key=lambda f: len(f.name))
            else:
                raise ValueError(f"Unknown keep strategy: {keep_strategy}")

            # Delete all others
            for file_path in files:
                if file_path != keep:
                    try:
                        file_path.unlink()
                        deleted += 1
                    except OSError:
                        continue

        return deleted


def find_duplicates(
    paths: List[str], algorithm: str = "sha256", min_size: int = 0
) -> Dict[str, List[str]]:
    """

    Args:
        paths: List of directory or file paths
        algorithm: Hash algorithm to use
        min_size: Minimum file size in bytes

    Returns:
        Dictionary mapping hash to list of duplicate file paths
    """
    finder = DuplicateFinder(algorithm, min_size)
    path_objects = [Path(p) for p in paths]
    duplicates = finder.find_duplicates(path_objects)

    # Convert back to strings
    return {h: [str(f) for f in files] for h, files in duplicates.items()}
