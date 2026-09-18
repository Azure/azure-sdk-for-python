# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# -------------------------------------------------------------------------
"""Azure Cosmos to Fabric mirror mapper."""

from .config import MirrorServingConfiguration
from .credentials import CredentialSource
from .errors import (
    ConfigurationError,
    CredentialError,
    DriverError,
    FabricMapperError,
    MissingOptionalDependencyError,
    UnsupportedCosmosQueryError,
)
from .sdk_hook import MirroredQueryRequest, run_mirrored_query

from ._version import VERSION

__version__ = VERSION

__all__ = [
    "ConfigurationError",
    "CredentialError",
    "CredentialSource",
    "DriverError",
    "FabricMapperError",
    "MirrorServingConfiguration",
    "MirroredQueryRequest",
    "MissingOptionalDependencyError",
    "UnsupportedCosmosQueryError",
    "run_mirrored_query",
]
