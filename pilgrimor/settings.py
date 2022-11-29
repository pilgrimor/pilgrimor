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

    class Config:
        env_file = ".env"
        env_prefix = "PILGRIMOR_"
        env_file_encoding = "utf-8"

    def add_new_fields(self) -> "PilgrimorSettings":  # noqa: C901, WPS210
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

        try:
            self.database_engine = pilgrimor_settings["database_engine"]
            self.migrations_dir = pilgrimor_settings["migrations_dir"]
        except KeyError as exc:
            sys.exit(error_text(f"Error in getting settings - {str(exc)}"))

        return self
