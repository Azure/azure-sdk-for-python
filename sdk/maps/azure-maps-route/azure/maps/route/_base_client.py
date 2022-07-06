# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Union, TYPE_CHECKING
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from ._generated import RouteClient as _RouteClient
from ._version import VERSION
if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

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

class RouteClientBase:
    def __init__(
        self,
        credential, #type: Union[AzureKeyCredential, TokenCredential]
        **kwargs #type Any
    ):
        # type: (...) -> None

        self._route_client = _RouteClient(
            credential=credential,  # type: ignore
            api_version=kwargs.pop("api_version", VERSION),
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            **kwargs
        ).route

    def __enter__(self):
        self._route_client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        self._route_client.__exit__(*args)  # pylint:disable=no-member