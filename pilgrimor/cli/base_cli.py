import sys
from argparse import Namespace

import tomlkit

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
            if self.namespace.version:
                project_version = self._get_project_version()
                if self.namespace.version != project_version:
                    exit(
                        error_text(
                            f"Migration version: {self.namespace.version} "
                            f"does not match the project version "
                            f"in pyproject.toml: {project_version}.",
                        ),
                    )
            getattr(self, self.namespace.command)()
        else:
            exit(
                attention_text(
                    "You don't call any command",
                ),
            )

    def _get_project_version(self) -> str:
        """
        Get project version fron pyproject.toml file.

        :returns: string of project version.
        """
        try:
            with open("pyproject.toml", "r") as pyproject_file:
                raw_poetry_settings = pyproject_file.read()
        except Exception:
            sys.exit("Can't find pyproject.toml.")

        pyproject_toml = tomlkit.parse(raw_poetry_settings)
        try:
            project_version: str = pyproject_toml["tool"]["poetry"]["version"]
        except KeyError:
            sys.exit(error_text("Can't find project version in pyproject.toml."))
        return project_version
