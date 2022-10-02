from abc import ABC, abstractmethod
from typing import List


class BaseMigration(ABC):
    """Base migration for all migrations."""

    # The version of the application to which the migration is linked.
    version: str = ""

    # Migration operations.
    operations: List[str] = []

    # Run all migration commands in transaction or not.
    in_transaction: bool = True

    @abstractmethod
    def build_new_migrations(self):
        """Creates new migrations."""

    @abstractmethod
    def apply(self):
        """Apply migrations."""

    @abstractmethod
    def rollback(self):
        """Rollback migrations."""
