# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Error taxonomy for the Fabric mapper."""

from __future__ import annotations


class FabricMapperError(RuntimeError):
    """Base error for all mapper failures."""


class MissingOptionalDependencyError(FabricMapperError):
    """Raised when an optional dependency (e.g., pyodbc) is required but missing."""


class UnsupportedCosmosQueryError(FabricMapperError):
    """Raised when the query uses Cosmos SQL features not supported by this mapper."""


class ConfigurationError(FabricMapperError):
    """Raised when MirrorServingConfiguration is invalid or incomplete."""


class CredentialError(FabricMapperError):
    """Raised when credentials are missing or invalid."""


class DriverError(FabricMapperError):
    """Raised for driver connectivity/query execution failures."""
