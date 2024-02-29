import pytest
import logging

from orm.orm import DataBaseConnector


def test_database_connector(caplog):
    caplog.set_level(logging.INFO)
    connector1 = DataBaseConnector(database_name="test_db.db")
    connector2 = DataBaseConnector(database_name="test_db.db")

    assert connector1 == connector2
    # new database instance with a different name
    connector3 = DataBaseConnector(database_name="new_db")
    assert connector3 == connector2
