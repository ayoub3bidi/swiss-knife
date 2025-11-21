#!/usr/bin/env python3

import argparse
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List

try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class CSVConverter:
    def __init__(
        self,
        delimiter: str = ",",
        skip_empty_rows: bool = True,
        skip_empty_fields: bool = False,
        strip_whitespace: bool = True,
        infer_types: bool = True,
        encoding: str = "utf-8",
    ):
        """
        Args:
            delimiter: CSV delimiter character
            skip_empty_rows: Skip rows with all empty fields
            skip_empty_fields: Remove empty fields from output
            strip_whitespace: Strip leading/trailing whitespace from values
            infer_types: Convert strings to numbers/booleans where appropriate
            encoding: File encoding
        """
        self.delimiter = delimiter
        self.skip_empty_rows = skip_empty_rows
        self.skip_empty_fields = skip_empty_fields
        self.strip_whitespace = strip_whitespace
        self.infer_types = infer_types
        self.encoding = encoding

        self.stats = {"rows_processed": 0, "rows_skipped": 0, "fields_found": 0}

    def _normalize_header(self, header: str) -> str:
        if self.strip_whitespace:
            header = header.strip()

        # Convert to valid identifier
        header = re.sub(r"[^\w\s-]", "", header)
        header = re.sub(r"[-\s]+", "_", header)
        header = header.lower()

        # Ensure it doesn't start with a number
        if header and header[0].isdigit():
            header = f"field_{header}"

        return header or "unnamed"

    def _convert_value(self, value: str) -> Any:
        if self.strip_whitespace:
            value = value.strip()

        if not value:
            return None if self.skip_empty_fields else ""

        if not self.infer_types:
            return value

        # Try boolean
        if value.lower() in ("true", "yes", "y", "1"):
            return True
        if value.lower() in ("false", "no", "n", "0"):
            return False

        # Try integer
        try:
            if "." not in value and "e" not in value.lower():
                return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        return value

    def _is_empty_row(self, row: Dict) -> bool:
        return all(
            not v or (isinstance(v, str) and not v.strip()) for v in row.values()
        )

    def read_csv(self, filepath: Path) -> List[Dict]:
        rows = []

        try:
            with open(filepath, encoding=self.encoding, newline="") as f:
                # Detect dialect
                sample = f.read(8192)
                f.seek(0)

                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=self.delimiter)
                except csv.Error:
                    dialect = csv.excel
                    dialect.delimiter = self.delimiter

                reader = csv.DictReader(f, dialect=dialect)

                # Normalize headers
                reader.fieldnames = [
                    self._normalize_header(h) for h in reader.fieldnames
                ]
                self.stats["fields_found"] = len(reader.fieldnames)

                # Process rows
                iterator = tqdm(reader, desc="Reading CSV") if HAS_TQDM else reader

                for row in iterator:
                    self.stats["rows_processed"] += 1

                    # Skip empty rows
                    if self.skip_empty_rows and self._is_empty_row(row):
                        self.stats["rows_skipped"] += 1
                        continue

                    # Convert values
                    converted_row = OrderedDict()
                    for key, value in row.items():
                        converted_value = self._convert_value(value)

                        # Skip empty fields if requested
                        if self.skip_empty_fields and converted_value is None:
                            continue

                        converted_row[key] = converted_value

                    rows.append(converted_row)

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filepath}")
        except PermissionError:
            raise PermissionError(f"Permission denied: {filepath}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Encoding error: {e}. Try different --encoding")

        return rows

    def to_json(
        self,
        data: List[Dict],
        pretty: bool = True,
        indent: int = 2,
        sort_keys: bool = False,
    ) -> str:
        return json.dumps(
            data,
            indent=indent if pretty else None,
            sort_keys=sort_keys,
            ensure_ascii=False,
        )

    def to_xml(
        self,
        data: List[Dict],
        root_tag: str = "root",
        row_tag: str = "row",
        pretty: bool = True,
    ) -> str:
        root = ET.Element(root_tag)

        for row in data:
            row_element = ET.SubElement(root, row_tag)

            for key, value in row.items():
                field_element = ET.SubElement(row_element, key)

                if value is None:
                    field_element.set("null", "true")
                elif isinstance(value, bool):
                    field_element.text = str(value).lower()
                    field_element.set("type", "boolean")
                elif isinstance(value, int):
                    field_element.text = str(value)
                    field_element.set("type", "integer")
                elif isinstance(value, float):
                    field_element.text = str(value)
                    field_element.set("type", "float")
                else:
                    field_element.text = str(value)

        xml_string = ET.tostring(root, encoding="unicode", method="xml")

        if pretty:
            xml_string = self._prettify_xml(xml_string)

        return xml_string

    def _prettify_xml(self, xml_string: str) -> str:
        import xml.dom.minidom

        dom = xml.dom.minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ")

    def convert_file(
        self, input_path: Path, output_path: Path, format: str, **kwargs
    ) -> None:
        print(f"Reading: {input_path}")
        data = self.read_csv(input_path)

        print(f"Converting to {format.upper()}...")

        if format == "json":
            output = self.to_json(data, **kwargs)
        elif format == "xml":
            output = self.to_xml(data, **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format}")

        print(f"Writing: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)

        self.print_stats(input_path, output_path)

    def print_stats(self, input_path: Path, output_path: Path):
        input_size = input_path.stat().st_size
        output_size = output_path.stat().st_size

        print("\n" + "=" * 60)
        print("Conversion Statistics")
        print("=" * 60)
        print(f"Rows processed: {self.stats['rows_processed']}")
        print(
            f"Rows converted: {self.stats['rows_processed'] - self.stats['rows_skipped']}"
        )
        print(f"Rows skipped: {self.stats['rows_skipped']}")
        print(f"Fields: {self.stats['fields_found']}")
        print(f"Input size: {self._format_bytes(input_size)}")
        print(f"Output size: {self._format_bytes(output_size)}")
        print(f"Size ratio: {(output_size / input_size * 100):.1f}%")

    def _format_bytes(self, bytes_val: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="Convert CSV files to JSON or XML format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert to JSON with default settings
  python csv_converter.py data.csv -f json -o output.json

  # Convert to XML with custom tags
  python csv_converter.py data.csv -f xml --root-tag data --row-tag record

  # Custom delimiter (TSV)
  python csv_converter.py data.tsv -f json -d $'\\t'

  # Compact JSON output
  python csv_converter.py data.csv -f json --no-pretty

  # Keep original types as strings
  python csv_converter.py data.csv -f json --no-infer-types

  # Handle different encoding
  python csv_converter.py data.csv -f json --encoding latin-1

  # Sort JSON keys alphabetically
  python csv_converter.py data.csv -f json --sort-keys
        """,
    )

    parser.add_argument("input", type=Path, help="Input CSV file")
    parser.add_argument(
        "-f", "--format", required=True, choices=["json", "xml"], help="Output format"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (default: input name with new extension)",
    )

    # CSV parsing options
    parser.add_argument(
        "-d", "--delimiter", default=",", help="CSV delimiter (default: comma)"
    )
    parser.add_argument(
        "--encoding", default="utf-8", help="File encoding (default: utf-8)"
    )
    parser.add_argument(
        "--skip-empty-rows",
        action="store_true",
        default=True,
        help="Skip rows with all empty fields (default: True)",
    )
    parser.add_argument(
        "--keep-empty-rows",
        dest="skip_empty_rows",
        action="store_false",
        help="Keep rows with all empty fields",
    )
    parser.add_argument(
        "--skip-empty-fields",
        action="store_true",
        help="Remove empty fields from output",
    )
    parser.add_argument(
        "--no-strip",
        dest="strip_whitespace",
        action="store_false",
        help="Don't strip whitespace from values",
    )
    parser.add_argument(
        "--no-infer-types",
        dest="infer_types",
        action="store_false",
        help="Keep all values as strings",
    )

    # JSON options
    parser.add_argument(
        "--no-pretty",
        dest="pretty",
        action="store_false",
        help="Output compact JSON/XML",
    )
    parser.add_argument(
        "--indent", type=int, default=2, help="JSON indentation spaces (default: 2)"
    )
    parser.add_argument(
        "--sort-keys", action="store_true", help="Sort JSON keys alphabetically"
    )

    # XML options
    parser.add_argument(
        "--root-tag", default="root", help="XML root element tag (default: root)"
    )
    parser.add_argument(
        "--row-tag", default="row", help="XML row element tag (default: row)"
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Determine output path
    if args.output is None:
        args.output = args.input.with_suffix(f".{args.format}")

    # Check output doesn't exist or confirm overwrite
    if args.output.exists():
        response = input(f"Output file exists: {args.output}\nOverwrite? (y/N): ")
        if response.lower() != "y":
            print("Operation cancelled.")
            sys.exit(0)

    try:
        # Initialize converter
        converter = CSVConverter(
            delimiter=args.delimiter,
            skip_empty_rows=args.skip_empty_rows,
            skip_empty_fields=args.skip_empty_fields,
            strip_whitespace=args.strip_whitespace,
            infer_types=args.infer_types,
            encoding=args.encoding,
        )

        # Build format-specific kwargs
        format_kwargs = {"pretty": args.pretty}

        if args.format == "json":
            format_kwargs.update({"indent": args.indent, "sort_keys": args.sort_keys})
        elif args.format == "xml":
            format_kwargs.update({"root_tag": args.root_tag, "row_tag": args.row_tag})

        # Convert
        converter.convert_file(args.input, args.output, args.format, **format_kwargs)

        print(f"\n✓ Successfully converted to {args.output}")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
