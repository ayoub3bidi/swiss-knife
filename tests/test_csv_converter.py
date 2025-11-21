import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from swiss_knife.text_processing.csv_converter import CSVConverter, convert_csv


class TestCSVConverter:

    def test_init(self):
        converter = CSVConverter(max_file_size_mb=50)
        assert converter.max_file_size_mb == 50

    def test_infer_type_none(self):
        converter = CSVConverter()
        assert converter._infer_type("") is None
        assert converter._infer_type("null") is None
        assert converter._infer_type("None") is None

    def test_infer_type_boolean(self):
        converter = CSVConverter()
        assert converter._infer_type("true") is True
        assert converter._infer_type("True") is True
        assert converter._infer_type("false") is False
        assert converter._infer_type("yes") is True
        assert converter._infer_type("no") is False
        assert converter._infer_type("1") is True
        assert converter._infer_type("0") is False

    def test_infer_type_integer(self):
        converter = CSVConverter()
        assert converter._infer_type("123") == 123
        assert converter._infer_type("-456") == -456

    def test_infer_type_float(self):
        converter = CSVConverter()
        assert converter._infer_type("123.45") == 123.45
        assert converter._infer_type("-67.89") == -67.89
        assert converter._infer_type("1.23e4") == 1.23e4

    def test_infer_type_string(self):
        converter = CSVConverter()
        assert converter._infer_type("hello") == "hello"
        assert converter._infer_type("123abc") == "123abc"

    def test_read_csv_basic(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_content = "name,age,active\nJohn,25,true\nJane,30,false\n"
        csv_file.write_text(csv_content)

        converter = CSVConverter()
        data = converter.read_csv(csv_file)

        assert len(data) == 2
        assert data[0] == {"name": "John", "age": 25, "active": True}
        assert data[1] == {"name": "Jane", "age": 30, "active": False}

    def test_read_csv_no_type_inference(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_content = "name,age,active\nJohn,25,true\n"
        csv_file.write_text(csv_content)

        converter = CSVConverter()
        data = converter.read_csv(csv_file, infer_types=False)

        assert data[0] == {"name": "John", "age": "25", "active": "true"}

    def test_read_csv_custom_delimiter(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_content = "name;age;active\nJohn;25;true\n"
        csv_file.write_text(csv_content)

        converter = CSVConverter()
        data = converter.read_csv(csv_file, delimiter=";")

        assert data[0] == {"name": "John", "age": 25, "active": True}

    def test_to_json_pretty(self):
        converter = CSVConverter()
        data = [{"name": "John", "age": 25}]

        result = converter.to_json(data, pretty=True)
        parsed = json.loads(result)

        assert parsed == data
        assert "\n" in result  # Pretty formatting includes newlines

    def test_to_json_compact(self):
        converter = CSVConverter()
        data = [{"name": "John", "age": 25}]

        result = converter.to_json(data, pretty=False)
        parsed = json.loads(result)

        assert parsed == data
        assert "\n" not in result  # Compact formatting

    def test_to_xml_basic(self):
        converter = CSVConverter()
        data = [{"name": "John", "age": 25}]

        result = converter.to_xml(data)
        root = ET.fromstring(result)

        assert root.tag == "data"
        assert len(root) == 1

        row = root[0]
        assert row.tag == "row"
        assert len(row) == 2

        name_elem = row.find("name")
        age_elem = row.find("age")

        assert name_elem.text == "John"
        assert age_elem.text == "25"

    def test_to_xml_custom_tags(self):
        converter = CSVConverter()
        data = [{"name": "John"}]

        result = converter.to_xml(data, root_tag="users", row_tag="user")
        root = ET.fromstring(result)

        assert root.tag == "users"
        assert root[0].tag == "user"

    def test_convert_file_to_json(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_content = "name,age\nJohn,25\n"
        csv_file.write_text(csv_content)

        converter = CSVConverter()
        output_path = converter.convert_file(str(csv_file), "json")

        assert Path(output_path).exists()
        assert output_path.endswith(".json")

        with open(output_path) as f:
            data = json.load(f)

        assert data == [{"name": "John", "age": 25}]

    def test_convert_file_to_xml(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_content = "name,age\nJohn,25\n"
        csv_file.write_text(csv_content)

        converter = CSVConverter()
        output_path = converter.convert_file(str(csv_file), "xml")

        assert Path(output_path).exists()
        assert output_path.endswith(".xml")

        root = ET.parse(output_path).getroot()
        assert root.tag == "data"
        assert root[0].find("name").text == "John"

    def test_convert_file_invalid_format(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name\nJohn\n")

        converter = CSVConverter()

        with pytest.raises(ValueError):
            converter.convert_file(str(csv_file), "invalid")


def test_convert_csv_convenience_function(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_content = "name,age\nJohn,25\n"
    csv_file.write_text(csv_content)

    output_path = convert_csv(str(csv_file), "json")

    assert Path(output_path).exists()
    with open(output_path) as f:
        data = json.load(f)

    assert data == [{"name": "John", "age": 25}]
