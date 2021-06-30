#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

def get_authentication_policy(
        credential: 'TokenCredential'
) -> AsyncBearerTokenCredentialPolicy:
    """Returns the correct authentication policy
    """

    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return AsyncBearerTokenCredentialPolicy(credential, "https://api.loganalytics.io/.default")

    raise TypeError("Unsupported credential")

def get_metrics_authentication_policy(
        credential: 'TokenCredential'
) -> AsyncBearerTokenCredentialPolicy:
    """Returns the correct authentication policy
    """

    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return AsyncBearerTokenCredentialPolicy(credential, "https://management.azure.com/.default")

    raise TypeError("Unsupported credential")
