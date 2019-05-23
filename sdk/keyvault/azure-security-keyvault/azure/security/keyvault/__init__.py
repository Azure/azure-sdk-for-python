# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from .vault_client import VaultClient
from .version import VERSION

__all__ = ["VaultClient"]

__version__ = VERSION
