#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy


def get_authentication_policy(credential: AsyncTokenCredential, audience: str) -> AsyncBearerTokenCredentialPolicy:
    """Returns the correct authentication policy"""
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    scope = audience.rstrip("/") + "/.default"
    if hasattr(credential, "get_token"):
        return AsyncBearerTokenCredentialPolicy(credential, scope)

    raise TypeError("Unsupported credential")
