# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline.policies import (
    BearerTokenCredentialPolicy,
)

def get_authentication_policy(base_url, credential):
    # type: (TokenCredential) -> SansIOHttpPolicy
    authentication_policy = None
    scope = base_url.strip("/") + "/.default"
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        authentication_policy = BearerTokenCredentialPolicy(credential, scope)
    else:
        raise TypeError("Please provide an instance from azure-identity "
                        "or a class that implement the 'get_token protocol")

    return authentication_policy