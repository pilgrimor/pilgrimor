from argparse import Namespace

from pilgrimor.utils import attention_text, error_text


class BaseCLI:
    """
    Base class for CLI commands.

    In this class, we must have all
    the commands from the parser as methods.
    """

    def __init__(self, namespace: Namespace) -> None:
        """
        Initialize the CLI.

        :param namespace: namespace with arguments.
        """
        self.namespace: Namespace = namespace

    def __call__(self) -> None:
        """
        Makes class callable.

        Try to find command in class method,
        if found - call it, else exit from the programm.
        """
        if self.namespace.command:
            available_commands = [
                command_name
                for command_name in self.__dir__()
                if not command_name.startswith("__")
                and not command_name.startswith("_")
            ]
            if self.namespace.command not in available_commands:
                exit(
                    error_text(
                        f"Can't find {self.namespace.command}.",
                    ),
                )

            getattr(self, self.namespace.command)()
        else:
            exit(
                attention_text(
                    "You don't call any command",
                ),
            )
