from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from importlib.metadata import entry_points
from pilgrimor.settings import settings


def get_default_parser():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    commands = parser.add_subparsers(
        title="commands",
        dest="command",
    )

    commands.add_parser(
        "initdb",
        help=(
            "Initialize you database."
        ),
    )

    migrate_parser = commands.add_parser(
        "apply",
        help=(
            "Apply new migrations."
        ),
    )
    migrate_parser.add_argument(
        "--version",
        "-v",
        help="Set release version for migration(s).",
    )

    downgrade_command = commands.add_parser(
        "rollback",
        help=(
            "Rollback migrations."
        ),
    )
    downgrade_command.add_argument(
        "--version",
        "-fv",
        help="Set release version for migration(s).",
    )
    downgrade_command.add_argument(
        "--latest",
        action='store_true',
        help=(
            "Downgrade last applied version."
        )
    )

    return parser


def get_parser():
    parser: ArgumentParser = get_default_parser()

    if settings.migrator_cli == "RawSQLCLI":
        return parser

    new_parser = entry_points(group="pilgrimor-parser")

    if not new_parser:
        print(
            """
            You set %s migrator, but do not install it.
            Please install it.
            """
        )
        exit(1)

    if len(new_parser) > 1:
        print(
            "You install many migrators. Please install required one."
        )
        exit(1)

    try:
        new_parser = new_parser[0].load()
    except IndexError:
        print("Can't load any parser.")
        exit(1)

    if new_parser.name != settings.migrator_cli:
        print(
            """
            You set %s migrator, but install another one.
            Please install required engine.
            """,
        )
        exit(1)

    parser._actions[1].choices.update(
        new_parser._actions[1].choices
    )

    return parser
