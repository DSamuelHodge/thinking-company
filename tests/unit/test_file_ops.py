"""Unit tests for file operation utilities."""

from __future__ import annotations

from pathlib import Path

import pytest

from restack_gen.utils.file_ops import (
    FileOperationError,
    copy_file,
    delete_path,
    ensure_directory,
    list_files,
    read_file,
    write_file,
)


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_creates_new_directory(self, temp_dir: Path) -> None:
        """Test creating a new directory."""
        new_dir = temp_dir / "test_dir"
        result = ensure_directory(new_dir)
        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_creates_nested_directories(self, temp_dir: Path) -> None:
        """Test creating nested directory structure."""
        nested = temp_dir / "a" / "b" / "c"
        result = ensure_directory(nested)
        assert result == nested
        assert nested.exists()

    def test_existing_directory_no_error(self, temp_dir: Path) -> None:
        """Test existing directory doesn't raise error by default."""
        existing = temp_dir / "existing"
        existing.mkdir()
        result = ensure_directory(existing)
        assert result == existing


class TestWriteFile:
    """Tests for write_file function."""

    def test_writes_new_file(self, temp_dir: Path) -> None:
        """Test writing a new file."""
        file_path = temp_dir / "test.txt"
        content = "Hello, World!"
        write_file(file_path, content)
        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == content

    def test_creates_parent_directories(self, temp_dir: Path) -> None:
        """Test write_file creates parent directories."""
        file_path = temp_dir / "nested" / "dir" / "file.txt"
        write_file(file_path, "content")
        assert file_path.exists()

    def test_existing_file_without_overwrite_raises(self, temp_dir: Path) -> None:
        """Test writing to existing file without overwrite flag raises error."""
        file_path = temp_dir / "existing.txt"
        file_path.write_text("original")

        with pytest.raises(FileOperationError) as exc_info:
            write_file(file_path, "new content", overwrite=False)
        assert "already exists" in str(exc_info.value)

    def test_existing_file_with_overwrite_succeeds(self, temp_dir: Path) -> None:
        """Test overwriting existing file with overwrite=True."""
        file_path = temp_dir / "existing.txt"
        file_path.write_text("original")
        write_file(file_path, "replaced", overwrite=True)
        assert file_path.read_text(encoding="utf-8") == "replaced"


class TestReadFile:
    """Tests for read_file function."""

    def test_reads_file_content(self, temp_dir: Path) -> None:
        """Test reading file content."""
        file_path = temp_dir / "test.txt"
        expected = "Test content\nMultiline"
        file_path.write_text(expected, encoding="utf-8")
        result = read_file(file_path)
        assert result == expected

    def test_nonexistent_file_raises(self, temp_dir: Path) -> None:
        """Test reading non-existent file raises error."""
        file_path = temp_dir / "missing.txt"
        with pytest.raises(FileOperationError) as exc_info:
            read_file(file_path)
        assert "Failed to read" in str(exc_info.value)


class TestCopyFile:
    """Tests for copy_file function."""

    def test_copies_file(self, temp_dir: Path) -> None:
        """Test copying a file."""
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        source.write_text("content")

        copy_file(source, dest)
        assert dest.exists()
        assert dest.read_text(encoding="utf-8") == "content"

    def test_creates_dest_parent_directories(self, temp_dir: Path) -> None:
        """Test copy_file creates destination parent directories."""
        source = temp_dir / "source.txt"
        dest = temp_dir / "nested" / "dir" / "dest.txt"
        source.write_text("content")

        copy_file(source, dest)
        assert dest.exists()

    def test_existing_dest_without_overwrite_raises(self, temp_dir: Path) -> None:
        """Test copying to existing destination without overwrite raises error."""
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        source.write_text("source content")
        dest.write_text("dest content")

        with pytest.raises(FileOperationError) as exc_info:
            copy_file(source, dest, overwrite=False)
        assert "already exists" in str(exc_info.value)

    def test_existing_dest_with_overwrite_succeeds(self, temp_dir: Path) -> None:
        """Test copying with overwrite=True replaces destination."""
        source = temp_dir / "source.txt"
        dest = temp_dir / "dest.txt"
        source.write_text("new content")
        dest.write_text("old content")

        copy_file(source, dest, overwrite=True)
        assert dest.read_text(encoding="utf-8") == "new content"


class TestListFiles:
    """Tests for list_files function."""

    def test_lists_all_files(self, temp_dir: Path) -> None:
        """Test listing all files in directory."""
        (temp_dir / "file1.txt").touch()
        (temp_dir / "file2.py").touch()
        (temp_dir / "subdir").mkdir()

        files = list(list_files(temp_dir))
        assert len(files) == 3
        assert temp_dir / "file1.txt" in files
        assert temp_dir / "file2.py" in files
        assert temp_dir / "subdir" in files

    def test_lists_with_pattern(self, temp_dir: Path) -> None:
        """Test listing files with glob pattern."""
        (temp_dir / "file1.txt").touch()
        (temp_dir / "file2.txt").touch()
        (temp_dir / "file3.py").touch()

        txt_files = list(list_files(temp_dir, pattern="*.txt"))
        assert len(txt_files) == 2
        assert all(f.suffix == ".txt" for f in txt_files)

    def test_empty_directory(self, temp_dir: Path) -> None:
        """Test listing files in empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        files = list(list_files(empty_dir))
        assert len(files) == 0


class TestDeletePath:
    """Tests for delete_path function."""

    def test_deletes_file(self, temp_dir: Path) -> None:
        """Test deleting a file."""
        file_path = temp_dir / "to_delete.txt"
        file_path.write_text("content")
        delete_path(file_path)
        assert not file_path.exists()

    def test_deletes_directory_recursively(self, temp_dir: Path) -> None:
        """Test deleting a directory with contents."""
        dir_path = temp_dir / "to_delete"
        dir_path.mkdir()
        (dir_path / "file1.txt").touch()
        (dir_path / "subdir").mkdir()
        (dir_path / "subdir" / "file2.txt").touch()

        delete_path(dir_path)
        assert not dir_path.exists()

    def test_deleting_nonexistent_path_no_error(self, temp_dir: Path) -> None:
        """Test deleting non-existent path doesn't raise error."""
        nonexistent = temp_dir / "nonexistent"
        delete_path(nonexistent)  # Should not raise
