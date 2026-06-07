#!/usr/bin/env python3
"""Umbrella CLI for package identity (version/help) and tool listing."""

from __future__ import annotations

import argparse
import sys

from ._common import add_version_argument

INSTALLED_TOOLS: tuple[tuple[str, str], ...] = (
    ("sk-duplicates", "Find duplicate files"),
    ("sk-csv", "Convert CSV files"),
    ("sk-password", "Generate secure passwords"),
    ("sk-rename", "Bulk rename files"),
)


def _format_tools_section() -> str:
    name_width = max(len(name) for name, _ in INSTALLED_TOOLS)
    lines = ["Installed tools:"]
    for name, description in INSTALLED_TOOLS:
        lines.append(f"  {name:<{name_width}}  {description}")
    return "\n".join(lines)


def _format_examples_section() -> str:
    return "\n".join(
        [
            "Examples:",
            "  sk-duplicates ~/Documents",
            "  sk-password --length 16",
            "  sk-csv data.csv --format json -o data.json",
        ]
    )


def _build_parser() -> argparse.ArgumentParser:
    epilog = f"{_format_tools_section()}\n\n{_format_examples_section()}"
    parser = argparse.ArgumentParser(
        prog="sk",
        description="Swiss Knife automation tools",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_version_argument(parser, "swiss-knife")
    return parser


def main() -> None:
    parser = _build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        raise SystemExit(0)
    parser.parse_args()


if __name__ == "__main__":
    main()
