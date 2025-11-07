"""Migration model for file-based project migrations.

This simple abstraction defines an interface for forward (up) and backward (down)
operations that modify a generated Restack project on disk.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class MigrationMeta:
    """Metadata about a migration.

    Attributes:
        id: A unique identifier, typically a timestamped string like
            "YYYYMMDD_HHMMSS_name" derived from the filename.
        name: Human-friendly migration name.
        created_at: Optional ISO datetime string for when the migration was created.
    """

    id: str
    name: str
    created_at: str | None = None


class Migration(ABC):
    """Base class for all migrations.

    Subclasses should implement ``up`` and ``down`` to mutate files within
    a target project directory.
    """

    def __init__(self, meta: MigrationMeta) -> None:
        self.meta = meta

    @abstractmethod
    def up(self, project_dir: Path, **kwargs: Any) -> None:  # pragma: no cover - abstract
        """Apply the migration.

        Implementations should perform idempotent, forward-only changes. If the
        migration cannot be applied, raise an exception with a helpful message.
        """

    @abstractmethod
    def down(self, project_dir: Path, **kwargs: Any) -> None:  # pragma: no cover - abstract
        """Rollback the migration.

        Implementations should attempt to revert changes made by ``up``. If a
        complete rollback is not possible, perform best-effort and document
        limitations in the migration file.
        """

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Migration id={self.meta.id} name={self.meta.name}>"
