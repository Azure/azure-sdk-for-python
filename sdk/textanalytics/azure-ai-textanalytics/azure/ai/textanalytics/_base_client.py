# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from enum import Enum
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from ._generated import TextAnalyticsClient as _TextAnalyticsClient
from ._policies import TextAnalyticsResponseHookPolicy
from ._user_agent import USER_AGENT

class TextAnalyticsApiVersion(str, Enum):
    """Text Analytics API versions supported by this package"""

    #: this is the default version
    V3_1_PREVIEW = "v3.1-preview.4"
    V3_0 = "v3.0"

def _authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(
            name="Ocp-Apim-Subscription-Key", credential=credential
        )
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError("Unsupported credential: {}. Use an instance of AzureKeyCredential "
                        "or a token credential from azure.identity".format(type(credential)))
    return authentication_policy


class TextAnalyticsClientBase(object):
    def __init__(self, endpoint, credential, **kwargs):
        self._client = _TextAnalyticsClient(
            endpoint=endpoint,
            credential=credential,
            api_version=kwargs.pop("api_version", TextAnalyticsApiVersion.V3_1_PREVIEW),
            sdk_moniker=USER_AGENT,
            authentication_policy=_authentication_policy(credential),
            custom_hook_policy=TextAnalyticsResponseHookPolicy(**kwargs),
            **kwargs
        )


    def __enter__(self):
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self):
        # type: () -> None
        """Close sockets opened by the client.
        Calling this method is unnecessary when using the client as a context manager.
        """
        self._client.close()
