"""Tests for cached SQL connection error handling."""

from unittest.mock import Mock, patch

import pytest

from azure.cosmos.fabric_mapper.config import MirrorServingConfiguration
from azure.cosmos.fabric_mapper.driver.mssql_driver import MssqlDriverClient
from azure.cosmos.fabric_mapper.driver.pyodbc_driver import PyOdbcDriverClient
from azure.cosmos.fabric_mapper.errors import DriverError


@pytest.mark.parametrize("driver_type", [MssqlDriverClient, PyOdbcDriverClient])
def test_cached_connection_errors_are_not_reexecuted(driver_type):
    connection = Mock()
    connection.cursor.return_value.execute.side_effect = RuntimeError("invalid query")
    credentials = Mock()
    driver = driver_type(
        MirrorServingConfiguration("server.example", "database", "container"),
        credentials,
    )
    driver._connection = connection

    import_target = (
        "azure.cosmos.fabric_mapper.driver.mssql_driver._import_mssql_python"
        if driver_type is MssqlDriverClient
        else "azure.cosmos.fabric_mapper.driver.pyodbc_driver._import_pyodbc"
    )
    with patch(import_target, return_value=Mock()):
        with pytest.raises(DriverError, match="RuntimeError"):
            driver.execute("SELECT invalid", [])

    connection.cursor.return_value.execute.assert_called_once()
    credentials.get_sql_access_token_struct.assert_not_called()
