# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""mssql-python driver implementation (primary, pure Python)."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Sequence

from ..config import MirrorServingConfiguration
from ..credentials import CredentialSource
from ..diagnostics import redact
from ..errors import DriverError, MissingOptionalDependencyError
from .base import ResultSet


def _import_mssql_python():
    """Attempt to import mssql-python with helpful error message if missing.
    
    Returns:
        mssql_python module
        
    Raises:
        MissingOptionalDependencyError: If mssql-python is not installed
    """
    try:
        import mssql_python  # type: ignore

        return mssql_python
    except ImportError as exc:  # pragma: no cover
        raise MissingOptionalDependencyError(
            "mssql-python is required for SQL connectivity. "
            "Install with 'pip install azure-cosmos-fabric-mapper[sql]'."
        ) from exc


@dataclass
class MssqlDriverClient:
    """SQL driver client using mssql-python for Fabric SQL connectivity.
    
    This is the primary driver implementation using Microsoft's pure Python
    TDS driver. It requires no system-level ODBC driver installation on Windows.
    
    Note: This client serializes all queries through a single connection with a lock.
    It is not designed for high-concurrency use. For concurrent workloads, create
    separate driver client instances per thread.
    
    Attributes:
        config: Mirror serving configuration
        credentials: Credential source for SQL authentication
    """
    
    config: MirrorServingConfiguration
    credentials: CredentialSource
    _connection: Any = field(default=None, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def __post_init__(self):
        self.config.validate()

    def execute(self, sql: str, params: Sequence[Any]) -> ResultSet:
        """Execute a parameterized SQL query via mssql-python.
        
        Args:
            sql: Parameterized SQL query (uses '?' placeholders)
            params: Parameter values in order
            
        Returns:
            ResultSet containing columns and rows
            
        Raises:
            DriverError: If execution fails
            MissingOptionalDependencyError: If mssql-python is not installed
        """
        mssql_python = _import_mssql_python()

        # Build connection string (same format as ODBC for compatibility)
        conn_str = (
            f"Server=tcp:{self.config.fabric_server};"
            f"Database={self.config.fabric_database};"
            "Encrypt=yes;TrustServerCertificate=no;"
        )

        try:
            with self._lock:
                conn = self._connection
                if conn is not None:
                    try:
                        cur = conn.cursor()
                        try:
                            cur.execute(sql, list(params))
                            columns = [c[0] for c in cur.description] if cur.description else []
                            rows = [tuple(r) for r in cur.fetchall()] if cur.description else []
                        finally:
                            cur.close()
                        return ResultSet(columns=columns, rows=rows)
                    except Exception as stale_exc:
                        # Any error on a cached connection may indicate staleness.
                        # Close and retry with a fresh connection.
                        try:
                            self._connection.close()
                        except Exception:
                            pass
                        self._connection = None

                # Get access token from credentials (same struct as pyodbc)
                token_struct = self.credentials.get_sql_access_token_struct()
                
                # mssql-python supports attrs_before for token auth (same as pyodbc)
                # SQL_COPT_SS_ACCESS_TOKEN = 1256
                conn = mssql_python.connect(conn_str, attrs_before={1256: token_struct})
                self._connection = conn
                
                cur = conn.cursor()
                try:
                    cur.execute(sql, list(params))
                    
                    # Extract columns and rows (DB-API 2.0 compliant)
                    columns = [c[0] for c in cur.description] if cur.description else []
                    rows = [tuple(r) for r in cur.fetchall()] if cur.description else []
                finally:
                    cur.close()
                
                return ResultSet(columns=columns, rows=rows)
                    
        except MissingOptionalDependencyError:
            raise
        except Exception as exc:
            raise DriverError(f"Driver execution failed: {type(exc).__name__}: {redact(str(exc))}") from exc

    def close(self) -> None:
        """Close the cached connection, if any."""
        with self._lock:
            if self._connection is not None:
                try:
                    self._connection.close()
                except Exception:
                    pass
                self._connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
