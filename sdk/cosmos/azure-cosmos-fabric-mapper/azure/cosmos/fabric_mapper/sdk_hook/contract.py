# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""SDK hook contract for Cosmos SDK integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from ..config import MirrorServingConfiguration
from ..credentials import CredentialSource, DefaultAzureSqlCredential
from ..driver.base import DriverClient
from ..driver import get_driver_client
from ..results.mapper import map_result_set
from ..translate import translate


@dataclass(frozen=True)
class MirroredQueryRequest:
    """Request to run a Cosmos query against a Fabric mirror.
    
    Attributes:
        query: Cosmos SQL query string
        parameters: Query parameters (list of dicts with 'name' and 'value')
    """
    
    query: str
    parameters: Sequence[dict[str, Any]] | None = None


def run_mirrored_query(
    request: MirroredQueryRequest,
    config: MirrorServingConfiguration,
    credentials: CredentialSource | None = None,
    driver: DriverClient | None = None,
) -> list[Any]:
    """Run a Cosmos-style query against a Fabric mirror endpoint.
    
    This is the main entry point for the SDK hook. It translates the query,
    executes it via a driver, and maps results back to Cosmos-like format.
    
    Args:
        request: Query request with Cosmos SQL and parameters
        config: Mirror serving configuration
        credentials: Optional credential source (defaults to DefaultAzureSqlCredential)
        driver: Optional driver client (defaults to auto-selected driver via get_driver_client() (prefers mssql-python))
        
    Returns:
        List of results in Cosmos format (dicts or scalars)
        
    Raises:
        ConfigurationError: If configuration is invalid
        UnsupportedCosmosQueryError: If query uses unsupported features
        DriverError: If query execution fails
        MissingOptionalDependencyError: If no SQL driver (mssql-python or pyodbc) is installed
    """
    config.validate()
    creds = credentials or DefaultAzureSqlCredential()
    auto_created_driver = driver is None
    drv: DriverClient = driver or get_driver_client(config=config, credentials=creds)

    try:
        # Translate Cosmos query to Fabric SQL
        t = translate(request.query, request.parameters, config)

        # Execute via driver
        rs = drv.execute(t.sql, t.params)

        # Map results back to Cosmos format
        mapped = map_result_set(rs, select_value=t.select_value)
        return mapped
    finally:
        if auto_created_driver:
            drv.close()
