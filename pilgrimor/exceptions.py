from typing import Any


class BasePilgrimorError(Exception):
    """Base error class for all Pilgrimor errors."""

    error_code = 0
    message = ""

    def __init__(self, *message_args: Any, **message_kwargs: Any) -> None:
        """Initialization.

        :param message_args: Positional parameters for error message.
        :param message_kwargs: Named parameters for error message.
        """
        self.message = "\n".join(  # noqa: WPS601
            [
                f"Exception error_code: {self.error_code}",
                self.message.format(*message_args, **message_kwargs),
            ],
        )
        super().__init__(self.message)


class ApplyMigrationsError(BasePilgrimorError):
    """Error for unsuccessful migrations apply."""

    error_code = 1
    message = "Can't apply migrations."


class IncorrectMigrationHistoryError(BasePilgrimorError):
    """Error if migrations have incorrect history."""


class WrongMigrationNumberError(ApplyMigrationsError):
    """Wrong migration number."""


class MigrationNumberRepeatNumberError(ApplyMigrationsError):
    """Error if there are two or more migrations with the same number."""


class VersionAlreadyExistsError(ApplyMigrationsError):
    """Error if version already exists."""


class BiggerVersionsExistsError(ApplyMigrationsError):
    """Error if bigger versions exist."""


class NoNewMigrationsError(ApplyMigrationsError):
    """Error if no new migrations."""


class RollBackMigrationsError(BasePilgrimorError):
    """Error for unsuccessful migrations rollback."""
