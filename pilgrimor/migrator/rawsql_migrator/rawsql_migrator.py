import re
from os import listdir
from os.path import isfile, join
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from packaging.version import parse as version_parse

from pilgrimor.abc.migrator import BaseMigrator
from pilgrimor.exceptions import (
    BiggerVersionsExistsError,
    IncorrectMigrationHistoryError,
    MigrationNumberRepeatNumberError,
    NoNewMigrationsError,
    VersionAlreadyExistsError,
    WrongMigrationNumberError,
)
from pilgrimor.utils import error_text, success_text, warning_text


class RawSQLMigator(BaseMigrator):
    """
    Migrator for .sql files.

    Can apply migration and monitor the state of the database.
    """

    def initialize_database(self) -> None:
        """Initialize new table for migration control."""
        query = """
        CREATE TABLE pilgrimor (
            id SERIAL,
            name VARCHAR(100) NOT NULL,
            version VARCHAR(25) NOT NULL
        )
        """
        self.engine.execute_sql_with_no_return(
            sql_query=query,
            sql_query_params=None,
        )
        print(success_text("Database initialized!"))

    def _get_migrations_with_version(self, version: str) -> List[str]:
        """
        Returns new migrations.

        Workflow:
        Firstly, check is version already exists,
        if yes print error message and stop the migrator.
        Secondly, check is version bigger exists,
        if yes, print what version(s) is bigger and
        stop the migrator.
        Thirdly, get migration to apply, if there are no new
        migrations print attention message and stop the migrator.
        Fourth, get apply commands, because every migration
        file must have `apply` and `rollback` sections.
        Fifth, apply new migrations and create new record in
        pilgrimor table.

        :param version: version for new migrations.

        :raises VersionAlreadyExistsError: if version is already exists.
        :raises BiggerVersionsExistsError: if bigger versions are exists.
        :raises NoNewMigrationsError: if no new migrations.

        :returns: migrations that will be applied.
        """
        if self._is_version_exists(version=version):
            raise VersionAlreadyExistsError(
                f"Version {version} already exists. Please choose another one.",
            )
        if bigger_versions := self._is_version_bigger_exists(version=version):
            raise BiggerVersionsExistsError(
                f"There are bigger versions - {', '.join(bigger_versions)}"
                f"Please choose another version.",
            )

        if not (to_apply_migrations := self._get_to_apply_migrations()):
            raise NoNewMigrationsError("There are no new migrations to apply.")

        return list(to_apply_migrations)

    def _get_exist_migrations(self) -> Dict[str, List[str]]:  # noqa: WPS210
        """
        Returns migrations with a known version.

        Iterate through the existing migration files
        and try to find an indication of which
        version this migration is linked to.

        In case a situation arises when the previous
        migration did not have a version,
        but the one we are considering has,
        stop the migration and report
        that the migration history is incorrect

        :raises IncorrectMigrationHistoryError: if incorrect migration history.

        :returns: Dict with keys as version and value as list of migrations.
        """
        all_migrations = self._get_migration_files()
        is_previous_migration_has_version = True
        to_apply_migration: Dict[str, List[str]] = {}

        for migration in all_migrations:
            full_path_migration = join(self.migrations_dir, migration)
            with open(full_path_migration, "r") as migration_file:
                migration_context = migration_file.read()

                search_result = re.search(
                    r"pilgrimore_version.*\n",
                    migration_context,
                )
                if search_result:
                    if not is_previous_migration_has_version:
                        raise IncorrectMigrationHistoryError(  # noqa: WPS220
                            "Incorrect migration history",
                        )
                    migration_version = search_result.group().split(
                        " ",
                    )[1]
                    to_apply_migration.setdefault(
                        migration_version,
                        [],
                    ).append(migration)
                    is_previous_migration_has_version = True
                else:
                    is_previous_migration_has_version = False

        return to_apply_migration

    def _get_rollback_migration_by_version(self, version: str) -> List[str]:
        """
        Rolls back migrations to specified version.

        :param version: version to which it is rolled back

        :raises VersionAlreadyExistsError: if version is already exists.

        :returns: migrations by selected version.
        """
        if not self._is_version_exists(version=version):
            raise VersionAlreadyExistsError(
                f"Can't find version - {version} in migrations. "
                f"Please choose another one.",
            )

        return self._get_migrations_by_version(version=version)

    def _get_rollback_migration_query(self, migration: str) -> str:
        """
        Return full rollback migration query with technical table record.

        :param migration: rollback migration.

        :returns: full migration query.
        """
        query = Path(
            join(self.migrations_dir, migration),
        ).read_text()
        try:
            rollback_query = query.split("-- rollback --")[1]
        except KeyError:
            print(
                warning_text(
                    f"You don't split apply and rollback "
                    f"context in migration {migration}."
                    f"Can't rollback this migration.",
                ),
            )
            return ""
        return self._drop_migration_from_system_table(
            rollback_query,
            migration,
        )

    def _get_apply_migration_query(
        self,
        migration: str,
        version: str,
    ) -> str:
        """
        Return full apply migration query with technical table record.

        :param migration: rollback migration.
        :param version: migration version.

        :returns: full migration query.
        """
        query = Path(
            join(self.migrations_dir, migration),
        ).read_text()
        try:
            apply_query = query.split("-- rollback --")[0]
        except KeyError:
            print(
                warning_text(
                    f"You don't split apply and rollback context in migration "
                    f"{migration}. All commands will be applied.",
                ),
            )
            apply_query = query
        return self._add_migration_to_system_table(
            apply_query,
            migration,
            version,
        )

    def _get_version_migrations(  # noqa: WPS234
        self,
        migrations: List[str],
        is_rollback: bool,
        version: str = "",
    ) -> Tuple[List[Dict[str, str]], bool]:
        """
        Confirm list with migrations data.

        :param is_rollback: rollback or apply migrations.
        :param migrations: List of migration to apply.
        :param version: migration version.
        :returns: list of dicts with migrations and is_concurrently flag.
        """
        version_migrations = []
        is_concurrently = False
        for migration in migrations:
            if is_rollback:
                to_execute_query = self._get_rollback_migration_query(migration)
                if not to_execute_query:
                    continue
            else:
                to_execute_query = self._get_apply_migration_query(migration, version)

            if "concurrently" in to_execute_query.lower():
                is_concurrently = True

            version_migrations.append(
                {
                    "migration": migration,
                    "query": to_execute_query,
                },
            )
        return version_migrations, is_concurrently

    def _apply_migrations(self, migrations: List[str], version: str) -> None:
        """
        Applies new migrations.

        Get migration text from migration, try to get
        apply context, if not found, use all migration
        as apply context.

        Add system query into migration query.

        After success migration add migration version to
        the migration file.
        If any exception is raised, rollback applied migration
        and stop the migrator.

        :param migrations: List of migration to apply.
        :param version: migration version.
        """
        version_migrations, is_concurrently = self._get_version_migrations(
            migrations,
            is_rollback=False,
            version=version,
        )

        self.engine.execute_version_migrations(
            version_migrations=version_migrations,
            sql_query_params=None,
            in_transaction=not is_concurrently,
        )

        self._add_version_to_migration_file(
            migrations=migrations,
            version=version,
        )

    def _rollback_migrations(  # noqa: WPS324
        self,
        migrations: List[str],
        **kwargs: Any,
    ) -> None:
        """
        Rolls back migration.

        Get migration text from migration, try to get
        rollback context, if not found, do not rollback migration.

        :param migrations: List of migration to apply.
        :param kwargs: any named arguments.
        """
        version_migrations, is_concurrently = self._get_version_migrations(
            migrations,
            is_rollback=True,
        )

        self.engine.execute_version_migrations(
            version_migrations=version_migrations,
            sql_query_params=None,
            in_transaction=not is_concurrently,
        )

    def _get_to_apply_migrations(self) -> List[str]:
        """
        Gets new migrations.

        Get all applied migrations and all exist migrations.
        If there are no applied_migrations, return all_migrations.
        Else find difference between all_migrations and applied_migrations.

        :returns: set of new migrations.
        """
        applied_migrations = self._get_applied_migrations()
        all_migrations = self._get_migration_files()

        if applied_migrations:
            to_apply_migrations = set(all_migrations) - set(applied_migrations)
        else:
            to_apply_migrations = set(all_migrations)

        return self._sort_migrations(to_apply_migrations)

    def _get_migration_files(self) -> List[str]:
        """
        Returns all migration files.

        :returns: list with migratons.
        """
        all_migrations = {
            sql_file
            for sql_file in listdir(self.migrations_dir)
            if isfile(join(self.migrations_dir, sql_file))
        }

        self._check_migrations_number(all_migrations)

        return self._sort_migrations(all_migrations)

    def _get_applied_migrations(self) -> List[str]:
        """
        Returns all applied migrations from database.

        :returns: list with migrations.
        """
        query = """
        SELECT name
        FROM pilgrimor
        """

        query_result = self.engine.execute_sql_with_return(
            sql_query=query,
            sql_query_params=None,
        )
        return query_result if query_result else []

    def _get_last_applied_migrations(self) -> List[str]:
        """
        Returns last applied migrations.

        :returns: set of last applied migrations.
        """
        query = """
        SELECT name
        FROM pilgrimor
        WHERE version = (
            SELECT version
            FROM pilgrimor
            ORDER BY id DESC
            LIMIT 1
        )
        """

        migrations = self.engine.execute_sql_with_return(
            sql_query=query,
            sql_query_params=None,
        )

        return self._sort_migrations(
            migrations if migrations else [],
            desc=True,
        )

    def _get_migrations_by_version(self, version: str) -> List[str]:
        """
        Returns all migrations by version.

        :param version: migration version.

        :returns: set with migratons.
        """
        query = """
        SELECT name
        FROM pilgrimor
        WHERE version = %s
        OR id > (
            SELECT id
            FROM pilgrimor
            WHERE version = %s
            ORDER BY id DESC
            LIMIT 1
        )
        """

        result = self.engine.execute_sql_with_return(
            sql_query=query,
            sql_query_params=[version, version],
        )

        return self._sort_migrations(
            result if result else [],
            desc=True,
        )

    def _is_version_exists(self, version: str) -> bool:
        """
        Checks is version exists.

        :param version: version number.

        :returns: True if version exists else False.
        """
        query = """
        SELECT EXISTS(
            SELECT version
            FROM pilgrimor
            WHERE version = %s
        )
        """
        result: Optional[List[bool]] = self.engine.execute_sql_with_return(
            sql_query=query,
            sql_query_params=[version],
        )
        return result[0] if result else False

    def _is_version_bigger_exists(
        self,
        version: str,
    ) -> Optional[Tuple[str, ...]]:
        """
        Checks if there are migrations higher in version than the specified one.

        If yes then return tuple with versions
        that are higher than the specified one.
        Else return None.

        :param version: version of new migrations.

        :returns: tuple with versions or None.
        """
        query = """
        SELECT version
        FROM pilgrimor
        GROUP BY version
        """
        versions = self.engine.execute_sql_with_return(
            sql_query=query,
            sql_query_params=None,
        )
        if versions:
            return tuple(
                exist_version
                for exist_version in versions
                if version_parse(exist_version) > version_parse(version)
            )

        return None

    def _check_migrations_number(self, migrations: Set[str]) -> None:
        """
        Checks migrations number.

        Migration numbers can not repeat and should
        start with <number>_.

        :param migrations: migrations.

        :raises WrongMigrationNumberError: if migration has wrong number.
        :raises MigrationNumberRepeatNumberError: migration number duplicates.
        """
        exists_numbers = []
        for migration in migrations:
            try:
                migration_number = int(migration.split("_")[0])
            except (KeyError, ValueError):
                raise WrongMigrationNumberError(
                    f"There is migration with wrong number - {migration}\n"
                    f"Migration name must be - <number>_<migration_name>.sql",
                )
            if migration_number in exists_numbers:
                raise MigrationNumberRepeatNumberError(
                    f"There are two or more migrations with number {migration_number}",
                )
            exists_numbers.append(migration_number)

    def _sort_migrations(
        self,
        migrations: Iterable[str],
        desc: bool = False,
    ) -> List[str]:
        """
        Sort migrations.

        :param migrations: List of migrations.
        :param desc: reverse or not.

        :returns: sorted list of migrations
        """

        def get_migration_number(file_name: str) -> str:  # noqa: WPS430
            return file_name.split("_")[0]

        return sorted(migrations, key=get_migration_number, reverse=desc)

    def _add_migration_to_system_table(
        self,
        query: str,
        migration: str,
        version: str,
    ) -> str:
        """
        Inserts new migration to pilgrimor database.

        :param query: query from migration.
        :param migration: migration.
        :param version: version.

        :returns: query
        """
        system_command = f"""
        INSERT INTO pilgrimor (name, version)
        VALUES ('{migration}', '{version}');
        """
        return "{0}{1}{2}".format(query, "\n", system_command)

    def _drop_migration_from_system_table(
        self,
        query: str,
        migration: str,
    ) -> str:
        """
        Drop migration from pilgrimor database.

        :param query: query from migration.
        :param migration: migration.

        :returns: query
        """
        system_command = f"""
        DELETE FROM pilgrimor
        WHERE name = '{migration}';
        """
        return "{0}{1}{2}".format(query, "\n", system_command)

    def _add_version_to_migration_file(
        self,
        migrations: List[str],
        version: str,
    ) -> None:
        """
        Adds migration version to migration file.

        :param migrations: List of migration to apply.
        :param version: migration version.
        """
        for migration in migrations:
            query = Path(
                join(self.migrations_dir, migration),
            ).read_text()
            if query.find("pilgrimore_version") == -1:
                try:
                    path_to_migration = join(self.migrations_dir, migration)
                    with open(path_to_migration, "a") as migration_file:
                        migration_file.write(  # noqa: WPS220
                            f"\n-- pilgrimore_version {version} -- \n",
                        )
                except Exception as exc:
                    print(
                        error_text(
                            f"Can't set version in migration file\n"
                            f"Rolling back migrations {migrations}\n"
                            f"Reason - {exc}",
                        ),
                    )
                    self._rollback_migrations(migrations=migrations)
