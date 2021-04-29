# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# Main Client
from ._client import ModelsRepositoryClient

# Constants
from ._client import (
    DEPENDENCY_MODE_DISABLED,
    DEPENDENCY_MODE_ENABLED,
    DEPENDENCY_MODE_TRY_FROM_EXPANDED,
)

# Error handling
from .exceptions import ModelError

__all__ = [
    "ModelsRepositoryClient",
    "ModelError",
    "DEPENDENCY_MODE_DISABLED",
    "DEPENDENCY_MODE_ENABLED",
    "DEPENDENCY_MODE_TRY_FROM_EXPANDED",
]

from ._constants import VERSION

__version__ = VERSION
