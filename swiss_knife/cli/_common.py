"""Shared helpers for packaged CLI entry points."""

from __future__ import annotations

import argparse


def add_version_argument(parser: argparse.ArgumentParser, prog: str) -> None:
    from .. import __version__

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"{prog} {__version__}",
    )
