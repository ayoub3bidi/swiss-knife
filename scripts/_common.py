"""Shared helpers for standalone repository scripts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def read_repo_version() -> str:
    """Return package/repo version from installed metadata or swiss_knife/__init__.py."""
    try:
        from importlib.metadata import PackageNotFoundError, version

        return version("swiss-knife-py")
    except (ImportError, PackageNotFoundError):
        pass

    repo_root = Path(__file__).resolve().parents[1]
    init_py = repo_root / "swiss_knife" / "__init__.py"
    if init_py.is_file():
        match = re.search(
            r'__version__\s*=\s*"([^"]+)"',
            init_py.read_text(encoding="utf-8"),
        )
        if match:
            return match.group(1)

    pyproject = repo_root / "pyproject.toml"
    if pyproject.is_file():
        match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject.read_text(encoding="utf-8"), re.MULTILINE)
        if match:
            return match.group(1)

    return "0.0.0+unknown"


def add_version_argument(
    parser: argparse.ArgumentParser,
    prog: str,
    *,
    include_long: bool = True,
) -> None:
    version_kwargs = {
        "action": "version",
        "version": f"{prog} {read_repo_version()}",
    }
    if include_long:
        parser.add_argument("-V", "--version", **version_kwargs)
    else:
        parser.add_argument("-V", **version_kwargs)


def ensure_scripts_importable() -> None:
    """Add repo root to sys.path so standalone scripts can import scripts._common."""
    repo_root = str(Path(__file__).resolve().parents[1])
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
