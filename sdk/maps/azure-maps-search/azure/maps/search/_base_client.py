# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import
from typing import Union, Any
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential, TokenCredential
from ._generated import SearchClient as _MapsSearchClient
from ._version import VERSION

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

class MapsSearchClientBase:
    def __init__(
        self,
        credential: Union[AzureKeyCredential, TokenCredential],
        **kwargs: Any
    ) -> None:

        self._maps_client = _MapsSearchClient(
            credential=credential,  # type: ignore
            api_version=kwargs.pop("api_version", VERSION),
            base_url=kwargs.pop("base_url", None),
            client_id=kwargs.pop("client_id", None),
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            **kwargs
        )
        self._search_client = self._maps_client.search

    def __enter__(self):
        self._maps_client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        self._maps_client.__exit__(*args)  # pylint:disable=no-member
