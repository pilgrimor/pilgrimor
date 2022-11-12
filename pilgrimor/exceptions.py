class BasePilgrimorError(Exception):
    """Base error class for all Pilgrimor errors."""


class ApplyMigrationsError(BasePilgrimorError):
    """Error for unsuccessful migrations apply."""


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
