from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union


class Engine(ABC):
    """
    Abstract class for engines.

    The engine works with the database.

    It performs or rolls back migrations
    and returns the necessary information
    for the migrator.
    """

    @abstractmethod
    def execute_sql(
        self,
        sql_query: str,
        sql_query_params: Tuple[Any],
    ) -> Optional[List[str]]:
        """
        Executes sql query.


        The engine works with the database.

        It performs or rolls back migrations
        and returns the necessary information
        for the migrator.

        :param sql_query: sql query to execute.
        :param sql_query_params: parameters for sql query.

        :returns: None or list with results.
        """
