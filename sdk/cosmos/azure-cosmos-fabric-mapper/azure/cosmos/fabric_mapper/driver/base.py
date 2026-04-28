# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Base driver protocol and result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence


@dataclass(frozen=True)
class ResultSet:
    """Tabular result set from a driver query.
    
    Attributes:
        columns: Column names
        rows: Rows of data (tuples matching column order)
    """
    
    columns: list[str]
    rows: list[tuple[Any, ...]]


class DriverClient(Protocol):
    """Protocol for executing parameterized SQL queries.
    
    This abstracts the underlying driver (pyodbc, JDBC, etc.) and allows
    for testing with stub implementations.
    """

    def execute(self, sql: str, params: Sequence[Any]) -> ResultSet:
        """Execute a parameterized SQL query.
        
        Args:
            sql: Parameterized SQL query (uses '?' placeholders)
            params: Parameter values in order
            
        Returns:
            ResultSet containing columns and rows
            
        Raises:
            DriverError: If execution fails
        """
        ...  # pragma: no cover

    def close(self) -> None:
        """Close the driver client and release resources."""
        ...  # pragma: no cover
