import pytest
import logging

import sys

sys.path.append("../")

from orm.orm import CharField, TextField


def test_char_field(caplog):
    caplog.set_level(logging.INFO)
    test_cases = [
        (
            {
                "max_length": None,
            },
            ValueError,
            "max_length can't be None or less than 2 characters and it should be an integer!",
            "",
        ),
        (
            {
                "max_length": "None",
            },
            ValueError,
            "max_length can't be None or less than 2 characters and it should be an integer!",
            "",
        ),
        (
            {"max_length": 0},
            ValueError,
            "max_length can't be None or less than 2 characters and it should be an integer!",
            "",
        ),
        (
            {"max_length": 566},
            ValueError,
            "CharField can not be longer than 255 characters. Use TextField!",
            "",
        ),
        (
            {"max_length": 10, "primary_key": True, "null": True},
            ValueError,
            "When using primary_key=True, do not set anything other than max_length",
            "",
        ),
        (
            {
                "max_length": 50,
                "primary_key": True,
            },
            ValueError,
            "",
            "VARCHAR(50) NOT NULL PRIMARY KEY",
        ),
        (
            {
                "max_length": 50,
                "primary_key": True,
                "unique": True,
                "null": False,
            },
            ValueError,
            "When using primary_key=True, do not set anything other than max_length",
            "",
        ),
        (
            {
                "max_length": 50,
                "primary_key": False,
                "unique": False,
                "null": True,
            },
            ValueError,
            "",
            "VARCHAR(50)",
        ),
        (
            {
                "max_length": 50,
                "primary_key": True,
                "unique": True,
                "null": False,
                "default": "some text",
            },
            ValueError,
            "When using primary_key=True, do not set anything other than max_length",
            "",
        ),
        (
            {
                "max_length": 50,
                "primary_key": False,
                "unique": False,
                "null": False,
                "default": "default_value_here",
            },
            ValueError,
            "",
            "VARCHAR(50) NOT NULL DEFAULT 'default_value_here'",
        ),
        (
            {
                "max_length": 50,
                "primary_key": False,
                "unique": True,
                "null": False,
                "default": "default_value_here",
            },
            ValueError,
            "If using CharField as unique you can't give a default value",
            "",
        ),
        (
            {
                "max_length": 50,
                "primary_key": False,
                "unique": True,
                "null": False,
                "default": None,
            },
            ValueError,
            "",
            "VARCHAR(50) UNIQUE",
        ),
        (
            {
                "max_length": 50,
                "primary_key": False,
                "unique": True,
                "null": True,
                "default": "None",
            },
            ValueError,
            "If using CharField as unique you can't give a default value",
            "",
        ),
        (
            {
                "max_length": 50,
                "primary_key": False,
                "unique": True,
                "null": False,
                "default": "None",
            },
            ValueError,
            "If using CharField as unique you can't give a default value",
            "",
        ),
    ]
    for kwargs, expected_exception, expected_message, result in test_cases:
        try:
            # logging.info(CharField(**kwargs))
            name = CharField(**kwargs)
            logging.info(name.to_sql())
            if result is not None:
                assert str(name.to_sql()) == result
        except Exception as e:
            logging.info(str(e))
            assert isinstance(e, expected_exception)

            assert str(e) == expected_message
