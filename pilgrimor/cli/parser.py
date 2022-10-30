from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace


def get_parse_args() -> Namespace:
    """
    Parses input terminal args.

    :returns: Namespace.
    """
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    commands = parser.add_subparsers(
        title="commands",
        dest="command",
    )

    commands.add_parser(
        "initdb",
        help=("Initialize you database."),
    )

    migrate_parser = commands.add_parser(
        "apply",
        help=("Apply new migrations."),
    )
    migrate_parser.add_argument(
        "--version",
        "-v",
        help="Set release version for migration(s).",
    )

    downgrade_command = commands.add_parser(
        "rollback",
        help=("Rollback migrations."),
    )
    downgrade_command.add_argument(
        "--version",
        "-fv",
        help="Set release version for migration(s).",
    )
    downgrade_command.add_argument(
        "--latest",
        action="store_true",
        help=("Downgrade last applied version."),
    )

    return parser.parse_args()
