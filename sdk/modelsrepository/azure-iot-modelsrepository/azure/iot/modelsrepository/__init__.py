# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# Main Client
from ._client import ModelsRepositoryClient

# Constants
from ._common import (
    DependencyModeType,
    VERSION
)

# Error handling
from .exceptions import ModelError

__all__ = [
    "ModelsRepositoryClient",
    "ModelError",
    "DependencyModeType",
]

__version__ = VERSION
