# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Driver package exports."""

from __future__ import annotations

from importlib.util import find_spec
import warnings
from typing import TYPE_CHECKING

from .base import DriverClient, ResultSet

if TYPE_CHECKING:
    from ..config import MirrorServingConfiguration
    from ..credentials import CredentialSource


_SUPPORTED_DRIVERS = ("mssql-python", "pyodbc")


def _driver_available(driver: str) -> bool:
    module_name = "mssql_python" if driver == "mssql-python" else "pyodbc"
    return find_spec(module_name) is not None


def _create_driver(
    driver: str, config: MirrorServingConfiguration, credentials: CredentialSource
) -> DriverClient:
    if driver == "mssql-python":
        from .mssql_driver import MssqlDriverClient

        return MssqlDriverClient(config=config, credentials=credentials)

    from .pyodbc_driver import PyOdbcDriverClient

    return PyOdbcDriverClient(config=config, credentials=credentials)


def get_driver_client(
    config: MirrorServingConfiguration,
    credentials: CredentialSource,
    prefer_driver: str | None = None,
) -> DriverClient:
    """Get an appropriate driver client based on availability.

    Priority order (unless prefer_driver is specified):
    1. mssql-python (MssqlDriverClient) - recommended, pure Python
    2. pyodbc (PyOdbcDriverClient) - legacy, requires system ODBC driver

    Args:
        config: Mirror serving configuration
        credentials: Credential source
        prefer_driver: Optional driver preference ('mssql-python' or 'pyodbc')

    Returns:
        DriverClient instance

    Raises:
        ImportError: If no supported driver is available
    """
    if prefer_driver is not None and prefer_driver not in _SUPPORTED_DRIVERS:
        raise ValueError(
            f"Unsupported driver preference {prefer_driver!r}; expected one of {_SUPPORTED_DRIVERS}"
        )

    candidates = list(_SUPPORTED_DRIVERS)
    if prefer_driver is not None:
        candidates.remove(prefer_driver)
        candidates.insert(0, prefer_driver)

    for index, driver in enumerate(candidates):
        if _driver_available(driver):
            return _create_driver(driver, config, credentials)
        if index == 0 and prefer_driver is not None:
            warnings.warn(
                f"Preferred driver {prefer_driver!r} not available, falling back to auto-detection",
                stacklevel=2,
            )

    raise ImportError(
        "No SQL driver available. Install one of:\n"
        "  pip install azure-cosmos-fabric-mapper[sql]   # mssql-python (recommended)\n"
        "  pip install azure-cosmos-fabric-mapper[odbc]  # pyodbc (legacy)"
    )


__all__ = ["DriverClient", "ResultSet", "get_driver_client"]
