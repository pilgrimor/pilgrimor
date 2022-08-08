from os import listdir
from os.path import join, isfile
from typing import List, Optional, Set, Tuple

from pilgrimor.utils import eprint, aprint, wprint, sprint
from packaging.version import parse as version_parse

from pathlib import Path


class RawSQLMigator:
    """"""

    def __init__(self, engine, migration_dir: str) -> None:
        """
        Initialize the migrator.

        :param engine: Engine to execute migrations queries.
        :param migration_dir: path to migrations.
        """
        self.engine = engine
        self.migrations_dir = migration_dir

    def apply_migrations(self, version: str) -> None:
        """
        Applies new migrations.

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
        """
        if self._is_version_exists(version=version):
            eprint(
                f"Version {version} already exists. "
                f"Please choose another one."
            )
            exit(1)
        if bigger_versions := self._is_version_bigger_exists(version=version):
            eprint(
                f"There are bigger versions - {', '.join(bigger_versions)}"
                f"Please choose another version."
            )
            exit(1)

        if not (to_apply_migrations := self._get_to_apply_migrations()):
            eprint("There are no new migrations to apply.")
            exit(1)

        # TODO: add applying animation

        for migration in to_apply_migrations:
            print(f"Applying migration {migration} ...")
            self._apply_migration(migration, version)
            sprint(f"Applying migration {migration} ... Done!")

    def rollback_migrations(self, version: Optional[str] = None, latest: bool = False):
        """"""
        if version:
            self._rollback_migration_by_version(version)
        if latest:
            self._rollback_latest_migrations()

    def _rollback_latest_migrations(self):
        """"""
        latest_migrations = self._get_last_applied_migrations()

        for migration in latest_migrations:
            print(f"Rolling back migration {migration} ...")
            self._rollback_migration(migration)
            sprint(f"Rolling back migration {migration} ... Done!")

    def _rollback_migration_by_version(self, version: str):
        """"""
        if bigger_versions := self._is_version_bigger_exists(version=version):
            eprint(
                f"There are bigger versions - {', '.join(bigger_versions)} "
                f"Please rollback them first."
            )
            exit(1)
        if not self._is_version_exists(version=version):
            eprint(
                f"Can't find version - {version} in migrations. "
                f"Please choose another one."
            )
            exit(1)

    def initialize_database(self) -> None:
        """Initialize new table for migration control."""
        query = """
        CREATE TABLE pilgrimor (
            id SERIAL,
            name VARCHAR(100) NOT NULL,
            version VARCHAR(25) NOT NULL
        )
        """
        self.engine.execute_sql_no_return(
            sql_query=query,
            sql_query_params=(),
        )

        sprint("Database initialized!")

    def _apply_migration(self, migration: str, version: str) -> bool:
        """"""
        query = Path(
            join(self.migrations_dir, migration),
        ).read_text()
        try:
            apply_query = query.split("-- rollback --")[0]
        except KeyError:
            wprint(
                f"You don't split apply and rollback context in migration "
                f"{migration}. All commands will be applied.",
            )
            apply_query = query

        to_execute_query = self._add_migration_to_system_table(
            apply_query,
            migration,
            version,
        )

        self.engine.execute_sql_no_return(
            sql_query=to_execute_query,
            sql_query_params=(),
        )

    def _rollback_migration(self, migration: str) -> Optional[bool]:
        """"""
        query = Path(
            join(self.migrations_dir, migration),
        ).read_text()
        try:
            rollback_query = query.split("-- rollback --")[1]
        except KeyError:
            wprint(
                f"You don't split apply and rollback context in migration {migration}."
                f"Can't rollback this migration.",
            )
            return None

        to_execute_query = self._drop_migration_from_system_table(
            rollback_query,
            migration,
        )

        self.engine.execute_sql_no_return(
            sql_query=to_execute_query,
            sql_query_params=(),
        )

    def _get_to_apply_migrations(self) -> Set[str]:
        """"""
        applied_migrations = self._get_applied_migrations()
        all_migrations = self._get_migration_files()

        if not applied_migrations:
            return all_migrations

        new_migrations = set(all_migrations) - set(applied_migrations)

        return self._sort_migrations(new_migrations)

    def _get_migration_files(self) -> List[str]:
        """
        Returns all migration files.

        :returns: list with migratons.
        """
        return [
            sql_file
            for sql_file
            in listdir(self.migrations_dir)
            if isfile(
                join(self.migrations_dir, sql_file),
            )
        ]

    def _get_applied_migrations(self) -> List[str]:
        """
        Returns all applied migrations from database.

        :returns: list with migrations.
        """
        query = """
        SELECT name
        FROM pilgrimor
        """

        migrations = self.engine.execute_sql_with_return(
            sql_query=query,
            sql_query_params=(),
        )

        return migrations

    def _get_last_applied_migrations(self) -> str:
        """"""
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
            sql_query_params=(),
        )

        return self._sort_migrations(migrations, desc=True)

    def _get_migrations_by_version(self) -> List[str]:
        """
        Returns all migrations by version.

        :returns: list with migratons.
        """

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
        result: List[bool] = self.engine.execute_sql_with_return(
            sql_query=query,
            sql_query_params=(version,),
        )
        return result[0]

    def _is_version_bigger_exists(
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
        query = """
        SELECT version
        FROM pilgrimor
        GROUP BY version
        """
        versions = self.engine.execute_sql_with_return(
            sql_query=query,
            sql_query_params=(),
        )
        if versions:
            return [
                exist_version
                for exist_version
                in versions
                if version_parse(exist_version) > version_parse(version)
            ]

        return None


    def _check_migrations_name(self, migration: str):
        """"""

    def _sort_migrations(
        self,
        migrations: Set[str],
        desc: bool = False,
    ) -> Set[str]:
        """
        Sort migrations.

        :param migrations: List of migrations.
        :param desc: reverse or not.

        :returns: sorted list of migrations
        """
        def get_migration_number(file_name: str) -> int:
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

        return query + "\n" + system_command

    def _drop_migration_from_system_table(
        self,
        query: str,
        migration: str,
    ) -> str:
        """
        Drop migration from pilgrimor database.

        :param query: query from migration.
        :param migration: migration.
        :param version: version.

        :returns: query
        """
        system_command = f"""
        DELETE FROM pilgrimor
        WHERE name = '{migration}';
        """
        return query + "\n" + system_command
