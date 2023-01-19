#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Optional

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy


def get_authentication_policy(
    credential: AsyncTokenCredential,
    audience: Optional[str] = None
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
    credential: AsyncTokenCredential,
    audience: Optional[str] = None
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
