# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains Identity Configuration for Azure Machine Learning SDKv2."""

from ._credentials import AzureMLOnBehalfOfCredential
from ._exceptions import CredentialUnavailableError

__all__ = [
    "AzureMLOnBehalfOfCredential",
    "CredentialUnavailableError",
]
