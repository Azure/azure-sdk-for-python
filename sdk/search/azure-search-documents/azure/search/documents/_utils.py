# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core.pipeline.policies import BearerTokenCredentialPolicy, AsyncBearerTokenCredentialPolicy

DEFAULT_AUDIENCE = "https://search.azure.com"


def is_retryable_status_code(status_code):
    # type: (int) -> bool
    return status_code in [422, 409, 503]


def get_authentication_policy(credential, **kwargs):
    audience = kwargs.get('audience', None)
    is_async = kwargs.get('is_async', False)
    if not audience:
        audience = DEFAULT_AUDIENCE
    scope = audience.rstrip('/') + '/.default'
    _policy = BearerTokenCredentialPolicy if not is_async else AsyncBearerTokenCredentialPolicy
    authentication_policy = _policy(
        credential, scope
    )
    return authentication_policy
