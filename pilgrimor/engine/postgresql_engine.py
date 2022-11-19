import sys
from typing import Any, Dict, List, Optional

from psycopg.rows import Row

from pilgrimor.abc.engine import PilgrimoreEngine
from pilgrimor.utils import error_text

try:
    import psycopg  # noqa: WPS433
except ImportError:
    sys.exit(error_text("You must install psycopg, psycopg-c and psycopg-binary."))


class PostgreSQLEngine(PilgrimoreEngine):
    """
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
        Creates connection pool.

        :param database_url: url to database.
        """
        self.database_url = database_url

    def execute_sql_with_return(
        self,
        sql_query: str,
        sql_query_params: Optional[List[Any]] = None,
        in_transaction: Optional[bool] = True,
    ) -> Optional[List[Any]]:
        """
        Executes sql query and return output.

        By default query

        :param sql_query: sql query to execute.
        :param sql_query_params: parameters for sql query.
        :param in_transaction: execute in transaction or not.

        :return: None or list with results.
        """
        autocommit = False
        if not in_transaction:
            autocommit = True

        with psycopg.connect(self.database_url, autocommit=autocommit) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query=sql_query,
                    params=sql_query_params,
                )
                result = cursor.fetchall()

        return self._form_result(result=result)

    def execute_sql_with_no_return(
        self,
        sql_query: str,
        sql_query_params: Optional[List[Any]] = None,
        in_transaction: Optional[bool] = True,
    ) -> None:
        """
        Executes sql query and return output.

        By default query

        :param sql_query: sql query to execute.
        :param sql_query_params: parameters for sql query.
        :param in_transaction: execute in transaction or not.
        """
        autocommit = False
        if not in_transaction:
            autocommit = True

        with psycopg.connect(self.database_url, autocommit=autocommit) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query=sql_query,
                    params=sql_query_params,
                )

    def execute_version_migrations(
        self,
        version_migrations: List[Dict[str, str]],
        sql_query_params: Optional[List[Any]] = None,
        in_transaction: bool = True,
    ) -> None:
        """
        Executes all migrations sql queries and do not return any output.

        :param version_migrations: sql queries dict by migrations.
        :param sql_query_params: parameters for sql query.
        :param in_transaction: execute in transaction or not.
        """
        autocommit = False
        if not in_transaction:
            autocommit = True
        connection = psycopg.connect(self.database_url, autocommit=autocommit)
        cursor = connection.cursor()
        if in_transaction:
            with connection.transaction():
                for tr_migration in version_migrations:
                    self._execute_migration_operations(
                        cursor,
                        tr_migration,
                        sql_query_params,
                        in_transaction,
                    )
                    print(f"migration: {tr_migration['migration']} - OK")
            connection.close()
        else:
            for migration in version_migrations:
                self._execute_migration_operations(
                    cursor,
                    migration,
                    sql_query_params,
                    in_transaction,
                )
                print(f"migration: {migration['migration']} - OK")
            cursor.close()
            connection.close()

    def _execute_migration_operations(
        self,
        cursor: psycopg.Cursor[Row],
        migration: Dict[str, str],
        sql_query_params: Optional[List[Any]] = None,
        in_transaction: bool = True,
    ) -> None:
        """
        Executes all operation sql queries in one migration.

        :param cursor: psycopg driver cursir
        :param migration: migrations sql queries dict.
        :param sql_query_params: parameters for sql query.
        :param in_transaction: execute in transaction or not.

        :raises Exception: error in migration query.
        """
        migration_queries = migration["query"].split(";")
        for query in migration_queries:
            try:
                cursor.execute(
                    query=query,
                    params=sql_query_params,
                )
            except (Exception, psycopg.DatabaseError) as error:
                print(f"{migration['migration']}, it not be applied", error)
                if not in_transaction:
                    continue
                print("All version migrations will be rollback")
                raise error

    def _form_result(self, result: Any) -> Optional[List[Any]]:
        """
        Create list with record from query result.

        :param result: result from query.

        :returns: :return: None or list with results.
        """
        result_length = len(result)

        if result_length == 1:
            return list(result[0])
        elif result_length == 0:
            return None

        to_return_result = []
        for record in result:
            if len(record) == 1:
                to_return_result.append(record[0])
            elif len(record) > 1:
                to_return_result.append(record)
        return to_return_result
