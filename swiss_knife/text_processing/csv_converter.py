import csv
import json
import xml.etree.ElementTree as ET  # nosec B405 - secured by defusedxml.defuse_stdlib()
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import defusedxml
    defusedxml.defuse_stdlib()
except ImportError:
    pass  # defusedxml not available, continue with standard library

from ..core import SafetyError, check_file_size_limit, validate_path


class CSVConverter:
    def __init__(self, max_file_size_mb: int = 100):
        """

        Args:
            max_file_size_mb: Maximum file size to process in MB
        """
        self.max_file_size_mb = max_file_size_mb

    def _infer_type(self, value: str) -> Any:
        if not value or value.lower() in ("", "null", "none"):
            return None

        # Boolean
        if value.lower() in ("true", "false", "yes", "no", "1", "0"):
            return value.lower() in ("true", "yes", "1")

        # Integer
        try:
            if "." not in value and "e" not in value.lower():
                return int(value)
        except ValueError:
            pass

        # Float
        try:
            return float(value)
        except ValueError:
            pass

        # String (default)
        return value

    def read_csv(
        self, file_path: Path, delimiter: str = ",", infer_types: bool = True
    ) -> List[Dict[str, Any]]:
        """

        Args:
            file_path: Path to CSV file
            delimiter: CSV delimiter character
            infer_types: Whether to infer data types

        Returns:
            List of dictionaries representing CSV rows
        """
        file_path = validate_path(file_path)
        check_file_size_limit(file_path, self.max_file_size_mb)

        data = []

        try:
            with open(file_path, encoding="utf-8", newline="") as f:
                # Detect delimiter if not specified
                if delimiter == "auto":
                    sample = f.read(1024)
                    f.seek(0)
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter

                reader = csv.DictReader(f, delimiter=delimiter)

                for row in reader:
                    if infer_types:
                        row = {k: self._infer_type(v) for k, v in row.items()}
                    data.append(row)

        except (OSError, csv.Error) as e:
            raise SafetyError(f"Error reading CSV file: {e}")

        return data

    def to_json(self, data: List[Dict[str, Any]], pretty: bool = True) -> str:
        """

        Args:
            data: List of dictionaries
            pretty: Whether to format JSON with indentation

        Returns:
            JSON string
        """
        try:
            if pretty:
                return json.dumps(data, indent=2, ensure_ascii=False)
            else:
                return json.dumps(data, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            raise SafetyError(f"Error converting to JSON: {e}")

    def to_xml(
        self, data: List[Dict[str, Any]], root_tag: str = "data", row_tag: str = "row"
    ) -> str:
        """

        Args:
            data: List of dictionaries
            root_tag: XML root element tag name
            row_tag: XML row element tag name

        Returns:
            XML string
        """
        try:
            root = ET.Element(root_tag)

            for row in data:
                row_elem = ET.SubElement(root, row_tag)

                for key, value in row.items():
                    # Sanitize key for XML
                    safe_key = "".join(
                        c if c.isalnum() or c in "_-" else "_" for c in str(key)
                    )
                    if safe_key and safe_key[0].isdigit():
                        safe_key = f"field_{safe_key}"

                    elem = ET.SubElement(row_elem, safe_key or "field")
                    elem.text = str(value) if value is not None else ""

            return ET.tostring(root, encoding="unicode")

        except Exception as e:
            raise SafetyError(f"Error converting to XML: {e}")

    def convert_file(
        self,
        input_path: str,
        output_format: str,
        output_path: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """

        Args:
            input_path: Path to input CSV file
            output_format: Output format ('json' or 'xml')
            output_path: Path for output file (optional)
            **kwargs: Additional arguments for conversion

        Returns:
            Path to output file or converted string
        """
        input_file = Path(input_path)
        data = self.read_csv(input_file, **kwargs)

        if output_format.lower() == "json":
            result = self.to_json(data, kwargs.get("pretty", True))
            extension = ".json"
        elif output_format.lower() == "xml":
            result = self.to_xml(
                data, kwargs.get("root_tag", "data"), kwargs.get("row_tag", "row")
            )
            extension = ".xml"
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        if output_path:
            output_file = Path(output_path)
        else:
            output_file = input_file.with_suffix(extension)

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
            return str(output_file)
        except OSError as e:
            raise SafetyError(f"Error writing output file: {e}")


def convert_csv(
    input_path: str, output_format: str, output_path: Optional[str] = None, **kwargs: Any
) -> str:
    """

    Args:
        input_path: Path to input CSV file
        output_format: Output format ('json' or 'xml')
        output_path: Path for output file (optional)
        **kwargs: Additional conversion arguments

    Returns:
        Path to output file
    """
    converter = CSVConverter()
    return converter.convert_file(input_path, output_format, output_path, **kwargs)
