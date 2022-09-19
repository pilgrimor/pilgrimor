from pilgrimor.cli.parser import get_parse_args
from pilgrimor.cli.rawsql_cli import RawSQLMigratorCLI
from pilgrimor.engine.engine import get_engine
from pilgrimor.settings import PilgrimorSettings


def main():
    namespace = get_parse_args()
    settings = PilgrimorSettings.new()
    engine = get_engine(
        settings,
    )(settings.database_url)
    cli = RawSQLMigratorCLI(
        namespace,
        engine,
        settings.migrations_dir,
    )
    cli()


if __name__ == "__main__":
    main()
