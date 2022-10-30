from argparse import Namespace

from pilgrimor.abc.engine import PilgrimoreEngine
from pilgrimor.cli.base_cli import BaseCLI
from pilgrimor.migrator.rawsql_migrator.rawsql_migrator import RawSQLMigator
from pilgrimor.utils import error_text


class RawSQLMigratorCLI(BaseCLI):
    """CLI for RawSQLMigrator."""

    def __init__(
        self,
        namespace: Namespace,
        engine: PilgrimoreEngine,
        migrations_dir: str,
    ) -> None:
        """
        Initialize the CLI.

        :param namespace: namespace with args from the command line.
        :param engine: sql engine.
        :param migrations_dir: directory with migrations.
        """
        self.namespace: Namespace = namespace
        self.migrator: RawSQLMigator = RawSQLMigator(
            engine,
            migrations_dir,
        )

    def apply(self) -> None:
        """
        Apply command.

        Runs apply_migarations method in the migrator.
        """
        version = self.namespace.version
        try:
            self.migrator.apply_migrations(version)
        except Exception as exc:
            exit(error_text(str(exc)))

    def rollback(self) -> None:  # noqa: C901
        """
        Rollback command.

        Runs rollback_migrations method in the migrator.
        """
        version = self.namespace.version
        latest = self.namespace.latest

        if not version and not latest:
            print(
                error_text(
                    "You must set a version or --latest flag",
                ),
            )

        if version and latest:
            exit(
                error_text(
                    "You must set only a version or --latest flag",
                ),
            )

        if version:
            try:
                self.migrator.rollback_migrations(
                    version=version,
                    latest=False,
                )
            except Exception as exc:
                exit(
                    error_text(
                        str(exc),
                    ),
                )
        if latest:
            try:
                self.migrator.rollback_migrations(
                    version=None,
                    latest=True,
                )
            except Exception as exc:  # noqa: WPS440
                exit(
                    error_text(
                        str(exc),
                    ),
                )

    def initdb(self) -> None:
        """
        Initdb command.

        Runs initialize_database method in the migrator.
        """
        self.migrator.initialize_database()
