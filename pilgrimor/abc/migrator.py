from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pilgrimor.abc.engine import PilgrimoreEngine
from pilgrimor.exceptions import ApplyMigrationsError
from pilgrimor.utils import success_text


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
        self.engine = engine
        self.migrations_dir = migration_dir

    @abstractmethod
    def initialize_database(self) -> None:
        """Initialize new table for migration control."""

    def apply_migrations(self, version: Optional[str]) -> None:
        """
        Applies new migrations.

        If the version is not specified,
        then we apply migrations with an already known version.
        If the version is specified,
        get new migrations and apply them.

        :param version: version for new migrations.
        """
        if version:
            self.run_migrations(
                self._get_migrations_with_version(version=version),
                version,
            )
        else:
            for m_version, migrations in self._get_exist_migrations().items():
                self.run_migrations(migrations, m_version)

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

        self.run_migrations(
            migrations=to_rollback_migations,
            apply=False,
        )

    def run_migrations(  # noqa: C901
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
        :param version: migration version.
        :param apply: to apply or not.

        :raises ApplyMigrationsError: error in migrations.
        """
        if apply:
            command = "apply"
        else:
            command = "rollback"
        try:
            if apply and version:
                self._apply_migrations(migrations=migrations, version=version)
            elif not apply:
                self._rollback_migrations(migrations=migrations)
        except Exception as exc:
            raise ApplyMigrationsError from exc
        print(success_text(f"Command {command} done."))

    @abstractmethod
    def _apply_migrations(self, migrations: List[str], version: str) -> None:
        """
        Applies new migration.

        Get migration text from migration, try to get
        apply context, if not found, use all migration
        as apply context.

        Add system query into migration query.

        After success migration add migration version to
        the migration file.
        If any exception is raised, rollback applied migration
        and stop the migrator.

        :param migrations: List of migration.
        :param version: migration version.
        """

    @abstractmethod
    def _rollback_migrations(  # noqa: WPS324
        self,
        migrations: List[str],
    ) -> None:
        """
        Rolls back migration.

        Get migration text from migration, try to get
        rollback context, if not found, do not rollback migration.

        :param migrations: List of migration.

        :returns: None.
        """

    @abstractmethod
    def _get_exist_migrations(self) -> Dict[str, List[str]]:
        """
        Returns migrations with a known version.

        In case a situation arises when the previous
        migration did not have a version,
        but the one we are considering has,
        stop the migration and report
        that the migration history is incorrect

        :raises IncorrectMigrationHistoryError: if incorrect migration history.

        :returns: Dict with keys as version and value as list of migrations.
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
