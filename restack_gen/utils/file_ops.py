"""Utility functions for file system operations used by generators."""

from __future__ import annotations

import shutil
from collections.abc import Iterable
from pathlib import Path


class FileOperationError(Exception):
    """Raised when a file operation fails."""


def ensure_directory(path: Path, exist_ok: bool = True) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    try:
        path.mkdir(parents=True, exist_ok=exist_ok)
    except Exception as exc:
        raise FileOperationError(f"Failed to create directory {path}") from exc
    return path


def write_file(path: Path, content: str, overwrite: bool = False) -> None:
    """Write text content to a file."""
    if path.exists() and not overwrite:
        raise FileOperationError(f"File already exists: {path}")
    try:
        ensure_directory(path.parent)
        path.write_text(content, encoding="utf-8")
    except Exception as exc:
        raise FileOperationError(f"Failed to write file {path}") from exc


def read_file(path: Path) -> str:
    """Read text content from a file."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        raise FileOperationError(f"Failed to read file {path}") from exc


def copy_file(source: Path, destination: Path, overwrite: bool = False) -> None:
    """Copy file from source to destination."""
    if destination.exists() and not overwrite:
        raise FileOperationError(f"Destination file already exists: {destination}")
    try:
        ensure_directory(destination.parent)
        shutil.copy2(source, destination)
    except Exception as exc:
        raise FileOperationError(f"Failed to copy {source} to {destination}") from exc


def list_files(directory: Path, pattern: str | None = None) -> Iterable[Path]:
    """Iterate over files in a directory, optionally filtered by glob pattern."""
    try:
        if pattern:
            return directory.glob(pattern)
        return directory.iterdir()
    except Exception as exc:
        raise FileOperationError(f"Failed to list files in {directory}") from exc


def delete_path(path: Path) -> None:
    """Delete file or directory recursively."""
    try:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    except Exception as exc:
        raise FileOperationError(f"Failed to delete {path}") from exc
