# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Any, Union
from azure.core.credentials import AzureKeyCredential, TokenCredential

from ._azure_app_configuration import AzureAppConfiguration as AzureAppConfigurationGenerated
from ._configuration import AzureAppConfigurationConfiguration as AzureAppConfigurationConfigurationGenerated


class AzureAppConfiguration(AzureAppConfigurationGenerated):
    """AzureAppConfiguration.

    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :param endpoint: The endpoint of the App Configuration instance to send requests to. Required.
    :type endpoint: str
    :param sync_token: Used to guarantee real-time consistency between requests. Default value is
     None.
    :type sync_token: str
    :keyword api_version: Api Version. Default value is "2023-11-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(
        self,
        credential: Union[TokenCredential, AzureKeyCredential],
        endpoint: str,
        sync_token: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(credential, endpoint, sync_token=sync_token, **kwargs)


class AzureAppConfigurationConfiguration(AzureAppConfigurationConfigurationGenerated):
    """Configuration for AzureAppConfiguration.

    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :param endpoint: The endpoint of the App Configuration instance to send requests to. Required.
    :type endpoint: str
    :param sync_token: Used to guarantee real-time consistency between requests. Default value is
     None.
    :type sync_token: str
    :keyword api_version: Api Version. Default value is "2023-11-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        credential: Union[TokenCredential, AzureKeyCredential],
        endpoint: str,
        sync_token: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(credential, endpoint, sync_token=sync_token, **kwargs)


__all__: List[str] = [
    "AzureAppConfiguration"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
