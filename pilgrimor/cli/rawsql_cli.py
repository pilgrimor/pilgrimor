from argparse import ArgumentParser, Namespace

from pilgrimor.cli.base_cli import BaseCLI
from pilgrimor.migrator.rawsql_migrator.rawsql_migrator import RawSQLMigator
from pilgrimor.utils import eprint


class RawSQLMigratorCLI(BaseCLI):
    """CLI for RawSQLMigrator."""

    def __init__(
        self,
        namespace: Namespace,
        engine,
        migrations_dir: str,
    ):
        """
        Initialize the CLI.

        :param parser: console argument parser.
        """
        self.namespace: Namespace = namespace
        self.migrator: RawSQLMigator = RawSQLMigator(
            engine,
            migrations_dir,
        )

    def apply(self):
        version = getattr(self.namespace, "version")
        # try:
        self.migrator.apply_migrations(version)
        # except Exception as exc:
        #     eprint(str(exc))

    def rollback(self):
        version = getattr(self.namespace, "version")
        latest = getattr(self.namespace, "latest")

        if not version and not latest:
            eprint(
                "You must set a version or --latest flag",
            )
        if version and latest:
            eprint(
                "You must set only a version or --latest flag"
            )

        if version:
            try:
                self.migrator.rollback_migrations(
                    version=version,
                    latest=False,
                )
            except Exception as exc:
                eprint(str(exc))
        if latest:
            try:
                self.migrator.rollback_migrations(
                    version=None,
                    latest=True,
                )
            except Exception as exc:
                eprint(str(exc))

    def initdb(self):
        self.migrator.initialize_database()
