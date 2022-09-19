from importlib.metadata import entry_points
import sys
from pilgrimor.settings import PilgrimorSettings
from pilgrimor.engine.postgresql_engine import PostgreSQLEngine

engines_map = {
    "PSQL": PostgreSQLEngine,
}


def get_engine(settings: PilgrimorSettings):
    """
    Returns the engine.

    Check if the specified engine exists in pyproject.toml.
    Next, check if there is an installed engine.
    And in the end, we check whether the correct engine is installed.
    """
    if engine := engines_map.get(settings.database_engine):
        return engine

    engine = entry_points().get("pilgrimor_engine")

    if not engine:
        sys.exit("You set %s database engine, but do not install it.")

    if len(engine) > 1:
        sys.exit("You install many migrators. Please install required one.")

    try:
        engine = engine[0].load()
    except IndexError:
        sys.exit("Can't load any external engine.")

    if engine.__name__ != settings.database_engine:
        sys.exit(
            f"You set {engine.__name__} database engine, "
            f"but install another one or many",
        )

    return engine
