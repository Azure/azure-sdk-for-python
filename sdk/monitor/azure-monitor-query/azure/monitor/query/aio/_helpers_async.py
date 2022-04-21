#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


def get_authentication_policy(
    credential: "AsyncTokenCredential",
    audience: str = None
) -> AsyncBearerTokenCredentialPolicy:
    """Returns the correct authentication policy"""
    if not audience:
        audience = "https://api.loganalytics.io/"
    scope = audience.rstrip('/') + "/.default"
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return AsyncBearerTokenCredentialPolicy(
            credential, scope
        )

    raise TypeError("Unsupported credential")


def get_metrics_authentication_policy(
    credential: "AsyncTokenCredential",
    audience: str = None
) -> AsyncBearerTokenCredentialPolicy:
    """Returns the correct authentication policy"""
    if not audience:
        audience = "https://management.azure.com/"
    scope = audience.rstrip('/') + "/.default"
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return AsyncBearerTokenCredentialPolicy(
            credential, scope
        )

    raise TypeError("Unsupported credential")
