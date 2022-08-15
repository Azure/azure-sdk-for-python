# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.pipeline import policies

CREDENTIAL_SCOPES = ["https://search.azure.com/.default"]


def is_retryable_status_code(status_code):
    # type: (int) -> bool
    return status_code in [422, 409, 503]


def get_authentication_policy(credential):
    authentication_policy = policies.BearerTokenCredentialPolicy(
        credential, *CREDENTIAL_SCOPES
    )
    return authentication_policy
