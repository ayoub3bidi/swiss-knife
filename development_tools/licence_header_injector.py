#!/usr/bin/env python3

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


@dataclass
class LicenseTemplate:
    name: str
    header: str
    spdx_id: str


class LicenseHeaderInjector:
    # License templates with placeholders
    LICENSES = {
        "mit": LicenseTemplate(
            name="MIT License",
            spdx_id="MIT",
            header="""Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""",
        ),
        "apache": LicenseTemplate(
            name="Apache License 2.0",
            spdx_id="Apache-2.0",
            header="""Copyright {year} {author}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.""",
        ),
        "gpl3": LicenseTemplate(
            name="GNU GPL v3.0",
            spdx_id="GPL-3.0",
            header="""Copyright (C) {year} {author}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.""",
        ),
        "bsd3": LicenseTemplate(
            name="BSD 3-Clause License",
            spdx_id="BSD-3-Clause",
            header="""Copyright (c) {year}, {author}
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.""",
        ),
        "isc": LicenseTemplate(
            name="ISC License",
            spdx_id="ISC",
            header="""Copyright (c) {year} {author}

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.""",
        ),
        "unlicense": LicenseTemplate(
            name="The Unlicense",
            spdx_id="Unlicense",
            header="""This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>""",
        ),
    }

    # Comment styles by file extension
    COMMENT_STYLES = {
        # C-style block comments
        "c_block": {
            "extensions": [
                ".c",
                ".cpp",
                ".cc",
                ".cxx",
                ".h",
                ".hpp",
                ".java",
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
                ".cs",
                ".go",
                ".rs",
                ".swift",
                ".m",
                ".mm",
                ".scala",
                ".kt",
            ],
            "start": "/*",
            "middle": " * ",
            "end": " */",
            "pattern": r"/\*.*?\*/",
        },
        # C-style line comments
        "c_line": {
            "extensions": [
                ".c",
                ".cpp",
                ".cc",
                ".cxx",
                ".h",
                ".hpp",
                ".java",
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
                ".cs",
                ".go",
                ".rs",
                ".swift",
                ".php",
            ],
            "start": "//",
            "middle": "// ",
            "end": None,
            "pattern": r"^//.*$",
        },
        # Hash comments (Python, Ruby, Shell, etc.)
        "hash": {
            "extensions": [
                ".py",
                ".rb",
                ".sh",
                ".bash",
                ".pl",
                ".pm",
                ".r",
                ".yml",
                ".yaml",
                ".toml",
                ".conf",
                ".cfg",
                ".ini",
                ".env",
            ],
            "start": "#",
            "middle": "# ",
            "end": None,
            "pattern": r"^#.*$",
        },
        # XML/HTML comments
        "xml": {
            "extensions": [".html", ".htm", ".xml", ".svg", ".vue"],
            "start": "<!--",
            "middle": "  ",
            "end": "-->",
            "pattern": r"<!--.*?-->",
        },
        # SQL comments
        "sql": {
            "extensions": [".sql"],
            "start": "--",
            "middle": "-- ",
            "end": None,
            "pattern": r"^--.*$",
        },
        # Lua comments
        "lua": {
            "extensions": [".lua"],
            "start": "--[[",
            "middle": "  ",
            "end": "--]]",
            "pattern": r"--\[\[.*?\]\]",
        },
    }

    def __init__(
        self,
        license_type: str,
        author: str,
        year: Optional[str] = None,
        custom_template: Optional[str] = None,
        update_existing: bool = False,
        remove_headers: bool = False,
        dry_run: bool = False,
    ):
        """
        Args:
            license_type: License type (mit, apache, gpl3, bsd3, isc, unlicense, custom)
            author: Copyright holder name
            year: Copyright year (default: current year)
            custom_template: Path to custom license template file
            update_existing: Update existing license headers
            remove_headers: Remove existing license headers
            dry_run: Show what would be done without making changes
        """
        self.license_type = license_type.lower()
        self.author = author
        self.year = year or str(datetime.now().year)
        self.update_existing = update_existing
        self.remove_headers = remove_headers
        self.dry_run = dry_run

        # Load license template
        if custom_template:
            self.license_template = self._load_custom_template(custom_template)
        elif self.license_type in self.LICENSES:
            self.license_template = self.LICENSES[self.license_type]
        else:
            raise ValueError(f"Unknown license type: {license_type}")

        # Statistics
        self.stats = {
            "files_processed": 0,
            "headers_added": 0,
            "headers_updated": 0,
            "headers_removed": 0,
            "files_skipped": 0,
            "errors": 0,
        }

        self.errors: List[Tuple[str, str]] = []

    def _load_custom_template(self, template_path: str) -> LicenseTemplate:
        try:
            with open(template_path, encoding="utf-8") as f:
                content = f.read()
            return LicenseTemplate(
                name="Custom License", spdx_id="Custom", header=content
            )
        except Exception as e:
            raise ValueError(f"Failed to load custom template: {e}")

    def _get_comment_style(self, filepath: Path) -> Optional[Dict]:
        ext = filepath.suffix.lower()

        for _style_name, style_info in self.COMMENT_STYLES.items():
            if ext in style_info["extensions"]:
                return style_info

        return None

    def _format_header(self, comment_style: Dict) -> str:
        # Replace placeholders
        header_text = self.license_template.header
        header_text = header_text.replace("{year}", self.year)
        header_text = header_text.replace("{author}", self.author)

        lines = header_text.split("\n")
        formatted_lines = []

        # Add start comment
        if comment_style["start"]:
            formatted_lines.append(comment_style["start"])

        # Add content with middle comment prefix
        for line in lines:
            if line.strip():
                formatted_lines.append(comment_style["middle"] + line)
            else:
                formatted_lines.append(comment_style["middle"].rstrip())

        # Add end comment
        if comment_style["end"]:
            formatted_lines.append(comment_style["end"])

        return "\n".join(formatted_lines) + "\n\n"

    def _detect_existing_header(
        self, content: str, comment_style: Dict
    ) -> Optional[Tuple[int, int]]:
        lines = content.split("\n")

        # Skip shebang and encoding declarations
        start_line = 0
        if lines and lines[0].startswith("#!"):
            start_line = 1
        if len(lines) > start_line and "coding" in lines[start_line]:
            start_line += 1

        # Look for copyright/license keywords in first 50 lines
        keywords = [
            "copyright",
            "license",
            "licensed",
            "permission",
            "warranty",
            "spdx-license-identifier",
            "all rights reserved",
        ]

        header_start = None
        header_end = None
        in_header = False

        for i in range(start_line, min(len(lines), 50)):
            line_lower = lines[i].lower()

            # Check if line has any license keyword
            if any(keyword in line_lower for keyword in keywords):
                if header_start is None:
                    header_start = i
                    in_header = True
                header_end = i
            elif in_header:
                # Check if still in comment block
                stripped = lines[i].strip()
                if not stripped or not any(
                    stripped.startswith(c) for c in ["#", "//", "/*", "*", "--", "<!--"]
                ):
                    # End of comment block
                    break
                header_end = i

        if header_start is not None:
            return (header_start, header_end + 1)

        return None

    def _inject_header(self, filepath: Path) -> bool:
        try:
            # Get comment style
            comment_style = self._get_comment_style(filepath)
            if not comment_style:
                self.stats["files_skipped"] += 1
                return False

            # Read file
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Check for existing header
            existing_header = self._detect_existing_header(content, comment_style)

            if self.remove_headers:
                if existing_header:
                    lines = content.split("\n")
                    start, end = existing_header
                    new_content = "\n".join(lines[:start] + lines[end:])

                    if not self.dry_run:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(new_content)

                    self.stats["headers_removed"] += 1
                    return True
                else:
                    self.stats["files_skipped"] += 1
                    return False

            # Format new header
            new_header = self._format_header(comment_style)

            if existing_header:
                if not self.update_existing:
                    self.stats["files_skipped"] += 1
                    return False

                # Replace existing header
                lines = content.split("\n")
                start, end = existing_header

                # Preserve shebang and encoding
                preserved_lines = []
                if start > 0:
                    preserved_lines = lines[:start]

                new_content = (
                    "\n".join(preserved_lines)
                    + ("\n" if preserved_lines else "")
                    + new_header
                    + "\n".join(lines[end:])
                )

                if not self.dry_run:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)

                self.stats["headers_updated"] += 1
            else:
                # Add new header
                # Preserve shebang and encoding
                lines = content.split("\n")
                insert_pos = 0

                if lines and lines[0].startswith("#!"):
                    insert_pos = 1
                if len(lines) > insert_pos and "coding" in lines[insert_pos]:
                    insert_pos += 1

                if insert_pos > 0:
                    preserved = "\n".join(lines[:insert_pos])
                    rest = "\n".join(lines[insert_pos:])
                    new_content = preserved + "\n\n" + new_header + rest
                else:
                    new_content = new_header + content

                if not self.dry_run:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)

                self.stats["headers_added"] += 1

            self.stats["files_processed"] += 1
            return True

        except Exception as e:
            self.errors.append((str(filepath), str(e)))
            self.stats["errors"] += 1
            return False

    def process_files(
        self,
        paths: List[Path],
        extensions: Optional[List[str]] = None,
        recursive: bool = False,
        exclude_patterns: Optional[List[str]] = None,
    ) -> None:
        # Collect files
        files = []
        exclude_patterns = exclude_patterns or []
        exclude_patterns.extend(
            [
                "node_modules",
                ".git",
                "__pycache__",
                "venv",
                ".venv",
                "dist",
                "build",
                "target",
                ".eggs",
                "*.min.js",
                "*.min.css",
            ]
        )

        for path in paths:
            if path.is_file():
                files.append(path)
            elif path.is_dir():
                pattern = "**/*" if recursive else "*"
                for file_path in path.glob(pattern):
                    if file_path.is_file():
                        # Check exclusions
                        if any(excl in str(file_path) for excl in exclude_patterns):
                            continue

                        # Check extensions
                        if extensions:
                            if file_path.suffix.lower().lstrip(".") not in extensions:
                                continue

                        files.append(file_path)

        if not files:
            print("No files found to process")
            return

        action = "Removing headers from" if self.remove_headers else "Processing"
        print(f"{action} {len(files)} file(s)...")

        if self.dry_run:
            print("DRY RUN MODE - No files will be modified\n")

        # Process files
        iterator = tqdm(files, desc="Processing", unit="files") if HAS_TQDM else files

        for filepath in iterator:
            result = self._inject_header(filepath)

            if result and self.dry_run:
                if self.remove_headers:
                    print(f"Would remove header: {filepath}")
                elif self.stats["headers_updated"] > self.stats["headers_added"]:
                    print(f"Would update header: {filepath}")
                else:
                    print(f"Would add header: {filepath}")

    def print_summary(self):
        print("\n" + "=" * 70)
        print("LICENSE HEADER OPERATION SUMMARY")
        print("=" * 70)
        print(f"Files processed:     {self.stats['files_processed']}")

        if self.remove_headers:
            print(f"Headers removed:     {self.stats['headers_removed']}")
        else:
            print(f"Headers added:       {self.stats['headers_added']}")
            print(f"Headers updated:     {self.stats['headers_updated']}")

        print(f"Files skipped:       {self.stats['files_skipped']}")
        print(f"Errors:              {self.stats['errors']}")

        if self.errors:
            print("\nErrors encountered:")
            for filepath, error in self.errors[:10]:
                print(f"  {filepath}: {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")


def main():
    parser = argparse.ArgumentParser(
        description="Inject, update, or remove license headers in source code files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add MIT license headers to Python files
  python license_header_injector.py -l mit -a "John Doe" src/ --ext py

  # Add Apache license to all source files recursively
  python license_header_injector.py -l apache -a "Acme Corp" . -r

  # Update existing headers with new year
  python license_header_injector.py -l mit -a "John Doe" -y 2025 src/ --update -r

  # Remove all license headers
  python license_header_injector.py src/ --remove -r

  # Dry run to preview changes
  python license_header_injector.py -l mit -a "John Doe" src/ --dry-run -r

  # Use custom license template
  python license_header_injector.py -l custom --template my_license.txt -a "John Doe" src/

  # Exclude specific directories
  python license_header_injector.py -l mit -a "John Doe" . -r --exclude tests,docs

Available licenses: mit, apache, gpl3, bsd3, isc, unlicense, custom
        """,
    )

    parser.add_argument(
        "paths", nargs="+", type=Path, help="Files or directories to process"
    )

    parser.add_argument(
        "-l",
        "--license",
        dest="license_type",
        choices=["mit", "apache", "gpl3", "bsd3", "isc", "unlicense", "custom"],
        help="License type",
    )
    parser.add_argument("-a", "--author", type=str, help="Copyright holder/author name")
    parser.add_argument(
        "-y", "--year", type=str, help="Copyright year (default: current year)"
    )
    parser.add_argument(
        "--template", type=str, help="Path to custom license template file"
    )

    parser.add_argument(
        "--update", action="store_true", help="Update existing license headers"
    )
    parser.add_argument(
        "--remove", action="store_true", help="Remove existing license headers"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    parser.add_argument(
        "--ext",
        "--extensions",
        dest="extensions",
        help="File extensions to process (comma-separated)",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Process directories recursively"
    )
    parser.add_argument(
        "--exclude", type=str, help="Exclude patterns (comma-separated)"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.remove:
        if not args.license_type:
            parser.error("--license is required (unless using --remove)")
        if not args.author:
            parser.error("--author is required (unless using --remove)")

    if args.license_type == "custom" and not args.template:
        parser.error("--template is required when using custom license")

    # Parse extensions
    extensions = None
    if args.extensions:
        extensions = [ext.strip().lstrip(".") for ext in args.extensions.split(",")]

    # Parse exclude patterns
    exclude_patterns = None
    if args.exclude:
        exclude_patterns = [p.strip() for p in args.exclude.split(",")]

    # Validate paths
    for path in args.paths:
        if not path.exists():
            print(f"Error: Path not found: {path}")
            sys.exit(1)

    try:
        injector = LicenseHeaderInjector(
            license_type=args.license_type or "mit",
            author=args.author or "",
            year=args.year,
            custom_template=args.template,
            update_existing=args.update,
            remove_headers=args.remove,
            dry_run=args.dry_run,
        )

        injector.process_files(
            args.paths,
            extensions=extensions,
            recursive=args.recursive,
            exclude_patterns=exclude_patterns,
        )

        injector.print_summary()

        sys.exit(0 if injector.stats["errors"] == 0 else 1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
