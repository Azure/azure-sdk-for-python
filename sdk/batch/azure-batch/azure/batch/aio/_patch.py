# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from ._client import BatchClient as GenerateBatchClient
from .._patch import BatchSharedKeyAuthPolicy
from azure.core.credentials import TokenCredential


from azure.core.credentials import AzureNamedKeyCredential


from typing import Union

__all__ = [
    "BatchClient",
]  # Add all objects you want publicly available to users at this package level


class BatchClient(GenerateBatchClient):
    """BatchClient.

    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param hub: Target hub name, which should start with alphabetic characters and only contain
     alpha-numeric characters or underscore.
    :type hub: str
    :param credentials: Credential needed for the client to connect to Azure.
    :type credentials: ~azure.identity.ClientSecretCredential, ~azure.core.credentials.AzureNamedKeyCredential,
     or ~azure.identity.TokenCredentials
    :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: Union[AzureNamedKeyCredential, TokenCredential], **kwargs):
        super().__init__(
            endpoint=endpoint,
            credential=credential, # type: ignore
            authentication_policy=kwargs.pop("authentication_policy", self._format_shared_key_credential(credential)),
            **kwargs
        )

    def _format_shared_key_credential(self, credential):
        if isinstance(credential, AzureNamedKeyCredential):
            return BatchSharedKeyAuthPolicy(credential)
        return None


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
