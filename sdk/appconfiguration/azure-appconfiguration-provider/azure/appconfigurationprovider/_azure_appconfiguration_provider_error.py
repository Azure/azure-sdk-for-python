# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

class KeyVaultReferenceError(ValueError):
    """Raised when a Key Vault reference is invalid."""

    def __init__(self, message, *args):
        # type: (str, Any) -> None
        super(KeyVaultReferenceError, self).__init__(message, *args)