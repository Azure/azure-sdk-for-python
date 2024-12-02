# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Union, Any
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, AzureSasCredentialPolicy
from azure.core.credentials import AzureKeyCredential, AzureSasCredential
from azure.core.credentials_async import AsyncTokenCredential
from .._generated.aio import GeolocationClient as _MapsGeolocationClient
from .._version import VERSION


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


class AsyncMapsGeolocationClientBase:
    def __init__(
            self,
            credential: Union[AzureKeyCredential, AzureSasCredential, AsyncTokenCredential],
            **kwargs: Any
    ) -> None:
        self._maps_client = _MapsGeolocationClient(
            credential=credential,  # type: ignore
            api_version=kwargs.pop("api_version", VERSION),
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            **kwargs
        )
        self._geolocation_client = self._maps_client.geolocation

    async def __aenter__(self):
        await self._maps_client.__aenter__()  # pylint:disable=no-member
        return self

    async def __aexit__(self, *args):
        return await self._maps_client.__aexit__(*args)  # pylint:disable=no-member
