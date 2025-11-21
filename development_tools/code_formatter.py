#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class CodeFormatter:
    FORMATTERS = {
        "python": {
            "tool": "ruff",
            "extensions": [".py"],
            "check_cmd": ["ruff", "--version"],
            "format_cmd": ["ruff", "{file}"],
            "check_only_cmd": ["ruff", "--check", "{file}"],
            "install": "pip install ruff",
        },
        "javascript": {
            "tool": "prettier",
            "extensions": [".js", ".jsx", ".mjs"],
            "check_cmd": ["prettier", "--version"],
            "format_cmd": ["prettier", "--write", "{file}"],
            "check_only_cmd": ["prettier", "--check", "{file}"],
            "install": "npm install -g prettier",
        },
        "typescript": {
            "tool": "prettier",
            "extensions": [".ts", ".tsx"],
            "check_cmd": ["prettier", "--version"],
            "format_cmd": ["prettier", "--write", "{file}"],
            "check_only_cmd": ["prettier", "--check", "{file}"],
            "install": "npm install -g prettier",
        },
        "json": {
            "tool": "prettier",
            "extensions": [".json"],
            "check_cmd": ["prettier", "--version"],
            "format_cmd": ["prettier", "--write", "{file}"],
            "check_only_cmd": ["prettier", "--check", "{file}"],
            "install": "npm install -g prettier",
        },
        "html": {
            "tool": "prettier",
            "extensions": [".html", ".htm"],
            "check_cmd": ["prettier", "--version"],
            "format_cmd": ["prettier", "--write", "{file}"],
            "check_only_cmd": ["prettier", "--check", "{file}"],
            "install": "npm install -g prettier",
        },
        "css": {
            "tool": "prettier",
            "extensions": [".css", ".scss", ".sass", ".less"],
            "check_cmd": ["prettier", "--version"],
            "format_cmd": ["prettier", "--write", "{file}"],
            "check_only_cmd": ["prettier", "--check", "{file}"],
            "install": "npm install -g prettier",
        },
        "cpp": {
            "tool": "clang-format",
            "extensions": [".cpp", ".cc", ".cxx", ".c", ".h", ".hpp"],
            "check_cmd": ["clang-format", "--version"],
            "format_cmd": ["clang-format", "-i", "{file}"],
            "check_only_cmd": ["clang-format", "--dry-run", "-Werror", "{file}"],
            "install": "apt-get install clang-format (Ubuntu) or brew install clang-format (macOS)",
        },
        "java": {
            "tool": "google-java-format",
            "extensions": [".java"],
            "check_cmd": ["google-java-format", "--version"],
            "format_cmd": ["google-java-format", "-i", "{file}"],
            "check_only_cmd": [
                "google-java-format",
                "--dry-run",
                "--set-exit-if-changed",
                "{file}",
            ],
            "install": "Download from https://github.com/google/google-java-format",
        },
        "go": {
            "tool": "gofmt",
            "extensions": [".go"],
            "check_cmd": ["gofmt", "-h"],
            "format_cmd": ["gofmt", "-w", "{file}"],
            "check_only_cmd": ["gofmt", "-l", "{file}"],
            "install": "Included with Go installation",
        },
        "rust": {
            "tool": "rustfmt",
            "extensions": [".rs"],
            "check_cmd": ["rustfmt", "--version"],
            "format_cmd": ["rustfmt", "{file}"],
            "check_only_cmd": ["rustfmt", "--check", "{file}"],
            "install": "rustup component add rustfmt",
        },
        "yaml": {
            "tool": "prettier",
            "extensions": [".yaml", ".yml"],
            "check_cmd": ["prettier", "--version"],
            "format_cmd": ["prettier", "--write", "{file}"],
            "check_only_cmd": ["prettier", "--check", "{file}"],
            "install": "npm install -g prettier",
        },
        "markdown": {
            "tool": "prettier",
            "extensions": [".md"],
            "check_cmd": ["prettier", "--version"],
            "format_cmd": ["prettier", "--write", "{file}"],
            "check_only_cmd": ["prettier", "--check", "{file}"],
            "install": "npm install -g prettier",
        },
    }

    def __init__(self, check_only: bool = False, verbose: bool = False):
        self.check_only = check_only
        self.verbose = verbose

        self.stats = {
            "files_checked": 0,
            "files_formatted": 0,
            "files_failed": 0,
            "files_skipped": 0,
            "needs_formatting": 0,
        }

        self.results: List[Dict] = []
        self.available_formatters = self._check_formatters()

    def _check_formatters(self) -> Dict[str, bool]:
        available = {}

        for lang, config in self.FORMATTERS.items():
            try:
                subprocess.run(
                    config["check_cmd"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                )
                available[lang] = True
            except (subprocess.SubprocessError, FileNotFoundError):
                available[lang] = False

        return available

    def _detect_language(self, filepath: Path) -> Optional[str]:
        ext = filepath.suffix.lower()

        for lang, config in self.FORMATTERS.items():
            if ext in config["extensions"]:
                return lang

        return None

    def _format_file(self, filepath: Path, language: str) -> Dict:
        result = {
            "file": str(filepath),
            "language": language,
            "status": "unknown",
            "formatted": False,
            "error": None,
        }

        config = self.FORMATTERS[language]

        # Check if formatter is available
        if not self.available_formatters.get(language, False):
            result["status"] = "no_formatter"
            result["error"] = (
                f"{config['tool']} not installed. Install: {config['install']}"
            )
            self.stats["files_skipped"] += 1
            return result

        # Choose command based on check_only flag
        if self.check_only:
            cmd = [
                c.format(file=str(filepath)) if "{file}" in c else c
                for c in config["check_only_cmd"]
            ]
        else:
            cmd = [
                c.format(file=str(filepath)) if "{file}" in c else c
                for c in config["format_cmd"]
            ]

        try:
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if process.returncode == 0:
                if self.check_only:
                    result["status"] = "ok"
                    result["formatted"] = False
                else:
                    result["status"] = "formatted"
                    result["formatted"] = True
                    self.stats["files_formatted"] += 1
            else:
                if self.check_only:
                    result["status"] = "needs_formatting"
                    result["formatted"] = False
                    self.stats["needs_formatting"] += 1
                else:
                    result["status"] = "error"
                    result["error"] = process.stderr or process.stdout
                    self.stats["files_failed"] += 1

        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["error"] = "Formatting timeout"
            self.stats["files_failed"] += 1

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.stats["files_failed"] += 1

        return result

    def format_files(self, filepaths: List[Path]) -> List[Dict]:
        # Detect languages and filter
        files_to_format = []

        for filepath in filepaths:
            if not filepath.exists():
                continue

            if not filepath.is_file():
                continue

            language = self._detect_language(filepath)
            if language:
                files_to_format.append((filepath, language))

        if not files_to_format:
            print("No supported files found")
            return []

        # Format files
        mode = "Checking" if self.check_only else "Formatting"
        iterator = (
            tqdm(files_to_format, desc=mode, unit="file")
            if HAS_TQDM
            else files_to_format
        )

        for filepath, language in iterator:
            self.stats["files_checked"] += 1
            result = self._format_file(filepath, language)
            self.results.append(result)

            if self.verbose:
                self._print_result(result)

        return self.results

    def format_directory(
        self,
        directory: Path,
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[Dict]:
        files = []

        # Default exclusions
        exclude = exclude_patterns or []
        exclude.extend(
            ["node_modules", ".git", "__pycache__", "venv", ".venv", "dist", "build"]
        )

        # Collect files
        pattern = "**/*" if recursive else "*"
        for filepath in directory.glob(pattern):
            if not filepath.is_file():
                continue

            # Check exclusions
            if any(excl in str(filepath) for excl in exclude):
                continue

            if self._detect_language(filepath):
                files.append(filepath)

        if not files:
            print(f"No supported files found in {directory}")
            return []

        print(f"Found {len(files)} file(s) to format")
        return self.format_files(files)

    def _print_result(self, result: Dict):
        status_icons = {
            "ok": "✓",
            "formatted": "✓",
            "needs_formatting": "⚠",
            "error": "✗",
            "no_formatter": "⊘",
            "timeout": "⏱",
        }

        icon = status_icons.get(result["status"], "?")
        print(f"{icon} {result['file']} [{result['language']}]")

        if result["error"]:
            print(f"  Error: {result['error']}")

    def print_summary(self):
        print("\n" + "=" * 80)
        print("FORMATTING SUMMARY")
        print("=" * 80)
        print(f"Files checked:      {self.stats['files_checked']}")

        if self.check_only:
            print(
                f"Files OK:           {self.stats['files_checked'] - self.stats['needs_formatting']}"
            )
            print(f"Needs formatting:   {self.stats['needs_formatting']}")
        else:
            print(f"Files formatted:    {self.stats['files_formatted']}")

        print(f"Files failed:       {self.stats['files_failed']}")
        print(f"Files skipped:      {self.stats['files_skipped']}")

        # Show missing formatters
        missing = [
            lang
            for lang, available in self.available_formatters.items()
            if not available
        ]
        if missing:
            print(f"\nMissing formatters: {', '.join(missing)}")

    def export_json(self, output_path: Path):
        data = {
            "timestamp": datetime.now().isoformat(),
            "mode": "check" if self.check_only else "format",
            "statistics": self.stats,
            "formatters": self.available_formatters,
            "results": self.results,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"\nResults exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Format code files using language-specific formatters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported Languages:
  Python      (.py)          - Ruff
  JavaScript  (.js, .jsx)    - Prettier
  TypeScript  (.ts, .tsx)    - Prettier
  JSON        (.json)        - Prettier
  HTML        (.html)        - Prettier
  CSS         (.css, .scss)  - Prettier
  C/C++       (.c, .cpp, .h) - clang-format
  Java        (.java)        - google-java-format
  Go          (.go)          - gofmt
  Rust        (.rs)          - rustfmt
  YAML        (.yaml, .yml)  - Prettier
  Markdown    (.md)          - Prettier

Examples:
  # Format single file
  python code_formatter.py script.py

  # Format multiple files
  python code_formatter.py src/app.js src/utils.js

  # Format entire directory
  python code_formatter.py src/

  # Format directory recursively
  python code_formatter.py src/ --recursive

  # Check only (don't modify)
  python code_formatter.py src/ --check

  # Exclude patterns
  python code_formatter.py . --recursive --exclude tests,docs

  # Verbose output
  python code_formatter.py src/ --verbose

  # Export results
  python code_formatter.py src/ --export-json format_report.json
""",
    )

    parser.add_argument(
        "paths", nargs="+", type=Path, help="Files or directories to format"
    )

    parser.add_argument(
        "--check", action="store_true", help="Check formatting without modifying files"
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Format directories recursively"
    )
    parser.add_argument(
        "--exclude", type=str, help="Exclude patterns (comma-separated)"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--export-json", type=Path, help="Export results to JSON")

    parser.add_argument(
        "--list-formatters",
        action="store_true",
        help="List available formatters and exit",
    )

    args = parser.parse_args()

    # Initialize formatter
    formatter = CodeFormatter(check_only=args.check, verbose=args.verbose)

    # List formatters and exit
    if args.list_formatters:
        print("Available Formatters:")
        print("=" * 80)
        for lang, available in sorted(formatter.available_formatters.items()):
            config = formatter.FORMATTERS[lang]
            status = "✓ Installed" if available else "✗ Not installed"
            print(f"{lang:15s} {config['tool']:20s} {status}")
            if not available:
                print(f"  Install: {config['install']}")
        sys.exit(0)

    # Parse exclude patterns
    exclude = None
    if args.exclude:
        exclude = [p.strip() for p in args.exclude.split(",")]

    try:
        # Collect files
        all_files = []

        for path in args.paths:
            if not path.exists():
                print(f"Warning: {path} does not exist")
                continue

            if path.is_file():
                all_files.append(path)
            elif path.is_dir():
                formatter.format_directory(path, args.recursive, exclude)

        # Format individual files
        if all_files:
            formatter.format_files(all_files)

        # Print summary
        formatter.print_summary()

        # Export if requested
        if args.export_json:
            formatter.export_json(args.export_json)

        # Exit code based on results
        if args.check and formatter.stats["needs_formatting"] > 0:
            sys.exit(1)
        elif formatter.stats["files_failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nFormatting cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
