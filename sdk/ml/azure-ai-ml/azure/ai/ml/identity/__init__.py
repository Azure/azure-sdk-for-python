# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._credentials import AzureMLOnBehalfOfCredential
from ._exceptions import CredentialUnavailableError

__all__ = [
    "AzureMLOnBehalfOfCredential",
    "CredentialUnavailableError",
]
