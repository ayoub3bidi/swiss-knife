import sys
from unittest.mock import patch

import pytest

from swiss_knife.cli.rename_cli import main


class TestRenameCLI:

    def test_rename_dry_run(self, tmp_path, capsys):
        # Create test files
        (tmp_path / "IMG_001.jpg").touch()
        (tmp_path / "IMG_002.jpg").touch()

        with patch.object(
            sys,
            "argv",
            [
                "sk-rename",
                r"IMG_(\d+)",
                r"photo_\1",
                str(tmp_path),
                "--dry-run",
            ],
        ):
            main()

        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out
        assert "IMG_001.jpg → photo_001.jpg" in captured.out
        assert "IMG_002.jpg → photo_002.jpg" in captured.out

        # Files should not be renamed
        assert (tmp_path / "IMG_001.jpg").exists()
        assert (tmp_path / "IMG_002.jpg").exists()
        assert not (tmp_path / "photo_001.jpg").exists()

    def test_rename_with_confirmation(self, tmp_path, capsys):
        # Create test files
        (tmp_path / "test_001.txt").touch()
        (tmp_path / "test_002.txt").touch()

        with patch.object(
            sys,
            "argv",
            ["sk-rename", r"test_(\d+)", r"file_\1", str(tmp_path), "--yes"],
        ):
            main()

        # Files should be renamed
        assert (tmp_path / "file_001.txt").exists()
        assert (tmp_path / "file_002.txt").exists()
        assert not (tmp_path / "test_001.txt").exists()

    def test_rename_recursive(self, tmp_path, capsys):
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "IMG_001.jpg").touch()
        (subdir / "IMG_002.jpg").touch()

        with patch.object(
            sys,
            "argv",
            [
                "sk-rename",
                r"IMG_(\d+)",
                r"photo_\1",
                str(tmp_path),
                "--recursive",
                "--dry-run",
            ],
        ):
            main()

        captured = capsys.readouterr()
        # Should find both files
        assert "Found 2 file(s)" in captured.out

    def test_rename_no_matches(self, tmp_path, capsys):
        (tmp_path / "test.txt").touch()

        with patch.object(
            sys,
            "argv",
            ["sk-rename", r"IMG_(\d+)", r"photo_\1", str(tmp_path)],
        ):
            main()

        captured = capsys.readouterr()
        assert "No files match" in captured.out

    def test_rename_invalid_directory(self, capsys):
        with patch.object(
            sys,
            "argv",
            ["sk-rename", r"test", r"new", "/nonexistent/directory"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "does not exist" in captured.err

    def test_rename_current_directory(self, tmp_path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "old_001.txt").touch()

        with patch.object(
            sys,
            "argv",
            ["sk-rename", r"old_(\d+)", r"new_\1", "--dry-run"],
        ):
            main()

        captured = capsys.readouterr()
        assert "old_001.txt → new_001.txt" in captured.out

    def test_rename_collision_error(self, tmp_path, capsys):
        # Create files that would collide after rename
        (tmp_path / "IMG_001.jpg").touch()
        (tmp_path / "IMG_002.jpg").touch()

        # Pattern that makes both files rename to same name
        with patch.object(
            sys,
            "argv",
            ["sk-rename", r"IMG_\d+", "photo", str(tmp_path)],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Error:" in captured.err

    def test_rename_invalid_regex(self, tmp_path, capsys):
        (tmp_path / "test.txt").touch()

        with patch.object(
            sys,
            "argv",
            ["sk-rename", r"[invalid(regex", r"test", str(tmp_path)],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Error:" in captured.err

    def test_help(self):
        with patch.object(sys, "argv", ["sk-rename", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
