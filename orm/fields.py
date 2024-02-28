"""
This module defines various field types for SQLite database and includes mappings for field and relationship types.

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

Functions:
    No functions in this module.
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
            self._unique_constraint_checks()
        else:
            self._default_value_checks()

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
                "When using primary_key=True, do not set null=True, unique=True, or provide a default value. Unique constraint is implied by primary key."
            )

    def _unique_constraint_checks(self):
        if self.null and self.unique:
            raise ValueError("On a unique field you can't set null as True")
        if self.unique and (self.null or self.default):
            raise ValueError(
                "If using CharField as unique you can't give a default value"
            )

    def _default_value_checks(self):
        """
        Check if default value is required.
        """
        print(self.__str__())
        if (not self.primary_key) and (not self.null) and (not self.default):
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
        print(sql)
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
