from abc import ABC, abstractmethod
try:
    import sqlite3
except Exception as e:
    raise ImportError("Try installing sqlite3")


# Fields section
"""
Attributes:
    __all__ (list): List of field types available in this module.
    field_mapper (dict): Mapping of field types to their corresponding SQLite data types.
    relationship_mapper (dict): Mapping of relationship types to their corresponding SQLite constraints.

Classes:
    Field (ABC): Abstract base class for all field types.
    CharField: Represents a character field with variable length.
    TextField: Represents a text field for storing longer text.
    AutoField: Represents an auto-incrementing integer primary key field.
    IntegerField: Represents a field for storing integer values.
    DecimalField: Represents a field for storing decimal values.
    FloatField: Represents a field for storing floating-point values.
    DateTimeField: Represents a field for storing date and time values.
    BooleanField: Represents a field for storing boolean values.
    ImageField: Represents a field for storing image file paths.
    FileField: Represents a field for storing file paths.
    DatabaseSchemaEditor: Schema editor for migrations.
    MigrationManager: To handle all the operations related to Migrations.
    QueryBuilder: Not implemented yet
    QueryManager: Not implemented yet
    Model: Base class for Models to be defined by users
"""

from abc import ABC, abstractmethod

__all__ = [
    "CharField",
    "TextField",
    "AutoField",
    "IntegerField",
    "DecimalField",
    "FloatField",
    "DateTimeField",
    "BooleanField",
    "ImageField",
    "FileField",

    # Database
    "DataBaseConnector",
    "MigrationManager",

    # Query Manager
    "QueryBuilder",
    "QueryManager",
    "Model",
]

# Mapping of field types to corresponding SQLite data types
field_mapper = {
    "CharField": "VARCHAR",
    "TextField": "TEXT",
    "IntegerField": "INTEGER",
    "DecimalField": "DECIMAL",
    "FloatField": "NUMERIC",
    "DateTimeField": "TEXT",
    "BooleanField": "INTEGER",
    "ImageField": "TEXT",
    "FileField": "TEXT",
}

# Mapping of relationship types to corresponding SQLite constraints
relationship_mapper = {
    "PrimaryKey": "{field_type} NOT NULL PRIMARY KEY",
    "AutoField": "INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT",
    "OneToOneField": "{field_type} NOT NULL UNIQUE REFERENCES {reference_table} ({ref_field_name}) DEFERRABLE INITIALLY DEFERRED",
    "ForeignKey": "{field_type} NOT NULL UNIQUE REFERENCES {reference_table} ({ref_field_name}) DEFERRABLE INITIALLY DEFERRED",
}


class Field(ABC):
    """
    Abstract base class for all field types.

    Attributes:
        primary_key (bool): Indicates if the field is a primary key.
        unique (bool): Indicates if the field values must be unique.
        null (bool): Indicates if the field allows NULL values.

    Methods:
        get_sql(): Abstract method to get the SQLite data type for the field.
    """

    def __init__(self, primary_key=False, unique=False, null=False):
        """
        Initialize a Field instance.

        Parameters:
            primary_key (bool): Indicates if the field is a primary key.
            unique (bool): Indicates if the field values must be unique.
            null (bool): Indicates if the field allows NULL values.
        """
        self.primary_key = primary_key
        self.unique = unique
        self.null = null

    def check_null(self):
        return " NOT NULL" if not self.null else ""

    def check_primary_key(self):
        return " PRIMARY KEY" if self.primary_key else ""

    def check_unique(self):
        return " UNIQUE" if self.unique else ""

    def check_default(self):
        return f" DEFAULT '{self.default}'" if self.default else ""

    def remaning_definition(self):
        """
        Generate constrainsts like UNIQUE, NOT NULL etc
        NOTE: they need to be generated in specific format
        so serialize them
        """
        method_order = [
            "check_null",
            "check_primary_key",
            "check_unique",
            "check_default",
        ]
        remaning_constrint = str()
        check_methods = [method for method in dir(self) if method.startswith("check_")]
        check_methods.sort(key=lambda x: method_order.index(x))

        for method_name in check_methods:
            method = getattr(self, method_name)
            remaning_constrint += method()
        return remaning_constrint

    @abstractmethod
    def to_sql(self):
        """
        Abstract method to get the SQLite data type for the field.
        """
        pass


class CharField(Field):
    """
    Represents a character field with variable length.

    Attributes:
        max_length (int): Maximum length of the character field.
        default: Default value for the field.
        NOTE: If you use CharField as PK then you can't set null=True or provide any default values
        eg: name = CharField(max_length=20, primary_key=True, null=True, default="myName") is not allowed
        Another thing to note is unique is automatically True in PK so don't mention it explicitly.
    """

    def __init__(
        self,
        max_length=None,
        primary_key=False,
        unique=False,
        null=False,
        default=None,
    ):
        """
        Initialize a CharField instance.

        Parameters:
            max_length (int): Maximum length of the character field.
            primary_key (bool): Indicates if the field is a primary key.
            unique (bool): Indicates if the field values must be unique.
            null (bool): Indicates if the field allows NULL values.
            default: Default value for the field.
        """
        super().__init__(primary_key, unique, null)
        self.max_length = max_length
        self.default = default
        self._basic_checks()
        if self.primary_key:
            self._primary_key_checks()
        elif self.unique:
            # enforce null as True bc some DB skip that
            self._unique_constraint_checks()
        elif (not self.null):
            self._check_for_default_val()

    def _basic_checks(self):
        methods_to_check = [
            "_check_max_length_and_type",
            "_check_max_length_limit",
        ]
        check_methods = [method for method in methods_to_check if method in dir(self)]
        for method_name in check_methods:
            method = getattr(self, method_name)
            method()

    def _primary_key_checks(self):
        """
        Check if primary key configuration is viable.
        """
        if self.primary_key and (
            self.null or (self.default is not None) or self.unique
        ):
            raise ValueError(
                "When using primary_key=True, do not set anything other than max_length"
            )

    def _unique_constraint_checks(self):
        # enforce null = True as DBs accept NULL in unique fields
        print("asdas")
        if self.unique and (self.default):
            raise ValueError(
                "If using CharField as unique you can't give a default value"
            )
        self.null = True

    def _check_for_default_val(self):
        """
        Check if default value is required.
        """
        print(self.__str__())
        if  (not self.null) and (not self.default):
            raise ValueError(
                "If null is False and primary_key=False, then it needs a default value"
            )

    def _check_max_length_and_type(self):
        """
        Check if max_length is valid.
        """
        if (
            (not isinstance(self.max_length, int))
            or (self.max_length is None)
            or (self.max_length <= 1)
        ):
            raise ValueError(
                "max_length can't be None or less than 2 characters and it should be an integer!"
            )

    def _check_max_length_limit(self):
        """
        Check if max_length is within the limit.
        """
        # print(self.max_length)
        if self.max_length > 255:
            raise ValueError(
                "CharField can not be longer than 255 characters. Use TextField!"
            )

    def to_sql(self):
        """
        Get the SQLite data type for the CharField.

        Returns:
            str: SQLite data type.
        """
        sql = str()
        if self.primary_key:
            sql = relationship_mapper["PrimaryKey"]
            field_type = field_mapper[self.__class__.__name__]
            sql = sql.format(field_type=f"{field_type}({self.max_length})")
        else:
            sql = f"{field_mapper[self.__class__.__name__]}({self.max_length})"
            remaning_definition = self.remaning_definition()
            print(remaning_definition)
            sql = "".join([sql, remaning_definition])
        # print(sql)
        return sql

    def __str__(self):
        """
        Get a string representation of the CharField.

        Returns:
            str: String representation.
        """
        return (
            f"CharField(max_length={self.max_length}, primary_key={self.primary_key}, "
            f"unique={self.unique}, null={self.null}, default={self.default})"
        )


class TextField(Field):
    """
    Represents a text field for storing longer text.

    Attributes:
        default: Default value for the field.
    """

    def __init__(self, primary_key=False, unique=False, null=True, default=None):
        """
        Initialize a TextField instance.

        Parameters:
            primary_key (bool): Indicates if the field is a primary key.
            unique (bool): Indicates if the field values must be unique.
            null (bool): Indicates if the field allows NULL values.
            default: Default value for the field.

        Raises:
            ValueError: If primary_key is set to True or unique is set to True.
        """
        super().__init__(primary_key, unique, null)
        if primary_key is True:
            raise ValueError("TEXT fields cannot be set as Primary Key")
        if unique is True:
            raise ValueError("TEXT fields cannot be set as UNIQUE")

        self.default = default

    def to_sql(self):
        """
        Get the SQLite data type for the TextField.

        Returns:
            str: SQLite data type.
        """
        sql = "TEXT"
        sql += f" NOT NULL" if not self.null else ""
        sql += f" DEFAULT '{self.default}'" if not self.default else ""
        return sql

    def __str__(self):
        """
        Get a string representation of the TextField.

        Returns:
            str: String representation.
        """
        return (
            f"TextField(primary_key={self.primary_key}, unique={self.unique}, "
            f"null={self.null}, default={self.default})"
        )


class AutoField(Field):
    """
    Represents an auto-incrementing integer primary key field.
    """

    def __init__(self, primary_key=True, unique=False, null=False):
        """
        Initialize an AutoField instance.

        Parameters:
            primary_key (bool): Indicates if the field is a primary key.
            unique (bool): Indicates if the field values must be unique.
            null (bool): Indicates if the field allows NULL values.

        Raises:
            ValueError: If primary_key is set to False, unique is set to True, or null is set to True.
        """
        super().__init__(primary_key, unique, null)
        if primary_key is False:
            raise ValueError("You can't provide any value for AutoField")
        if unique is True:
            raise ValueError("You can't provide any value for AutoField")
        if null is True:
            raise ValueError("You can't provide any value for AutoField")

    def to_sql(self):
        """
        Get the SQLite data type for the AutoField.

        Returns:
            str: SQLite data type.
        """
        return "INTEGER PRIMARY KEY AUTOINCREMENT"


class IntegerField(Field):
    """
    Represents a field for storing integer values.

    Attributes:
        default: Default value for the field.
    """

    def __init__(self, primary_key=False, unique=False, null=True, default=None):
        """
        Initialize an IntegerField instance.

        Parameters:
            primary_key (bool): Indicates if the field is a primary key.
            unique (bool): Indicates if the field values must be unique.
            null (bool): Indicates if the field allows NULL values.
            default: Default value for the field.
        """
        super().__init__(primary_key, unique, null)
        if primary_key is True:
            raise ValueError("Instead use AutoField as Primary Key")
        self.default = default

    def to_sql(self):
        """
        Get the SQLite data type for the IntegerField.

        Returns:
            str: SQLite data type.
        """
        sql = f"INTEGER"
        sql += " UNIQUE" if self.unique else ""
        sql += " NOT NULL" if not self.null else ""
        sql += f" DEFAULT {self.default}" if not self.default else " DEFAULT NULL"
        return sql


class DecimalField(Field):
    """
    Represents a field for storing decimal values.

    Attributes:
        default: Default value for the field.
    """

    def __init__(self, primary_key=False, unique=False, null=True, default=None):
        """
        Initialize a DecimalField instance.

        Parameters:
            primary_key (bool): Indicates if the field is a primary key.
            unique (bool): Indicates if the field values must be unique.
            null (bool): Indicates if the field allows NULL values.
            default: Default value for the field.
        """
        super().__init__(primary_key, unique, null)
        if primary_key is True or unique is True:
            raise ValueError("For Decimal values primary_key or unique cannot be True")
        self.default = default

    def to_sql(self):
        """
        Get the SQLite data type for the DecimalField.

        Returns:
            str: SQLite data type.
        """
        sql = f"DECIMAL"
        sql += f" NOT NULL" if not self.null else ""
        sql += f" DEFAULT {self.default}" if not self.default else " DEFAULT NULL"
        return sql


class FloatField(Field):
    """
    Represents a field for storing floating-point values.

    Attributes:
        default: Default value for the field.
    """

    def __init__(self, primary_key=False, unique=False, null=True, default=None):
        """
        Initialize a FloatField instance.

        Parameters:
            primary_key (bool): Indicates if the field is a primary key.
            unique (bool): Indicates if the field values must be unique.
            null (bool): Indicates if the field allows NULL values.
            default: Default value for the field.
        """
        super().__init__(primary_key, unique, null)
        if primary_key is True or unique is True:
            raise ValueError(
                "For Decimal or Float values primary_key or unique cannot be True"
            )
        self.default = default

    def to_sql(self):
        """
        Get the SQLite data type for the FloatField.

        Returns:
            str: SQLite data type.
        """
        sql = f"NUMERIC"
        sql += f" NOT NULL" if not self.null else ""
        sql += f" DEFAULT {self.default}" if not self.default else " DEFAULT NULL"
        return sql


class DateTimeField(Field):
    """
    Represents a field for storing date and time values.
    """

    def __init__(self, primary_key=False, unique=False, null=True):
        """
        Initialize a DateTimeField instance.

        Parameters:
            primary_key (bool): Indicates if the field is a primary key.
            unique (bool): Indicates if the field values must be unique.
            null (bool): Indicates if the field allows NULL values.
        """
        super().__init__(primary_key, unique, null)
        if primary_key is True or unique is True:
            raise ValueError("For DateTimeField primary key or unique cannot be True")

    def to_sql(self):
        """
        Get the SQLite data type for the DateTimeField.

        Returns:
            str: SQLite data type.
        """
        sql = f"TEXT"
        sql += f" NOT NULL" if not self.null else ""
        return sql


class BooleanField(Field):
    """
    Represents a field for storing boolean values.

    Attributes:
        default: Default value for the field.
    """

    def __init__(self, primary_key=False, unique=False, null=True, default=0):
        """
        Initialize a BooleanField instance.

        Parameters:
            primary_key (bool): Indicates if the field is a primary key.
            unique (bool): Indicates if the field values must be unique.
            null (bool): Indicates if the field allows NULL values.
            default: Default value for the field.
        """
        super().__init__(primary_key, unique, null)
        if primary_key is True or unique is True:
            raise ValueError("For BooleanField primary key or unique cannot be True")
        self.default = default

    def to_sql(self):
        """
        Get the SQLite data type for the BooleanField.

        Returns:
            str: SQLite data type.
        """
        return f"INTEGER DEFAULT {self.default}"


class ImageField(Field):
    """
    Represents a field for storing image file paths.
    """

    def __init__(self, primary_key=False, unique=False, null=True, file_path=None):
        """
        Initialize an ImageField instance.

        Parameters:
            primary_key (bool): Indicates if the field is a primary key.
            unique (bool): Indicates if the field values must be unique.
            null (bool): Indicates if the field allows NULL values.
        """
        super().__init__(primary_key, unique, null)
        if primary_key is True or unique is True:
            raise ValueError("For ImageField primary key or unique cannot be True")

    def to_sql(self):
        """
        Get the SQLite data type for the ImageField.

        Returns:
            str: SQLite data type.
        """
        return f"TEXT"


class FileField(Field):
    """
    Represents a field for storing file paths.
    """

    def __init__(self, primary_key=False, unique=False, null=True):
        """
        Initialize a FileField instance.

        Parameters:
            primary_key (bool): Indicates if the field is a primary key.
            unique (bool): Indicates if the field values must be unique.
            null (bool): Indicates if the field allows NULL values.
        """
        super().__init__(primary_key, unique, null)
        if primary_key is True or unique is True:
            raise ValueError("For FileField primary key or unique cannot be True")

    def to_sql(self):
        """
        Get the SQLite data type for the FileField.

        Returns:
            str: SQLite data type.
        """
        return f"TEXT"

"""
This module handles schema management and database connections.
It is not intended for handling queries.
"""

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
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(self._database_name)
            except Exception as e:
                raise Exception(f"{e}")
        return self._connection
    
    def exec_create_query(self, schema):
        cursor = self._connection.cursor()
        try:
            for query in schema:
                print(query)
                cursor.execute(query)
                self._connection.commit()
        except Exception as e:
            raise e
        finally:
            print("Tables Migrated")
    

    def close(self):
        """Close the database connection."""
        self._connection.close()


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

    def generate_table(self, table_name, definition):
        """
        Generate SQL for creating a table.

        Parameters:
        - table_name (str): Name of the table.
        - definition (str): Definition of the table's columns.

        Returns:
        str: SQL for creating the table.
        """
        # print(table_name)
        # print(definition)
        return self.sql_create_table.format(table_name=table_name, definition=definition)


class SingletonMigrationManager(type):
    """
    Metaclass for implementing a singleton pattern for the MigrationManager class.
    NOTE: Since I have combined the file no need to have two different SingletonManager
    _instances = {} will do the trick
    """

    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            instance = super().__call__(*args, **kwargs)
            cls._instance = instance
        return cls._instance


class MigrationManager(DatabaseSchemaEditor, metaclass=SingletonMigrationManager):
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
        self.migration = str()
        self.schema = []
        self._create_migrations()

    def _create_migrations(self):
        """
        Create database migration scripts for the specified models.

        Raises:
        ValueError: If a model is not an instance of the Model class.
        """
        for model in self.models:
            if not issubclass(model, Model):
                raise ValueError("Make sure you inherit Model when creating Models")
            else:
                obj = model().get_column_details()
                table_name = model()._get_table_name()
                # table_query = f"{table_name} ({model.get_column_details()})"
                table_query = self.generate_table(table_name=table_name, definition=model().get_column_details())
                print(table_query)
                self.schema.append(table_query)
        print(self.schema)

    def apply(self, connection):
        """
        Apply database migrations delegate work to DBConnector
        """
        connection.exec_create_query(schema=self.schema)
        # DataBaseConnector.exec_create_query(schema=self.schema)


"""
This section has classes Related to Query and Model base class

Attributes:
    ``__all__`` (list): List of classes available in this module.
    ``QueryBuilder``: Class for building queries to fetch data from the database.
    ``QueryManager``: Class containing functions to execute queries.
    ``Model``: Base class for building tables in the database.

Classes:
    ``QueryBuilder``: Class for building queries to fetch data from the database.
    ``QueryManager``: Class containing functions to execute queries.
    ``Model``: Base class for building tables in the database.

"""

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
    
    @classmethod
    def _get_table_name(cls):
        if cls._table_name:
            return cls._table_name
        else:
            return (cls.__name__).lower()
         
    @classmethod
    def get_column_details(cls):
        sql_args = []
        for field_name, field_obj in cls.__dict__.items():
            if isinstance(field_obj, Field):
                sql_args.append(" ".join([field_name, field_obj.to_sql()]))
                # print(" ".join([field_name, field_obj.to_sql()]))
        # print(", ".join(sql_args))
        return ",".join(sql_args)

