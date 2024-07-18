# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302
from typing import Union, Any, MutableMapping

from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.maps.search.aio import MapsSearchClient

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


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


class AzureMapsSearchClient(MapsSearchClient):

    def __init__(
        self,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        **kwargs: Any
    ) -> None:

        super().__init__(
            credential=credential,  # type: ignore
            endpoint=kwargs.pop("base_url", "https://atlas.microsoft.com"),
            client_id=kwargs.pop("client_id", None),
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            **kwargs
        )
