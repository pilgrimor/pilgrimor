from pydantic import BaseSettings

import tomlkit
from dotenv import dotenv_values
import logging

from pilgrimor.utils import eprint

logger = logging.getLogger("pilgrimor.settings")


class PilgrimorSettings(BaseSettings):
    """BaseSettings for Pilgrimor."""

    migrations_dir: str = "./migrations"
    database_engine: str = "PostgreSQLEngine"
    database_url: str = "postgres://pilgrimor:pilgrimor@localhost:5432/pilgrimor"
    migrator_cli: str = "RawSQLCLI"

    @classmethod
    def new(cls):
        """
        Create new instance of Settings.

        Parse .env and pyproject.toml file to get settings.

        :returns: PilgrimorSettings.
        """
        try:
            with open("pyproject.toml", "r") as pyproject_file:
                raw_poetry_settings = pyproject_file.read()
        except Exception:
            eprint("Can't find pyproject.toml.")
            exit(1)

        try:
            pilgrimor_settings = tomlkit.parse(
                raw_poetry_settings,
            )["tool"]["pilgrimor"]
        except KeyError:
            eprint("Can't find pilgrimor tool settings in pyproject.toml")
            exit(1)

        config = dotenv_values(pilgrimor_settings.pop("env_file"))

        if not config:
            eprint("Can't find .env file. Please specify it in pyproject.toml.")
            exit(1)

        try:
            pilgrimor_settings["database_url"] = config["PILGRIMOR_DB_URL"]
        except KeyError:
            eprint("Can't get PILGRIMOR_DATABASE_URL from .env file.")

        return PilgrimorSettings(**pilgrimor_settings)
