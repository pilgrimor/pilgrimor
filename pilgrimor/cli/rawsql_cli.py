from argparse import ArgumentParser, Namespace

from pilgrimor.cli.base_cli import BaseCLI
from pilgrimor.migrator.rawsql_migrator.rawsql_migrator import RawSQLMigator
from pilgrimor.utils import eprint


class RawSQLMigratorCLI(BaseCLI):
    """CLI for RawSQLMigrator."""

    def __init__(
        self,
        parser: ArgumentParser,
        engine,
        migrations_dir: str,
    ):
        """
        Initialize the CLI.

        :param parser: console argument parser.
        """
        self.namespace: Namespace = parser.parse_args()
        self.migrator: RawSQLMigator = RawSQLMigator(
            engine,
            migrations_dir,
        )

    def apply(self):
        if not (version := getattr(self.namespace, "version")):
            print("WOW!")
            exit(1)
        self.migrator.apply_migrations(version)

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
            self.migrator.rollback_migrations(
                version=version,
                latest=False,
            )
        if latest:
            self.migrator.rollback_migrations(
                version=None,
                latest=True,
            )

    def initdb(self):
        print("We are in initdb")
        self.migrator.initialize_database()
