#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from ..text_processing.csv_converter import CSVConverter


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert CSV files to JSON or XML formats"
    )
    parser.add_argument("input", help="Input CSV file path")
    parser.add_argument(
        "--format",
        choices=["json", "xml"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output", "-o", help="Output file path (default: input file with new extension)"
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="CSV delimiter character (default: comma)",
    )
    parser.add_argument(
        "--no-infer-types",
        action="store_true",
        help="Disable automatic type inference",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print JSON output (default: True)",
    )
    parser.add_argument(
        "--no-pretty",
        action="store_true",
        help="Disable pretty-printing for JSON",
    )
    parser.add_argument(
        "--root-tag",
        default="data",
        help="XML root element tag name (default: data)",
    )
    parser.add_argument(
        "--row-tag",
        default="row",
        help="XML row element tag name (default: row)",
    )
    parser.add_argument(
        "--max-size-mb",
        type=int,
        default=100,
        help="Maximum file size to process in MB (default: 100)",
    )

    args = parser.parse_args()

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Initialize converter
    converter = CSVConverter(max_file_size_mb=args.max_size_mb)

    try:
        # Prepare kwargs for reading CSV
        read_kwargs = {
            "delimiter": args.delimiter,
            "infer_types": not args.no_infer_types,
        }

        # Prepare kwargs for conversion
        convert_kwargs = {}
        if args.format == "json":
            convert_kwargs["pretty"] = not args.no_pretty
        elif args.format == "xml":
            convert_kwargs["root_tag"] = args.root_tag
            convert_kwargs["row_tag"] = args.row_tag

        # Read CSV
        data = converter.read_csv(Path(args.input), **read_kwargs)

        # Convert to desired format
        if args.format == "json":
            result = converter.to_json(data, **convert_kwargs)
            extension = ".json"
        elif args.format == "xml":
            result = converter.to_xml(data, **convert_kwargs)
            extension = ".xml"

        # Determine output file
        if args.output:
            output_file = Path(args.output)
        else:
            output_file = Path(args.input).with_suffix(extension)

        # Write output
        output_file.write_text(result, encoding="utf-8")
        print(f"Successfully converted {args.input} to {output_file}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
