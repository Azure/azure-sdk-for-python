# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Configuration for Fabric mirror serving."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import ConfigurationError


@dataclass(frozen=True)
class MirrorServingConfiguration:
    """Configuration for serving Cosmos-like queries from a Fabric mirrored table.
    
    Attributes:
        fabric_server: Fabric Warehouse endpoint (e.g., ``endpoint.datawarehouse.fabric.microsoft.com``)
        fabric_database: Database name in Fabric
        fabric_table: Table name (should match the mirrored Cosmos container)
        fabric_schema: Schema name (default 'dbo')
    """

    fabric_server: str
    fabric_database: str
    fabric_table: str
    fabric_schema: str = "dbo"

    def validate(self) -> None:
        """Validate that required configuration fields are present.
        
        Raises:
            ConfigurationError: If required fields are missing
        """
        missing: list[str] = []
        if not self.fabric_server:
            missing.append("fabric_server")
        if not self.fabric_database:
            missing.append("fabric_database")
        if not self.fabric_table:
            missing.append("fabric_table")
        if missing:
            raise ConfigurationError(f"Missing required config fields: {', '.join(missing)}")


def default_table_sql(config: MirrorServingConfiguration) -> str:
    """Generate the default table reference SQL for a configuration.
    
    Args:
        config: Mirror serving configuration
        
    Returns:
        Fully qualified table reference (e.g., '[dbo].[tablename]')
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    config.validate()
    schema = (config.fabric_schema or "dbo").replace(']', ']]')
    table = config.fabric_table.replace(']', ']]')
    return f"[{schema}].[{table}]"
