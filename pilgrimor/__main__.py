from pilgrimor.cli.parser import get_parser
from pilgrimor.cli.rawsql_cli import RawSQLMigratorCLI
from pilgrimor.engine.engine import get_engine
from settings import settings


if __name__ == "__main__":
    engine = get_engine()(settings.database_url)
    parser = get_parser()
    cli = RawSQLMigratorCLI(parser, engine, settings.migrations_dir)
    cli()
