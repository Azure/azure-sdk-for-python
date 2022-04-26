#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Optional
from azure.core.credentials import TokenCredential
from azure.core.pipeline.policies import BearerTokenCredentialPolicy

def get_authentication_policy(
    endpoint: str,
    credential: TokenCredential,
) -> BearerTokenCredentialPolicy:
    # type: (...) -> BearerTokenCredentialPolicy
    """Returns the correct authentication policy"""
    scope = endpoint.rstrip('/') + "/.default"
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return BearerTokenCredentialPolicy(
            credential, scope
        )

    raise TypeError("Unsupported credential")
