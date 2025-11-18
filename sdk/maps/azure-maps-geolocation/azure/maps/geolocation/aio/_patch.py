# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Union, Any, Optional
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, AzureSasCredentialPolicy
from azure.core.credentials import AzureKeyCredential, AzureSasCredential
from azure.core.credentials_async import AsyncTokenCredential
from ._client import MapsGeolocationClient as MapsGeolocationClientGenerated

def _authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(name="subscription-key", credential=credential)
    elif isinstance(credential, AzureSasCredential):
        authentication_policy = AzureSasCredentialPolicy(credential)
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError(
            "Unsupported credential: {}. Use an instance of AzureKeyCredential "
            "or AzureSasCredential or a token credential from azure.identity".format(type(credential))
        )
    return authentication_policy

class MapsGeolocationClient(MapsGeolocationClientGenerated):
    """Azure Maps Geolocation REST APIs.

    :param credential: Credential used to authenticate requests to the service. Is either a token
     credential type or a key credential type. Required.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential or
     ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.AzureSasCredential
    :param client_id: Indicates the account intended for use with the Microsoft Entra ID security
     model. This unique ID for the Azure Maps account can be obtained from the
     `Azure Maps management plane Account API </rest/api/maps-management/accounts>`_.
     For more information on using Microsoft Entra ID security in Azure Maps, see
     `Manage authentication in Azure
     Maps </azure/azure-maps/how-to-manage-authentication>`_. Default value is None.
    :type client_id: str
    :keyword api_version: The API version to use for this operation. Default value is "1.0". Note
     that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self, credential: Union["AsyncTokenCredential", AzureKeyCredential, AzureSasCredential], client_id: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            credential=credential,
            client_id=client_id,
            endpoint=kwargs.pop("endpoint", "https://atlas.microsoft.com"),
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            **kwargs
        )

__all__: list[str] = ["MapsGeolocationClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
