# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Union, Any
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential, TokenCredential
from ._generated import GeolocationClient as _GeolocationClient
from ._version import API_VERSION

# To check the credential is either AzureKeyCredential or TokenCredential
def _authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(
            name="subscription-key", credential=credential
        )
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError(
            "Unsupported credential: {}. Use an instance of AzureKeyCredential "
            "or a token credential from azure.identity".format(type(credential))
        )
    return authentication_policy

class MapsGeolocationClientBase:
    def __init__(
        self,
        credential: Union[AzureKeyCredential, TokenCredential],
        **kwargs: Any
    ) -> None:
        self._maps_client = _GeolocationClient(
            credential=credential,  # type: ignore
            api_version=kwargs.pop("api_version", API_VERSION),
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            **kwargs
        )
        self._geolocation_client = self._maps_client.geolocation

    def __enter__(self):
        self._maps_client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        self._maps_client.__exit__(*args)  # pylint:disable=no-member
