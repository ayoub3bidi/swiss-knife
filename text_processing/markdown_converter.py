#!/usr/bin/env python3

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import markdown

    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False
    print("Error: markdown not installed. Run: pip install markdown")
    sys.exit(1)

try:
    from pygments.formatters import HtmlFormatter

    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False


class MarkdownConverter:
    # CSS themes for code highlighting
    THEMES = {
        "default": "default",
        "monokai": "monokai",
        "github": "github",
        "dracula": "dracula",
        "solarized-dark": "solarized-dark",
        "solarized-light": "solarized-light",
    }

    # HTML templates
    TEMPLATE_MINIMAL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {styles}
</head>
<body>
    {content}
</body>
</html>"""

    TEMPLATE_STYLED = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
        }}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            padding-left: 15px;
            color: #666;
            margin: 15px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background: #f4f4f4;
            font-weight: bold;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .toc {{
            background: #f9f9f9;
            border: 1px solid #ddd;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .toc ul {{
            list-style: none;
            padding-left: 0;
        }}
        .toc ul ul {{
            padding-left: 20px;
        }}
        .metadata {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 0.9em;
            color: #666;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 0.9em;
            color: #666;
        }}
    </style>
    {pygments_css}
</head>
<body>
    {metadata}
    {toc}
    {content}
    {footer}
</body>
</html>"""

    def __init__(
        self,
        template: str = "styled",
        theme: str = "github",
        enable_toc: bool = True,
        enable_tables: bool = True,
        enable_code_highlight: bool = True,
        enable_metadata: bool = True,
        line_numbers: bool = False,
        title: Optional[str] = None,
        add_footer: bool = False,
    ):
        """
        Args:
            template: HTML template style ('minimal', 'styled')
            theme: Code highlighting theme
            enable_toc: Generate table of contents
            enable_tables: Enable table support
            enable_code_highlight: Enable syntax highlighting
            enable_metadata: Parse YAML frontmatter
            line_numbers: Show line numbers in code blocks
            title: Custom page title
            add_footer: Add generation timestamp footer
        """
        self.template = template
        self.theme = theme if theme in self.THEMES else "github"
        self.enable_toc = enable_toc
        self.enable_tables = enable_tables
        self.enable_code_highlight = enable_code_highlight
        self.enable_metadata = enable_metadata
        self.line_numbers = line_numbers
        self.custom_title = title
        self.add_footer = add_footer

        # Setup markdown extensions
        self.extensions = ["fenced_code", "nl2br", "attr_list"]

        if self.enable_tables:
            self.extensions.append("tables")

        if self.enable_toc:
            self.extensions.append("toc")

        if self.enable_code_highlight and HAS_PYGMENTS:
            self.extensions.append("codehilite")

        if self.enable_metadata:
            self.extensions.append("meta")

        # Extension configs
        self.extension_configs = {
            "codehilite": {"linenums": self.line_numbers, "css_class": "highlight"},
            "toc": {"title": "Table of Contents"},
        }

        self.stats = {"files_converted": 0, "lines_processed": 0}

    def _get_pygments_css(self) -> str:
        if not HAS_PYGMENTS or not self.enable_code_highlight:
            return ""

        try:
            formatter = HtmlFormatter(style=self.theme)
            return f"<style>\n{formatter.get_style_defs('.highlight')}\n</style>"
        except Exception:
            return ""

    def _extract_title(self, markdown_content: str, filepath: Path) -> str:
        if self.custom_title:
            return self.custom_title

        # Try to find h1 heading
        match = re.search(r"^#\s+(.+)$", markdown_content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Fallback to filename
        return filepath.stem.replace("_", " ").replace("-", " ").title()

    def _format_metadata(self, md: markdown.Markdown) -> str:
        if not self.enable_metadata or not hasattr(md, "Meta") or not md.Meta:
            return ""

        html = ['<div class="metadata">']
        for key, value in md.Meta.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            html.append(f"<p><strong>{key.title()}:</strong> {value}</p>")
        html.append("</div>")
        return "\n".join(html)

    def _format_toc(self, md: markdown.Markdown) -> str:
        if not self.enable_toc or not hasattr(md, "toc") or not md.toc:
            return ""

        return f'<div class="toc">\n{md.toc}\n</div>'

    def _format_footer(self) -> str:
        if not self.add_footer:
            return ""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f'<div class="footer">Generated on {timestamp}</div>'

    def convert(self, markdown_content: str, filepath: Path) -> str:
        # Initialize markdown processor
        md = markdown.Markdown(
            extensions=self.extensions, extension_configs=self.extension_configs
        )

        # Convert to HTML
        html_content = md.convert(markdown_content)

        # Extract components
        title = self._extract_title(markdown_content, filepath)
        metadata = self._format_metadata(md)
        toc = self._format_toc(md)
        footer = self._format_footer()

        # Get CSS
        if self.template == "minimal":
            styles = self._get_pygments_css() if self.enable_code_highlight else ""
            html = self.TEMPLATE_MINIMAL.format(
                title=title, styles=styles, content=html_content
            )
        else:  # styled
            pygments_css = (
                self._get_pygments_css() if self.enable_code_highlight else ""
            )
            html = self.TEMPLATE_STYLED.format(
                title=title,
                pygments_css=pygments_css,
                metadata=metadata,
                toc=toc,
                content=html_content,
                footer=footer,
            )

        # Update stats
        self.stats["lines_processed"] += markdown_content.count("\n")

        return html

    def convert_file(self, input_path: Path, output_path: Path) -> None:
        print(f"Converting: {input_path}")

        # Read markdown
        try:
            with open(input_path, encoding="utf-8") as f:
                markdown_content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(input_path, encoding="latin-1") as f:
                markdown_content = f.read()

        # Convert
        html = self.convert(markdown_content, input_path)

        # Write HTML
        print(f"Writing: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        self.stats["files_converted"] += 1

    def convert_directory(
        self, input_dir: Path, output_dir: Path, recursive: bool = False
    ) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)

        pattern = "**/*.md" if recursive else "*.md"
        md_files = list(input_dir.glob(pattern))

        if not md_files:
            print(f"No markdown files found in {input_dir}")
            return

        print(f"Found {len(md_files)} markdown file(s)")

        for md_file in md_files:
            # Determine output path
            rel_path = md_file.relative_to(input_dir)
            html_file = output_dir / rel_path.with_suffix(".html")
            html_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                self.convert_file(md_file, html_file)
            except Exception as e:
                print(f"Error converting {md_file}: {e}")

    def print_stats(self):
        print(f"\n{'=' * 60}")
        print("Conversion Statistics")
        print(f"{'=' * 60}")
        print(f"Files converted: {self.stats['files_converted']}")
        print(f"Lines processed: {self.stats['lines_processed']}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to HTML with syntax highlighting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion
  python markdown_converter.py README.md

  # Custom output path
  python markdown_converter.py input.md -o output.html

  # Minimal template (no styling)
  python markdown_converter.py doc.md --template minimal

  # Different syntax theme
  python markdown_converter.py code.md --theme monokai

  # Disable table of contents
  python markdown_converter.py doc.md --no-toc

  # Add line numbers to code blocks
  python markdown_converter.py tutorial.md --line-numbers

  # Convert entire directory
  python markdown_converter.py docs/ -o html/ --recursive

Available themes: default, monokai, github, dracula, solarized-dark, solarized-light
        """,
    )

    parser.add_argument("input", type=Path, help="Input markdown file or directory")
    parser.add_argument(
        "-o", "--output", type=Path, help="Output HTML file or directory"
    )

    parser.add_argument(
        "--template",
        choices=["minimal", "styled"],
        default="styled",
        help="HTML template style (default: styled)",
    )
    parser.add_argument(
        "--theme",
        choices=list(MarkdownConverter.THEMES.keys()),
        default="github",
        help="Syntax highlighting theme (default: github)",
    )

    parser.add_argument(
        "--no-toc",
        dest="enable_toc",
        action="store_false",
        help="Disable table of contents",
    )
    parser.add_argument(
        "--no-tables",
        dest="enable_tables",
        action="store_false",
        help="Disable table support",
    )
    parser.add_argument(
        "--no-highlight",
        dest="enable_highlight",
        action="store_false",
        help="Disable syntax highlighting",
    )
    parser.add_argument(
        "--no-metadata",
        dest="enable_metadata",
        action="store_false",
        help="Disable YAML frontmatter parsing",
    )

    parser.add_argument(
        "--line-numbers", action="store_true", help="Show line numbers in code blocks"
    )
    parser.add_argument("--title", type=str, help="Custom page title")
    parser.add_argument(
        "--footer", action="store_true", help="Add generation timestamp footer"
    )

    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Process directories recursively"
    )

    args = parser.parse_args()

    if not HAS_MARKDOWN:
        print("Error: markdown library required. Install: pip install markdown")
        sys.exit(1)

    # Validate input
    if not args.input.exists():
        print(f"Error: Input not found: {args.input}")
        sys.exit(1)

    # Determine output
    if args.output is None:
        if args.input.is_file():
            args.output = args.input.with_suffix(".html")
        else:
            args.output = Path("html_output")

    # Check output overwrite
    if args.input.is_file() and args.output.exists():
        response = input(f"Output exists: {args.output}\nOverwrite? (y/N): ")
        if response.lower() != "y":
            print("Cancelled.")
            sys.exit(0)

    try:
        converter = MarkdownConverter(
            template=args.template,
            theme=args.theme,
            enable_toc=args.enable_toc,
            enable_tables=args.enable_tables,
            enable_code_highlight=args.enable_highlight,
            enable_metadata=args.enable_metadata,
            line_numbers=args.line_numbers,
            title=args.title,
            add_footer=args.footer,
        )

        if args.input.is_file():
            converter.convert_file(args.input, args.output)
        else:
            converter.convert_directory(args.input, args.output, args.recursive)

        converter.print_stats()
        print(f"\n✓ Successfully converted to {args.output}")

    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
