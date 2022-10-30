import logging
import sys
from typing import Dict

import tomlkit
from dotenv import dotenv_values
from pydantic import BaseSettings

from pilgrimor.utils import error_text

logger = logging.getLogger("pilgrimor.settings")


class PilgrimorSettings(BaseSettings):
    """BaseSettings for Pilgrimor."""

    migrations_dir: str = "./migrations"
    database_engine: str = "PSQL"
    database_url: str = "postgres://pilgrimor:pilgrimor@localhost:5432/pilgrimor"
    migrator_cli: str = "RAW"

    @classmethod
    def new(cls) -> "PilgrimorSettings":  # noqa: C901, WPS210
        """
        Create new instance of Settings.

        Parse .env and pyproject.toml file to get settings.

        :returns: PilgrimorSettings.
        """
        try:
            with open("pyproject.toml", "r") as pyproject_file:
                raw_poetry_settings = pyproject_file.read()
        except Exception:
            sys.exit("Can't find pyproject.toml.")

        pyproject_toml = tomlkit.parse(raw_poetry_settings)
        try:
            pilgrimor_settings: Dict[str, str] = pyproject_toml["tool"][  # type: ignore
                "pilgrimor"
            ]
        except KeyError:
            sys.exit(error_text("Can't find pyproject.toml."))

        config = dotenv_values(pilgrimor_settings.pop("env_file"))

        if not config:
            sys.exit(
                error_text(
                    "Can't find .env file. Please specify it in pyproject.toml.",
                ),
            )

        if not (db_url := config.get("PILGRIMOR_DATABASE_URL")):
            sys.exit(
                error_text(
                    "Can't get PILGRIMOR_DATABASE_URL from .env file.",
                ),
            )
        pilgrimor_settings["database_url"] = db_url

        return PilgrimorSettings(**pilgrimor_settings)
