# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
# pylint: disable=unused-import,ungrouped-imports, R0904, C0302
from typing import Union, Any, MutableMapping, List

from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from ._client import MapsSearchClient as MapsSearchClientGenerated

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

__all__: List[str] = ["MapsSearchClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

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


# pylint: disable=C4748
class MapsSearchClient(MapsSearchClientGenerated):

    def __init__(
        self,
        credential: Union[AzureKeyCredential, TokenCredential],
        *,
        endpoint: Optional[str] = None,
        client_id: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            credential=credential,  # type: ignore
            endpoint=kwargs.pop("endpoint", "https://atlas.microsoft.com"),
            api_version=kwargs.pop("api_version", "2023-06-01"),
            client_id=kwargs.pop("client_id", None),
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            **kwargs
        )
