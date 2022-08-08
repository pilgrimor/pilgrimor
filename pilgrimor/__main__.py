from pilgrimor.cli.cli import get_cli
from pilgrimor.cli.parser import get_parser
from pilgrimor.engine.engine import get_engine


if __name__ == "__main__":
    engine = get_engine()
    parser = get_parser()
    cli = get_cli(parser)

    cli()
