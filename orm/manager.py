"""
This module defines classes related to database schema management and querying.

Attributes:
    ``__all__`` (list): List of classes available in this module.
    ``QueryBuilder``: Class for building queries to fetch data from the database.
    ``QueryManager``: Class containing functions to execute queries.
    ``Model``: Base class for building tables in the database.

Classes:
    ``QueryBuilder``: Class for building queries to fetch data from the database.
    ``QueryManager``: Class containing functions to execute queries.
    ``Model``: Base class for building tables in the database.

Functions:
    No functions in this module.
"""


__all__ = [
    "QueryBuilder",
    "QueryManager",
    "Model",
]


class QueryBuilder:
    """
    Class for building queries to fetch data from the database.
    """

    pass


class QueryManager:
    """
    Class containing functions to execute queries.
    """

    pass


class Model:
    """
    Base class for building tables in the database.

    Attributes:
        ``_table_name`` (str): Name of the table in the database.

    Methods:
        ``__init__(**kwargs)``: Initializes a Model instance with field values.
        ``create_table_sql()``: Generates SQL query for creating the table in the database.
    """

    _table_name = None

    def __init__(self, **kwargs):
        """
        Initializes a Model instance with field values.

        Parameters:
            ``**kwargs``: Keyword arguments representing field names and values.
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
            print(k, v)

    @classmethod
    def create_table_sql(cls):
        """
        Generates SQL query for creating the table in the database.

        Returns:
            ``str``: SQL query for creating the table.
        """
        fields_sql = []
        for field_name, field_obj in cls.__dict__.items():
            if isinstance(field_obj, Field):
                fields_sql.append(f"{field_name.lower()} {field_obj.to_sql()}")
        table_name = cls._table_name or cls.__name__.lower()
        query = f"CREATE TABLE {table_name} ({', '.join(fields_sql)})"
        return query
