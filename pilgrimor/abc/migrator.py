from abc import ABC, abstractmethod
import sys
from typing import List, Optional

from pilgrimor.abc.engine import PilgrimoreEngine
from pilgrimor.utils import sprint


class BaseMigrator(ABC):
    """
    Base migrator.

    Can make 3 base operations:
        1) Create new migrations.
        2) Apply migrations.
        3) Rollback migrations.
    """

    def __init__(self, engine: PilgrimoreEngine, migration_dir: str) -> None:
        """
        Initializes the migrator.

        :param engine: Migration engine.
        :param migration_dir: path to the directory with migration files.
        """

    @abstractmethod
    def initialize_database(self) -> None:
        """Initialize new table for migration control."""

    def apply_migations(self, version: Optional[str]) -> None:
        """
        Applies new migrations.

        If the version is not specified,
        then we apply migrations with an already known version.
        If the version is specified,
        get new migrations and apply them.

        :param version: version for new migrations.
        """
        to_apply_migrations = []

        if not version:
            to_apply_migrations = self._get_exist_migrations()
        if version:
            to_apply_migrations = self._get_migrations_with_version(version=version)

        self.run_migrations(to_apply_migrations, version)

    def rollback_migrations(
        self,
        version: Optional[str] = None,
        latest: bool = False,
    ) -> None:
        """
        Rolls back migrations.

        There are two options - version and latest.
        If version was choosen, downgrade the version
        of migrations to the specified version
        and rollback all migrations that were
        before this version inclusive

        If latest is specifed, only migration based on latest
        version will be rolled back.

        :param version: version for migrations.
        :param latest: rollback only latests migrations.
        """
        if version:
            to_rollback_migations = self._get_rollback_migration_by_version(version)
        if latest:
            to_rollback_migations = self._get_last_applied_migrations()

        self.run_migrations(to_rollback_migations)

    def run_migrations(
        self,
        migrations: List[str],
        version: Optional[str] = None,
        apply: bool = True,
    ) -> None:
        """
        Runs migrations.

        If apply is True, apply new migrations.
        Else roll back migrations.

        :param migrations: List of migration.
        :param apply: to apply or not.
        """
        if apply:
            to_run_func = self._apply_migration
            command = "apply"
        else:
            to_run_func = self._rollback_migration
            command = "rollback"
        success_migrations = []

        for migration in migrations:
            try:
                to_run_func(migration=migration, version=version)
                sprint(f"Command {command} done for {migration}")
                success_migrations.append(migration)
            except Exception as exc:
                not_applied_migrations = set(migrations) - set(success_migrations)
                sys.exit(
                    f"Can't {command} migrations {not_applied_migrations} because "
                    f"there is error - {exc}"
                )

    @abstractmethod
    def _get_exist_migrations(self) -> List[str]:
        """
        Returns migrations with a known version.

        In case a situation arises when the previous
        migration did not have a version,
        but the one we are considering has,
        stop the migration and report
        that the migration history is incorrect

        :raises IncorrectMigrationHistoryError: if incorrect migration history.

        :returns: list of migrations with known versions.
        """

    @abstractmethod
    def _get_migrations_with_version(self, version: str) -> List[str]:
        """
        Returns new migrations by version.

        :param version: version for new migrations.

        :raises VersionAlreadyExistsError: if version is already exists.
        :raises BiggerVersionsExistsError: if bigger versions are exists.
        :raises NoNewMigrationsError: if no new migrations.
        """

    @abstractmethod
    def _get_rollback_migration_by_version(self, version: str) -> List[str]:
        """
        Rolls back migrations to specified version.

        :param version: version to which it is rolled back

        :raises VersionAlreadyExistsError: if version is already exists.
        """

    @abstractmethod
    def _get_last_applied_migrations(self) -> List[str]:
        """
        Returns last applied migrations.

        :returns: set of last applied migrations.
        """
