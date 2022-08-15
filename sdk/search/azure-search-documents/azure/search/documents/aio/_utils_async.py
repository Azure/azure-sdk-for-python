# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.pipeline import policies

from .._utils import CREDENTIAL_SCOPES


def get_async_authentication_policy(credential):
    authentication_policy = policies.AsyncBearerTokenCredentialPolicy(
        credential, *CREDENTIAL_SCOPES
    )
    return authentication_policy
