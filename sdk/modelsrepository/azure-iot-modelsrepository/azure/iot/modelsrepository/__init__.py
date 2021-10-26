# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# Main Client
from ._client import ModelsRepositoryClient

# Constants
from ._common import (
    DependencyMode,
    DEFAULT_LOCATION,
    VERSION
)

# Error handling
from .exceptions import ModelError

__all__ = [
    "ModelsRepositoryClient",
    "DEFAULT_LOCATION",
    "ModelError",
    "DependencyMode",
]

__version__ = VERSION
