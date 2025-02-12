# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Union, overload
from azure.core.credentials import TokenCredential, AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import (
    AsyncBearerTokenCredentialPolicy,
    BearerTokenCredentialPolicy,
)
from .._credential.call_automation_policy import CallAutomationHMACCredentialsPolicy
from .custom_policy import CustomHMACCredentialsPolicy

@overload
def get_authentication_policy(
    endpoint: str,
    credential: Union[TokenCredential, AsyncTokenCredential, AzureKeyCredential, str],
    acs_url: str,
    decode_url: bool = False,
    is_async: bool = False,
):
    """Returns the correct authentication policy based on which credential is being passed.

    :param endpoint: The endpoint to which we are authenticating to.
    :type endpoint: str
    :param credential: The credential we use to authenticate to the service
    :type credential: Union[TokenCredential, AsyncTokenCredential, AzureKeyCredential, str]
    :param acs_url: The endpoint of the Azure Communication Service.
    :type acs_url: str
    :param bool decode_url: `True` if there is a need to decode the url. Default value is `False`
    :param bool is_async: For async clients there is a need to decode the url

    :return: Either AsyncBearerTokenCredentialPolicy or BearerTokenCredentialPolicy
     or CallAutomationHMACCredentialsPolicy
    :rtype: ~azure.core.pipeline.policies.AsyncBearerTokenCredentialPolicy or
    ~azure.core.pipeline.policies.BearerTokenCredentialPolicy or
    ~azure.communication.callautomation.credential.callautomationpolicy.CallAutomationHMACCredentialsPolicy
    """

    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        if is_async:
            return AsyncBearerTokenCredentialPolicy(
                credential, "https://communication.azure.com//.default"  # type: ignore
            )
        return BearerTokenCredentialPolicy(credential, "https://communication.azure.com//.default")  # type: ignore
    if isinstance(credential, (AzureKeyCredential, str)):
        return CallAutomationHMACCredentialsPolicy(endpoint, acs_url, credential, decode_url=decode_url)

    raise TypeError(
        f"Unsupported credential: {format(type(credential))}. Use an access token string to use HMACCredentialsPolicy"
        "or a token credential from azure.identity"
    )

@overload
def get_authentication_policy(
    endpoint: str,
    credential: Union[TokenCredential, AsyncTokenCredential, AzureKeyCredential, str],
    decode_url: bool = False,
    is_async: bool = False,
):

    """Returns the correct authentication policy based on which credential is being passed.

    :param endpoint: The endpoint to which we are authenticating to.
    :type endpoint: str
    :param credential: The credential we use to authenticate to the service
    :type credential: Union[TokenCredential, AsyncTokenCredential, AzureKeyCredential, str]
    :param bool decode_url: `True` if there is a need to decode the url. Default value is `False`
    :param bool is_async: For async clients there is a need to decode the url

    :return: Either AsyncBearerTokenCredentialPolicy or BearerTokenCredentialPolicy or HMACCredentialsPolicy
    :rtype: ~azure.core.pipeline.policies.AsyncBearerTokenCredentialPolicy or
    ~azure.core.pipeline.policies.BearerTokenCredentialPolicy or
    ~azure.communication.callautomation.shared.policy.HMACCredentialsPolicy
    """

def get_authentication_policy(
    endpoint: str,
    credential: Union[TokenCredential, AsyncTokenCredential, AzureKeyCredential, str],
    **kwargs,
):
    # type: (...) -> Union[AsyncBearerTokenCredentialPolicy, BearerTokenCredentialPolicy, HMACCredentialsPolicy]
    """Returns the correct authentication policy based on which credential is being passed.

    :param endpoint: The endpoint to which we are authenticating to.
    :type endpoint: str
    :param credential: The credential we use to authenticate to the service
    :type credential: Union[TokenCredential, AsyncTokenCredential, AzureKeyCredential, str]   
    :return: Either AsyncBearerTokenCredentialPolicy or BearerTokenCredentialPolicy or HMACCredentialsPolicy
    :rtype: ~azure.core.pipeline.policies.AsyncBearerTokenCredentialPolicy or
    ~azure.core.pipeline.policies.BearerTokenCredentialPolicy or
    ~azure.communication.callautomation.shared.policy.HMACCredentialsPolicy
    """

    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    is_async = kwargs.pop("is_async", False)
    decode_url = kwargs.pop("decode_url", False)
    acs_url = kwargs.pop("acs_url", None)
    if hasattr(credential, "get_token"):
        if is_async:
            return AsyncBearerTokenCredentialPolicy(
                credential, "https://communication.azure.com//.default"  # type: ignore
            )
        return BearerTokenCredentialPolicy(credential, "https://communication.azure.com//.default")  # type: ignore
    if acs_url and  isinstance(credential, (AzureKeyCredential, str)):
        return CallAutomationHMACCredentialsPolicy(endpoint, acs_url, credential, decode_url=decode_url)

    if isinstance(credential, (AzureKeyCredential, str)):
        return CustomHMACCredentialsPolicy(endpoint, credential, decode_url=decode_url)

    raise TypeError(
        f"Unsupported credential: {format(type(credential))}. Use an access token string to use HMACCredentialsPolicy"
        "or a token credential from azure.identity"
    )
