from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class PilgrimoreEngine(ABC):
    """
    Base class for any engine for pilgrimor.

    Engine to execute sql quries.

    The engine works with the database.

    It performs sql queries, return data if needed
    and returns the necessary information
    for the migrator.

    By default, the request is executed in a transaction
    (in psycopg this is autocommit=False)
    but this behavior can be changed by
    adding autocommit=True.

    However, there is a nuance in this method,
    only one command will be executed not in a transaction,
    if there are several of them,
    then the rest will be in a transaction.
    """

    def __init__(self, database_url: str) -> None:
        """
        Initialize the engine.

        :param database_url: url to database.
        """
        self.database_url = database_url

    @abstractmethod
    def execute_sql_with_return(
        self,
        sql_query: str,
        sql_query_params: Optional[List[Any]] = None,
        in_transaction: Optional[bool] = True,
    ) -> Optional[List[Any]]:
        """
        Executes sql query and return output.

        By default query must be executed in transaction.

        :param sql_query: sql query to execute.
        :param sql_query_params: parameters for sql query.
        :param in_transaction: execute in transaction or not.

        :return: list with results.
        """

    @abstractmethod
    def execute_sql_with_no_return(
        self,
        sql_query: str,
        sql_query_params: Optional[List[Any]] = None,
        in_transaction: Optional[bool] = True,
    ) -> None:
        """
        Executes sql query.

        By default query must be executed in transaction.

        :param sql_query: sql query to execute.
        :param sql_query_params: parameters for sql query.
        :param in_transaction: execute in transaction or not.
        """

    @abstractmethod
    def execute_version_migrations(
        self,
        version_migrations: List[Dict[str, str]],
        sql_query_params: Optional[List[Any]] = None,
        in_transaction: bool = True,
    ) -> None:
        """
        Executes all migrations sql queries and do not return any output.

        By default query must be executed in transaction.

        :param version_migrations: list of dicts with migration data for single version.
        :param sql_query_params: parameters for sql query.
        :param in_transaction: execute in transaction or not.
        """
