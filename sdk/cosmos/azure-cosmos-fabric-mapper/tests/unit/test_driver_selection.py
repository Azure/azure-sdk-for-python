"""Tests for optional SQL driver selection."""

from unittest.mock import Mock, patch

import pytest

from azure.cosmos.fabric_mapper.config import MirrorServingConfiguration
from azure.cosmos.fabric_mapper.driver import get_driver_client


@pytest.fixture
def config():
    return MirrorServingConfiguration("server.example", "database", "container")


@pytest.mark.parametrize(
    "available, expected_type",
    [
        ({"mssql_python"}, "MssqlDriverClient"),
        ({"pyodbc"}, "PyOdbcDriverClient"),
        ({"mssql_python", "pyodbc"}, "MssqlDriverClient"),
    ],
)
def test_auto_detection_uses_installed_driver(config, available, expected_type):
    with patch(
        "azure.cosmos.fabric_mapper.driver.find_spec",
        side_effect=lambda name: Mock() if name in available else None,
    ):
        driver = get_driver_client(config, Mock())

    assert type(driver).__name__ == expected_type


def test_auto_detection_rejects_missing_drivers(config):
    with patch("azure.cosmos.fabric_mapper.driver.find_spec", return_value=None):
        with pytest.raises(ImportError, match="No SQL driver available"):
            get_driver_client(config, Mock())


def test_preferred_driver_falls_back_when_unavailable(config):
    with patch(
        "azure.cosmos.fabric_mapper.driver.find_spec",
        side_effect=lambda name: Mock() if name == "pyodbc" else None,
    ):
        with pytest.warns(UserWarning, match="falling back"):
            driver = get_driver_client(config, Mock(), prefer_driver="mssql-python")

    assert type(driver).__name__ == "PyOdbcDriverClient"


def test_unknown_preferred_driver_is_rejected(config):
    with pytest.raises(ValueError, match="Unsupported driver preference"):
        get_driver_client(config, Mock(), prefer_driver="unknown")
