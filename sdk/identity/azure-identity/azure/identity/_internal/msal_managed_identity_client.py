# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Union, Dict

import msal

from .msal_client import MsalClient
from .._internal import _scopes_to_resource


class MsalManagedIdentityClient:  # pylint: disable=too-many-instance-attributes
    """Base class for managed identity client wrapping MSAL ManagedIdentityClient.

    :param managed_identity: the managed identity instance
    :type managed_identity: msal.ManagedIdentity
    """

    def __init__(
        self,
        managed_identity: msal.ManagedIdentity,
        **kwargs: Any
    ) -> None:
        self._client = MsalClient(**kwargs)
        self._msal_client = msal.ManagedIdentityClient(managed_identity, http_client=self._client)

    def __enter__(self) -> "MsalManagedIdentityClient":
        self._client.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self._client.__exit__(*args)

    def close(self) -> None:
        self.__exit__()

    def get_token(self, *scopes: str, **kwargs: Any) -> Dict[str, Any]:
        resource = _scopes_to_resource(*scopes)
        return self._msal_client.acquire_token_for_client(resource)

    def get_managed_identity(self, **kwargs: Any) -> msal.ManagedIdentity:
        if "client_id" in kwargs:
            return msal.UserAssignedManagedIdentity(client_id=kwargs["client_id"])
        identity_config = kwargs.pop("identity_config", None) or {}
        if "client_id" in identity_config:
            return msal.UserAssignedManagedIdentity(client_id=identity_config["client_id"])
        if "resource_id" in identity_config:
            return msal.UserAssignedManagedIdentity(resource_id=identity_config["resource_id"])
        if "object_id" in identity_config:
            return msal.UserAssignedManagedIdentity(object_id=identity_config["object_id"])
        return msal.SystemAssignedManagedIdentity()
