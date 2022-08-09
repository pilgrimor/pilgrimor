
from importlib.metadata import entry_points
from pilgrimor.settings import PilgrimorSettings

available_engines = (
    "PostgreSQLEngine",
    "MySQLEngine",
)


def get_engine(settings: PilgrimorSettings):
    """
    Returns the engine.

    Check if the specified engine exists in pyproject.toml.
    Next, check if there is an installed engine.
    And in the end, we check whether the correct engine is installed.
    """
    if settings.database_engine not in available_engines:
        print(
            """
            You set %s database engine, but it does not support.
            Choose another engine, please.
            """ % settings.database_engine,
        )
        exit(1)

    engine = entry_points().get("pilgrimor_engine")

    if not engine:
        print(
            """
            You set %s database engine, but do not install it.
            Please install it.
            """,
        )
        exit(1)

    if len(engine) > 1:
        print(
            "You install many migrators. Please install required one."
        )
        exit(1)

    try:
        engine = engine[0].load()
    except IndexError:
        print("Can't load any engine.")
        exit(1)

    if engine.__name__ != settings.database_engine:
        print(
            """
            You set %s database engine, but install another one or many.
            Please install required engine.
            """,
        )
        exit(1)

    return engine
