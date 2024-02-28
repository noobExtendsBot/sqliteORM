"""
This module handles schema management and database connections.
It is not intended for handling queries.
"""

from abc import ABC, abstractmethod

__all__ = [
    "DataBaseConnector",
    "MigrationManager",
]

try:
    import sqlite3
except Exception as e:
    raise ImportError("Try installing sqlite3")


class SingletonDBManagerMeta(type):
    """
    Metaclass for implementing a singleton pattern for the DataBaseConnector class.
    """

    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            instance = super().__call__(*args, **kwargs)
            cls._instance = instance
        return cls._instance


class DataBaseConnector(metaclass=SingletonDBManagerMeta):
    """
    Singleton class for managing database connections.

    Parameters:
    - database_name (str): The name of the database.
    - host (str, optional): The host of the database. Defaults to None.
    - port (int, optional): The port of the database. Defaults to None.
    - username (str, optional): The username for connecting to the database. Defaults to None.
    - password (str, optional): The password for connecting to the database. Defaults to None.
    """

    _connection = None

    def __init__(
        self, database_name, host=None, port=None, username=None, password=None
    ):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._database_name = database_name

        self.connect()

    def connect(self):
        """
        Establish a connection to the database.

        Raises:
        - Exception: If the connection cannot be established.
        """
        if DataBaseConnector._connection is None:
            try:
                DataBaseConnector._connection = sqlite3.connect(self._database_name)
            except Exception as e:
                raise Exception(f"{e}")

    def close(self):
        """Close the database connection."""
        DataBaseConnector._connection.close()


class DatabaseSchemaEditor:
    """
    Class for handling database schema editing.

    Attributes:
    - sql_create_table (str): SQL template for creating a table.
    - sql_alter_table (str): SQL template for altering a table.
    - sql_delete_table (str): SQL template for deleting a table.
    - sql_create_column (str): SQL template for creating a column in a table.
    - sql_delete_column (str): SQL template for deleting a column from a table.
    - sql_rename_column (str): SQL template for renaming a column in a table.
    """

    sql_create_table = "CREATE TABLE {table_name} ({definition});"
    sql_alter_table = "ALTER TABLE {old_table_name} RENAME TO {new_table_name}"
    sql_delete_table = "DROP TABLE {table_name} CASACDE"

    sql_create_column = "ALTER TABLE {table_name} ADD {column_name} {definition}"
    sql_delete_column = "ALTER TABLE {table_name} DROP COLUMN {column_name}"
    sql_rename_column = (
        "ALTER TABLE {table_name} RENAME COLUMN {old_name} to {new_name}"
    )

    @classmethod
    def generate_table(cls, table_name, definition):
        """
        Generate SQL for creating a table.

        Parameters:
        - table_name (str): Name of the table.
        - definition (str): Definition of the table's columns.

        Returns:
        str: SQL for creating the table.
        """
        return cls.sql_create_table.format(table_name=table_name, definition=definition)


class SingletonMigrationManager(type):
    """
    Metaclass for implementing a singleton pattern for the MigrationManager class.
    """

    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            instance = super().__call__(*args, **kwargs)
            cls._instance = instance
        return cls._instance


class MigrationManager(metaclass=SingletonMigrationManager):
    """
    Singleton class for managing database migrations.

    Parameters:
    - models (list): List of model classes for which migrations will be managed.

    Attributes:
    - migration_history: Placeholder for storing migration history.
    """

    def __init__(self, models):
        """
        Initialize the MigrationManager.

        Parameters:
        - models (list): List of model classes for which migrations will be managed.

        Raises:
        ValueError: If models is not a list.
        """
        if not isinstance(models, list):
            raise ValueError("models should be a list of Models")
        self.migration_history = None
        self.models = models

    def create_migration(self):
        """
        Create database migration scripts for the specified models.

        Raises:
        ValueError: If a model is not an instance of the Model class.
        """
        for model in self.models:
            if not isinstance(model, Model):
                raise ValueError("Make sure you inherit Model when creating Models")
            pass

    def apply(self, connection):
        """
        Apply database migrations using the provided database connection.

        Parameters:
        - connection: Database connection to be used for applying migrations.
        """
        pass
