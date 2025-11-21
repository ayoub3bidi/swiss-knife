import pytest

from swiss_knife.file_management.duplicate_finder import (
    DuplicateFinder,
    find_duplicates,
)


class TestDuplicateFinder:

    def test_init_valid_algorithm(self):
        finder = DuplicateFinder("sha256", min_size=100)
        assert finder.algorithm == "sha256"
        assert finder.min_size == 100

    def test_init_invalid_algorithm(self):
        with pytest.raises(ValueError):
            DuplicateFinder("invalid_algo")

    def test_find_duplicates_empty_directory(self, tmp_path):
        finder = DuplicateFinder()
        duplicates = finder.find_duplicates([tmp_path])
        assert duplicates == {}

    def test_find_duplicates_no_duplicates(self, tmp_path):
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates([tmp_path])
        assert duplicates == {}

    def test_find_duplicates_with_duplicates(self, tmp_path):
        content = "duplicate content"
        (tmp_path / "file1.txt").write_text(content)
        (tmp_path / "file2.txt").write_text(content)
        (tmp_path / "unique.txt").write_text("unique content")

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates([tmp_path])

        assert len(duplicates) == 1
        duplicate_files = list(duplicates.values())[0]
        assert len(duplicate_files) == 2

        file_names = {f.name for f in duplicate_files}
        assert file_names == {"file1.txt", "file2.txt"}

    def test_min_size_filter(self, tmp_path):
        content = "small"
        (tmp_path / "small1.txt").write_text(content)
        (tmp_path / "small2.txt").write_text(content)

        finder = DuplicateFinder(min_size=100)
        duplicates = finder.find_duplicates([tmp_path])
        assert duplicates == {}

        finder = DuplicateFinder(min_size=1)
        duplicates = finder.find_duplicates([tmp_path])
        assert len(duplicates) == 1

    def test_delete_duplicates_first_strategy(self, tmp_path):
        content = "duplicate content"
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text(content)
        file2.write_text(content)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates([tmp_path])

        deleted = finder.delete_duplicates(duplicates, "first", force=True)

        assert deleted == 1
        assert file1.exists()  # First file should be kept
        assert not file2.exists()  # Second file should be deleted

    def test_delete_duplicates_shortest_name_strategy(self, tmp_path):
        content = "duplicate content"
        short_file = tmp_path / "a.txt"
        long_file = tmp_path / "very_long_filename.txt"
        short_file.write_text(content)
        long_file.write_text(content)

        finder = DuplicateFinder()
        duplicates = finder.find_duplicates([tmp_path])

        deleted = finder.delete_duplicates(duplicates, "shortest_name", force=True)

        assert deleted == 1
        assert short_file.exists()  # Shorter name should be kept
        assert not long_file.exists()  # Longer name should be deleted


def test_find_duplicates_convenience_function(tmp_path):
    content = "duplicate content"
    (tmp_path / "file1.txt").write_text(content)
    (tmp_path / "file2.txt").write_text(content)

    duplicates = find_duplicates([str(tmp_path)])

    assert len(duplicates) == 1
    duplicate_files = list(duplicates.values())[0]
    assert len(duplicate_files) == 2

    # Should return string paths
    assert all(isinstance(path, str) for path in duplicate_files)
