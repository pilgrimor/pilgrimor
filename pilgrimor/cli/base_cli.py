from argparse import ArgumentParser, Namespace

from pilgrimor.utils import eprint, aprint


class BaseCLI:
    """
    Base class for CLI commands.

    In this class, we must have all
    the commands from the parser as methods.
    """

    def __init__(self, parser: ArgumentParser) -> None:
        """
        Initialize the CLI.

        :param parser: console argument parser.
        :param migrator: migrator instance
        """
        self.namespace: Namespace = parser.parse_args()

    def __call__(self):
        """
        Makes class callable.

        Try to find command in class method,
        if found - call it, else exit from the programm.
        """
        if self.namespace.command:
            available_commands = [
                command_name
                for command_name
                in self.__dir__()
                if not command_name.startswith("__")
                and not command_name.startswith("_")
            ]
            if self.namespace.command not in available_commands:
                eprint(f"Can't find {self.namespace.command}.")
                exit(1)

            getattr(self, self.namespace.command)()
        else:
            aprint("You don't call any command")
            exit(1)
