# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Union
from azure.core.credentials import TokenCredential, AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import (
    AsyncBearerTokenCredentialPolicy,
    BearerTokenCredentialPolicy,
)
from .._shared.policy import HMACCredentialsPolicy


def get_authentication_policy(
    endpoint,  # type: str
    credential,  # type: Union[TokenCredential, AsyncTokenCredential, AzureKeyCredential, str]
    decode_url=False,  # type: bool
    is_async=False,  # type: bool
):
    # type: (...) -> Union[AsyncBearerTokenCredentialPolicy, BearerTokenCredentialPolicy, HMACCredentialsPolicy]
    """Returns the correct authentication policy based
    on which credential is being passed.
    :param endpoint: The endpoint to which we are authenticating to.
    :type endpoint: str
    :param credential: The credential we use to authenticate to the service
    :type credential: Union[TokenCredential, AzureKeyCredential, str]
    :param isAsync: For async clients there is a need to decode the url
    :type bool: isAsync or str
    :rtype: ~azure.core.pipeline.policies.BearerTokenCredentialPolicy or
    ~azure.communication.chat.shared.policy.HMACCredentialsPolicy
    """

    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        if is_async:
            return AsyncBearerTokenCredentialPolicy(
                credential, "https://communication.azure.com//.default"  # type: ignore
            )
        return BearerTokenCredentialPolicy(
            credential, "https://communication.azure.com//.default"  # type: ignore
        )
    if isinstance(credential, (AzureKeyCredential, str)):
        return HMACCredentialsPolicy(endpoint, credential, decode_url=decode_url)

    raise TypeError(
        "Unsupported credential: {}. Use an access token string to use HMACCredentialsPolicy"
        "or a token credential from azure.identity".format(type(credential))
    )
