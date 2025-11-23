import json
import sys
from unittest.mock import patch

import pytest

from swiss_knife.cli.csv_cli import main


class TestCSVCLI:

    def test_csv_to_json_basic(self, tmp_path):
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n")

        # Run CLI
        with patch.object(
            sys,
            "argv",
            [
                "sk-csv",
                str(csv_file),
                "--format",
                "json",
                "--output",
                str(tmp_path / "out.json"),
            ],
        ):
            main()

        # Verify output
        output_file = tmp_path / "out.json"
        assert output_file.exists()

        data = json.loads(output_file.read_text())
        assert len(data) == 2
        assert data[0]["name"] == "Alice"
        assert data[0]["age"] == 30

    def test_csv_to_xml_basic(self, tmp_path):
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,value\ntest,123\n")

        # Run CLI
        with patch.object(
            sys,
            "argv",
            [
                "sk-csv",
                str(csv_file),
                "--format",
                "xml",
                "--output",
                str(tmp_path / "out.xml"),
            ],
        ):
            main()

        # Verify output
        output_file = tmp_path / "out.xml"
        assert output_file.exists()
        assert "<data>" in output_file.read_text()
        assert "<name>test</name>" in output_file.read_text()

    def test_csv_missing_file(self, capsys):
        with patch.object(sys, "argv", ["sk-csv", "nonexistent.csv"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "does not exist" in captured.err

    def test_csv_with_custom_delimiter(self, tmp_path):
        # Create test CSV with semicolon delimiter
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name;age\nAlice;30\n")

        with patch.object(
            sys,
            "argv",
            [
                "sk-csv",
                str(csv_file),
                "--format",
                "json",
                "--delimiter",
                ";",
                "--output",
                str(tmp_path / "out.json"),
            ],
        ):
            main()

        output_file = tmp_path / "out.json"
        data = json.loads(output_file.read_text())
        assert data[0]["name"] == "Alice"
        assert data[0]["age"] == 30

    def test_csv_disable_type_inference(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age\nAlice,30\n")

        with patch.object(
            sys,
            "argv",
            [
                "sk-csv",
                str(csv_file),
                "--no-infer-types",
                "--output",
                str(tmp_path / "out.json"),
            ],
        ):
            main()

        output_file = tmp_path / "out.json"
        data = json.loads(output_file.read_text())
        # With type inference disabled, age should be string
        assert data[0]["age"] == "30"

    def test_csv_custom_xml_tags(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,value\ntest,1\n")

        with patch.object(
            sys,
            "argv",
            [
                "sk-csv",
                str(csv_file),
                "--format",
                "xml",
                "--root-tag",
                "records",
                "--row-tag",
                "item",
                "--output",
                str(tmp_path / "out.xml"),
            ],
        ):
            main()

        output = (tmp_path / "out.xml").read_text()
        assert "<records>" in output
        assert "<item>" in output

    def test_csv_help(self):
        with patch.object(sys, "argv", ["sk-csv", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
