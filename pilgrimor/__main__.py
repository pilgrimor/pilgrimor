from pilgrimor.cli.parser import get_parser
from pilgrimor.cli.rawsql_cli import RawSQLMigratorCLI
from pilgrimor.engine.engine import get_engine
from pilgrimor.settings import PilgrimorSettings


def main():
    settings = PilgrimorSettings.new()
    engine = get_engine(
        settings,
    )(settings.database_url)
    parser = get_parser(settings)
    cli = RawSQLMigratorCLI(
        parser,
        engine,
        settings.migrations_dir,
    )
    cli()


if __name__ == "__main__":
    main()
