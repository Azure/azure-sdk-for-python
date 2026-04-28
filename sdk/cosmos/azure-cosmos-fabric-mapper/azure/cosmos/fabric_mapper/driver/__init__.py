# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Driver package exports."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from .base import DriverClient, ResultSet

if TYPE_CHECKING:
    from ..config import MirrorServingConfiguration
    from ..credentials import CredentialSource

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
    failed_drivers: set[str] = set()

    # Try preferred driver first if specified
    if prefer_driver == "mssql-python":
        try:
            from .mssql_driver import MssqlDriverClient
            return MssqlDriverClient(config=config, credentials=credentials)
        except ImportError:
            failed_drivers.add("mssql-python")
            warnings.warn(f"Preferred driver 'mssql-python' not available, falling back to auto-detection")
    
    elif prefer_driver == "pyodbc":
        try:
            from .pyodbc_driver import PyOdbcDriverClient
            return PyOdbcDriverClient(config=config, credentials=credentials)
        except ImportError:
            failed_drivers.add("pyodbc")
            warnings.warn(f"Preferred driver 'pyodbc' not available, falling back to auto-detection")
    
    # Auto-detection: try mssql-python first (unless already failed), then pyodbc
    if "mssql-python" not in failed_drivers:
        try:
            from .mssql_driver import MssqlDriverClient
            return MssqlDriverClient(config=config, credentials=credentials)
        except ImportError:
            pass
    
    if "pyodbc" not in failed_drivers:
        try:
            from .pyodbc_driver import PyOdbcDriverClient
            return PyOdbcDriverClient(config=config, credentials=credentials)
        except ImportError:
            pass
    
    raise ImportError(
        "No SQL driver available. Install one of:\n"
        "  pip install azure-cosmos-fabric-mapper[sql]   # mssql-python (recommended)\n"
        "  pip install azure-cosmos-fabric-mapper[odbc]  # pyodbc (legacy)"
    )


__all__ = ["DriverClient", "ResultSet", "get_driver_client"]
