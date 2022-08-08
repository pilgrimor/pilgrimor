from typing import List, Optional, Tuple


class RawSQLMigator:
    """"""

    def __init__(self):
        """"""

    def apply_migrations(self, migrations: List[str]):
        """
        Applies migrations.
        """

    def rollback_migrations(self):
        """"""

    def _apply_migration(self, migration: str) -> bool:
        """"""

    def _rollback_migration(self, migration: str) -> bool:
        """"""

    def get_migration_files(self) -> List[str]:
        """
        Returns all migration files.

        :returns: list with migratons.
        """

    def initialize_database(self):
        """"""

    def get_applied_migrations(self) -> List[str]:
        """"""

    def get_last_applied_version(self) -> str:
        """"""

    def get_migrations_by_version(self) -> List[str]:
        """
        Returns all migrations by version.

        :returns: list with migratons.
        """

    def is_version_exists(self, version: str) -> bool:
        """
        Checks is version exists.
        """

    def is_version_bigger_exists(
        self,
        version: str,
    ) -> Optional[Tuple[str, ...]]:
        """
        Checks if there are migrations higher in version than the specified one.

        If yes then return tuple with versions
        that are higher than the specified one.
        Else return None.

        :returns: tuple with versions or None.
        """

    def check_migrations_name(self):
        """"""

    def sort_migrations(
        self,
        migrations: List[str],
        desc: bool,
    ) -> List[str]:
        """
        Sort migrations.
        """

