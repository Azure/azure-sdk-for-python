#
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.pipeline.policies import BearerTokenCredentialPolicy

def get_authentication_policy(
        credential, # type: TokenCredential
):
    # type: (...) -> BearerTokenCredentialPolicy
    """Returns the correct authentication policy
    """

    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return BearerTokenCredentialPolicy(credential, "https://api.loganalytics.io/.default")

    raise TypeError("Unsupported credential")
