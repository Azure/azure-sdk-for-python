# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import json
import os

from azure.core.credentials import AccessToken

from azure.core.credentials import AzureKeyCredential
from common.common import AzureKeyInQueryCredentialPolicy


from azure.maps.search.models import TextFormat
from azure.maps.search import SearchClient

from azure.identity import DefaultAzureCredential
from azure.core.pipeline.policies import HeadersPolicy
from azure.core.credentials import TokenCredential, AsyncTokenCredential



def get_authentication_policy(
        credential, # type: TokenCredential or AsyncTokenCredential
        is_async=False, # type: bool
):
    # type: (...) -> BearerTokenCredentialPolicy or HMACCredentialPolicy
    """Returns the correct authentication policy based
    on which credential is being passed.
    :param credential: The credential we use to authenticate to the service
    :type credential: TokenCredential or str
    :param isAsync: For async clients there is a need to decode the url
    :type bool: isAsync or str
    :rtype: ~azure.core.pipeline.policies.BearerTokenCredentialPolicy
    """

    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential):
        return (('None', x_ms_client_id=os.environ.get("CLIENT_ID", None), authentication_policy=AzureKeyInQueryCredentialPolicy(AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), "subscription-key")))

    if isinstance(credential, str):
        return (DefaultAzureCredential(), x_ms_client_id=os.environ.get("CLIENT_ID", None), headers_policy=HeadersPolicy({'x-ms-client-id': os.environ.get("CLIENT_ID", None)}))
