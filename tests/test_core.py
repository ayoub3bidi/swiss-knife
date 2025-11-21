from unittest.mock import patch

import pytest

from swiss_knife.core import (
    SafetyError,
    ValidationError,
    check_file_size_limit,
    confirm_destructive_action,
    safe_filename,
    validate_path,
)


class TestCoreUtilities:

    def test_validate_path_existing_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = validate_path(test_file)
        assert result == test_file.resolve()

    def test_validate_path_nonexistent_must_exist(self, tmp_path):
        nonexistent = tmp_path / "nonexistent.txt"

        with pytest.raises(ValidationError):
            validate_path(nonexistent, must_exist=True)

    def test_validate_path_nonexistent_optional(self, tmp_path):
        nonexistent = tmp_path / "nonexistent.txt"

        result = validate_path(nonexistent, must_exist=False)
        assert result == nonexistent.resolve()

    def test_validate_path_string_input(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = validate_path(str(test_file))
        assert result == test_file.resolve()

    @patch("builtins.input", return_value="y")
    def test_confirm_destructive_action_yes(self, mock_input):
        result = confirm_destructive_action("Delete files?")
        assert result is True
        mock_input.assert_called_once_with("Delete files? (y/N): ")

    @patch("builtins.input", return_value="n")
    def test_confirm_destructive_action_no(self, mock_input):
        result = confirm_destructive_action("Delete files?")
        assert result is False

    @patch("builtins.input", return_value="")
    def test_confirm_destructive_action_empty(self, mock_input):
        result = confirm_destructive_action("Delete files?")
        assert result is False

    def test_confirm_destructive_action_force(self):
        result = confirm_destructive_action("Delete files?", force=True)
        assert result is True

    @patch("builtins.input", return_value="yes")
    def test_confirm_destructive_action_yes_full(self, mock_input):
        result = confirm_destructive_action("Delete files?")
        assert result is True

    def test_check_file_size_limit_nonexistent(self, tmp_path):
        nonexistent = tmp_path / "nonexistent.txt"
        # Should not raise exception for nonexistent file
        check_file_size_limit(nonexistent, max_size_mb=1)

    def test_check_file_size_limit_small_file(self, tmp_path):
        small_file = tmp_path / "small.txt"
        small_file.write_text("small content")

        # Should not raise exception for small file
        check_file_size_limit(small_file, max_size_mb=1)

    def test_check_file_size_limit_large_file(self, tmp_path):
        large_file = tmp_path / "large.txt"
        # Create a file larger than 1MB (1MB = 1024*1024 bytes)
        large_content = "x" * (2 * 1024 * 1024)  # 2MB
        large_file.write_text(large_content)

        with pytest.raises(SafetyError):
            check_file_size_limit(large_file, max_size_mb=1)

    def test_safe_filename_basic(self):
        result = safe_filename("normal_file.txt")
        assert result == "normal_file.txt"

    def test_safe_filename_dangerous_chars(self):
        result = safe_filename('file<>:"/\\|?*.txt')
        assert result == "file_________.txt"

    def test_safe_filename_leading_trailing_dots(self):
        result = safe_filename("  .file.  ")
        assert result == "file"

    def test_safe_filename_empty(self):
        result = safe_filename("")
        assert result == "unnamed"

    def test_safe_filename_only_dangerous(self):
        result = safe_filename('<>:"/\\|?*')
        assert result == "_________"


def test_safety_error():
    with pytest.raises(SafetyError):
        raise SafetyError("Test safety error")


def test_validation_error():
    with pytest.raises(ValidationError):
        raise ValidationError("Test validation error")
