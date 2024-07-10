from abc import ABC, abstractmethod
import oracledb
from sqlalchemy import create_engine
import pandas as pd
import logging
import typing

logger = logging.getLogger(__name__)


class HierarchyDB(ABC):
    @abstractmethod
    def read_data(self, *, schema=None, table=None, parent=None, child=None):
        pass

    @abstractmethod
    def write_data(self, df, *, schema=None, table=None):
        pass


class HierarchyDBOracle(HierarchyDB):
    """
    Class for interacting with an Oracle database to read and write hierarchy data.

    :ivar user: The database username.
    :ivar password: The database password.
    :ivar dsn: The Data Source Name identifying the Oracle database.
    :ivar engine: SQLAlchemy engine object. Defaults to None.
    """
    def __init__(self, *, user=None, password=None, dsn=None, **kwargs):
        """
        Initialize the HierarchyDBOracle with database connection parameters.

        :param user: The username for the database connection.
        :param password: The password for the database connection.
        :param dsn: The Data Source Name for the database connection.
        :param kwargs: Additional keyword arguments.
        :raises ValueError: If any of 'user', 'password', or 'dsn' are not provided.
        """
        if not all((user, password, dsn)):
            raise ValueError("All parameters 'user', 'password', and 'dsn' must be provided.")
        self.user = user
        self.password = password
        self.dsn = dsn
        self.engine = self._create_engine()

    def _create_engine(self):
        """
        Create a SQLAlchemy engine for connecting to the Oracle database.
        This method constructs the connection string and creates an SQLAlchemy
        engine using the provided user, password, and dsn.

        :return: A SQLAlchemy engine instance for the Oracle database.
        """
        cp = oracledb.ConnectParams()
        cp.parse_connect_string(self.dsn)
        thick_mode = None

        return create_engine(f'oracle+oracledb://{self.user}:{self.password}@{cp.host}:{cp.port}/?service_name={cp.service_name}', thick_mode=thick_mode)

    def read_data(self, *, schema=None, table=None, parent=None, child=None, where='', **kwargs):
        """
        Reads hierarchy data from the specified database table.


        :param schema: The database schema.
        :param table: The database table name.
        :param parent: The parent column name.
        :param child: The child column name.
        :param where: Where clause optionally.
        :return: DataFrame containing the hierarchy data or None if an error occurs.
        :raises ValueError: If any of the required parameters ('schema', 'table', 'parent', 'child') are not provided.
        :raises Exception: If there is an issue reading from the database.
        """
        if not all((schema, table, parent, child)):
            raise ValueError("All parameters 'schema', 'table', 'parent', and 'child' must be provided.")

        source_query = f"SELECT {parent}, {child} FROM {schema}.{table} {('WHERE ' + where) if where != '' else ''}"

        if self.engine is None:
            self._create_engine()

        try:
            return pd.read_sql(source_query, con=self.engine)
        except Exception as e:
            logger.error(f"Failed to read data: {e}")
            return None

    def write_data(self, df: pd.DataFrame, *, schema=None, table=None, **kwargs):
        """
        Writes hierarchy data to the specified database table.

        :param df: DataFrame containing the hierarchy data to write.
        :param schema: The database schema.
        :param table: The database table name.
        :raises ValueError: If either 'schema' or 'table' is not provided.
        :raises Exception: If there is an issue writing to the database.
        """
        if not all((schema, table)):
            raise ValueError("All parameters 'schema' and 'table' must be provided.")

        try:
            df.to_sql(table, self.engine, schema=schema, if_exists=typing.cast(typing.Literal["append", "fail", "replace"], kwargs.get("if_exists", "fail")), index=False)
        except Exception as e:
            logger.error(f"Failed to write data to database: {e}")
            raise

    def dispose(self):
        """
        Dispose of the SQLAlchemy engine.
        This method disposes of the SQLAlchemy engine to free up database connections and resources.
        """
        self.engine.dispose()
