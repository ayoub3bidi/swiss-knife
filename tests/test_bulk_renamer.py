import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from swiss_knife.core import SafetyError
from swiss_knife.file_management.bulk_renamer import BulkRenamer, bulk_rename


class TestBulkRenamer:

    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.renamer = BulkRenamer(dry_run=False)

    def teardown_method(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_files(self, names):
        files = []
        for name in names:
            file_path = self.temp_dir / name
            file_path.touch()
            files.append(file_path)
        return files

    def test_init_default(self):
        renamer = BulkRenamer()
        assert renamer.dry_run is False
        assert renamer.operations == []

    def test_init_dry_run(self):
        renamer = BulkRenamer(dry_run=True)
        assert renamer.dry_run is True
        assert renamer.operations == []

    def test_add_pattern_simple_rename(self):
        self.create_test_files(["IMG_001.jpg", "IMG_002.jpg", "doc.txt"])

        operations = self.renamer.add_pattern(
            r"IMG_(\d+)", r"photo_\1", self.temp_dir, False
        )

        assert len(operations) == 2
        operations.sort(key=lambda x: x[0].name)
        assert operations[0][0].name == "IMG_001.jpg"
        assert operations[0][1].name == "photo_001.jpg"
        assert operations[1][0].name == "IMG_002.jpg"
        assert operations[1][1].name == "photo_002.jpg"

    def test_add_pattern_no_matches(self):
        self.create_test_files(["doc.txt", "readme.md"])

        operations = self.renamer.add_pattern(
            r"IMG_(\d+)", r"photo_\1", self.temp_dir, False
        )

        assert len(operations) == 0

    def test_add_pattern_invalid_regex(self):
        with pytest.raises(SafetyError, match="Invalid regex pattern"):
            self.renamer.add_pattern("[", "replacement", self.temp_dir, False)

    def test_add_pattern_recursive(self):
        subdir = self.temp_dir / "subdir"
        subdir.mkdir()

        self.create_test_files(["IMG_001.jpg"])
        (subdir / "IMG_002.jpg").touch()

        operations = self.renamer.add_pattern(
            r"IMG_(\d+)", r"photo_\1", self.temp_dir, True
        )

        assert len(operations) == 2

    def test_add_pattern_name_collision(self):
        self.create_test_files(["IMG_001.jpg", "IMG_002.jpg"])

        with pytest.raises(SafetyError, match="Name collisions detected"):
            self.renamer.add_pattern(r"IMG_(\d+)", r"photo", self.temp_dir, False)

    def test_add_pattern_existing_target(self):
        self.create_test_files(["IMG_001.jpg", "photo_001.jpg"])

        with pytest.raises(SafetyError, match="Target files already exist"):
            self.renamer.add_pattern(r"IMG_(\d+)", r"photo_\1", self.temp_dir, False)

    def test_add_pattern_replacement_error(self):
        self.create_test_files(["IMG_001.jpg"])

        with pytest.raises(SafetyError, match="Replacement error"):
            self.renamer.add_pattern(r"IMG_(\d+)", r"photo_\2", self.temp_dir, False)

    def test_execute_no_operations(self):
        result = self.renamer.execute()
        assert result == 0

    def test_execute_dry_run(self):
        self.create_test_files(["IMG_001.jpg"])
        renamer = BulkRenamer(dry_run=True)
        renamer.add_pattern(r"IMG_(\d+)", r"photo_\1", self.temp_dir, False)

        with patch("builtins.print") as mock_print:
            result = renamer.execute()

        assert result == 0
        mock_print.assert_called()

    def test_execute_force(self):
        self.create_test_files(["IMG_001.jpg"])
        self.renamer.add_pattern(r"IMG_(\d+)", r"photo_\1", self.temp_dir, False)

        result = self.renamer.execute(force=True)

        assert result == 1
        assert (self.temp_dir / "photo_001.jpg").exists()


class TestBulkRenameFunction:

    def setup_method(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_files(self, names):
        for name in names:
            (self.temp_dir / name).touch()

    def test_bulk_rename_dry_run(self):
        self.create_test_files(["IMG_001.jpg", "IMG_002.jpg"])

        with patch("builtins.print") as mock_print:
            result = bulk_rename(
                r"IMG_(\d+)", r"photo_\1", str(self.temp_dir), dry_run=True
            )

        assert result == 0
        mock_print.assert_called()
