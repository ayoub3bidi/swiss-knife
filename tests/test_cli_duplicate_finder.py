import json
from unittest.mock import patch

import pytest

from swiss_knife.cli.duplicate_finder import main


class TestCLIDuplicateFinder:
    def test_main_help(self):
        with patch("sys.argv", ["sk-duplicates", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_no_duplicates_found(self, tmp_path):
        # Create unique files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")

        with patch("sys.argv", ["sk-duplicates", str(tmp_path)]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called_with("No duplicates found.")

    def test_main_duplicates_found(self, tmp_path):
        # Create duplicate files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)

        with patch("sys.argv", ["sk-duplicates", str(tmp_path)]):
            with patch("builtins.print") as mock_print:
                main()

                # Check that duplicate information was printed
                print_calls = [call.args[0] for call in mock_print.call_args_list]
                assert any(
                    "Found" in call and "duplicate" in call for call in print_calls
                )
                assert any("Group 1" in call for call in print_calls)

    def test_main_with_algorithm(self, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "test content"
        file1.write_text(content)
        file2.write_text(content)

        with patch("sys.argv", ["sk-duplicates", str(tmp_path), "--algorithm", "md5"]):
            with patch("builtins.print") as mock_print:
                main()

                print_calls = [call.args[0] for call in mock_print.call_args_list]
                assert any(
                    "Found" in call and "duplicate" in call for call in print_calls
                )

    def test_main_with_min_size(self, tmp_path):
        # Create small duplicate files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "x"  # 1 byte
        file1.write_text(content)
        file2.write_text(content)

        # Set min-size to 10 bytes (larger than our files)
        with patch("sys.argv", ["sk-duplicates", str(tmp_path), "--min-size", "10"]):
            with patch("builtins.print") as mock_print:
                main()
                mock_print.assert_called_with("No duplicates found.")

    def test_main_export_json(self, tmp_path):
        # Create duplicate files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)

        json_file = tmp_path / "results.json"

        with patch(
            "sys.argv",
            ["sk-duplicates", str(tmp_path), "--export-json", str(json_file)],
        ):
            with patch("builtins.print") as mock_print:
                main()

                # Check JSON file was created and contains data
                assert json_file.exists()
                with open(json_file) as f:
                    data = json.load(f)
                assert len(data) > 0  # Should have duplicate groups

                # Check export message was printed
                print_calls = [call.args[0] for call in mock_print.call_args_list]
                assert any("Results exported to" in call for call in print_calls)

    def test_main_delete_duplicates_with_confirmation(self, tmp_path):
        # Create duplicate files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)

        with patch("sys.argv", ["sk-duplicates", str(tmp_path), "--delete-duplicates"]):
            with patch("builtins.print") as mock_print:
                with patch(
                    "swiss_knife.file_management.duplicate_finder.DuplicateFinder.delete_duplicates"
                ) as mock_delete:
                    mock_delete.return_value = 1
                    main()

                    # Check delete was called
                    mock_delete.assert_called_once()

                    # Check deletion message was printed
                    print_calls = [call.args[0] for call in mock_print.call_args_list]
                    assert any(
                        "Deleted 1 duplicate files" in call for call in print_calls
                    )

    def test_main_delete_duplicates_skip_confirmation(self, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)

        with patch(
            "sys.argv", ["sk-duplicates", str(tmp_path), "--delete-duplicates", "--yes"]
        ):
            with patch("builtins.print"):
                with patch(
                    "swiss_knife.file_management.duplicate_finder.DuplicateFinder.delete_duplicates"
                ) as mock_delete:
                    mock_delete.return_value = 2
                    main()

                    # Verify delete was called with yes=True
                    args, kwargs = mock_delete.call_args
                    assert (
                        kwargs.get("force", False) or args[2]
                    )  # yes parameter

    def test_main_keep_strategy(self, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "duplicate content"
        file1.write_text(content)
        file2.write_text(content)

        with patch(
            "sys.argv",
            [
                "sk-duplicates",
                str(tmp_path),
                "--delete-duplicates",
                "--keep-strategy",
                "shortest_name",
            ],
        ):
            with patch("builtins.print"):
                with patch(
                    "swiss_knife.file_management.duplicate_finder.DuplicateFinder.delete_duplicates"
                ) as mock_delete:
                    mock_delete.return_value = 1
                    main()

                    # Verify delete was called with correct strategy
                    args, kwargs = mock_delete.call_args
                    assert args[1] == "shortest_name"  # keep_strategy parameter

    def test_main_multiple_paths(self, tmp_path):
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        # Create files in both directories
        (dir1 / "file.txt").write_text("content")
        (dir2 / "file.txt").write_text("different")

        with patch("sys.argv", ["sk-duplicates", str(dir1), str(dir2)]):
            with patch("builtins.print") as mock_print:
                main()
                # Should process both directories without error
                mock_print.assert_called_with("No duplicates found.")

    def test_main_invalid_algorithm(self):
        with patch("sys.argv", ["sk-duplicates", "/tmp", "--algorithm", "invalid"]):
            with pytest.raises(SystemExit):
                main()

    def test_main_nonexistent_path(self):
        from swiss_knife.core import ValidationError

        with patch("sys.argv", ["sk-duplicates", "/nonexistent/path"]):
            with patch("builtins.print"):
                with pytest.raises(ValidationError):
                    main()
