# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
# pylint: disable=unused-import
from typing import Union, Any, List

from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from ._client import MapsWeatherClient as MapsWeatherClientGenerated

__all__: List[str] = ["MapsWeatherClient"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


# To check the credential is either AzureKeyCredential or TokenCredential
def _authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(name="subscription-key", credential=credential)
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError(
            "Unsupported credential: {}. Use an instance of AzureKeyCredential "
            "or a token credential from azure.identity".format(type(credential))
        )
    return authentication_policy


# pylint: disable=C4748
class MapsWeatherClient(MapsWeatherClientGenerated):
    def __init__(self, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:

        super().__init__(
            credential=credential,  # type: ignore
            endpoint=kwargs.pop("endpoint", "https://atlas.microsoft.com"),
            client_id=kwargs.pop("client_id", None),
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            **kwargs
        )
