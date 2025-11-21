from pathlib import Path
from typing import Union


class SafetyError(Exception):
    """Raised when a safety check fails."""

    pass


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


def validate_path(path: Union[str, Path], must_exist: bool = True) -> Path:
    path = Path(path).resolve()

    if must_exist and not path.exists():
        raise ValidationError(f"Path does not exist: {path}")

    # Prevent path traversal attacks
    try:
        path.relative_to(Path.cwd())
    except ValueError:
        # Allow absolute paths but warn
        pass

    return path


def confirm_destructive_action(message: str, force: bool = False) -> bool:
    if force:
        return True

    response = input(f"{message} (y/N): ").strip().lower()
    return response in ("y", "yes")


def check_file_size_limit(path: Path, max_size_mb: int = 100) -> None:
    if not path.exists():
        return

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        raise SafetyError(f"File too large: {size_mb:.1f}MB > {max_size_mb}MB")


def safe_filename(filename: str) -> str:
    import re

    # Remove or replace dangerous characters
    safe = re.sub(r'[<>:"/\\|?*]', "_", filename)
    safe = safe.strip(". ")
    return safe or "unnamed"
