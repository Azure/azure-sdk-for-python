# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Optional
import time

import msal
from azure.core.credentials import AccessToken

from .msal_client import MsalClient
from .._internal import _scopes_to_resource
from .._exceptions import CredentialUnavailableError


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

    def get_token(self, *scopes: str, **kwargs: Any) -> Optional[AccessToken]:
        if not scopes:
            raise ValueError('"get_token" requires at least one scope')
        resource = _scopes_to_resource(*scopes)
        result = self._msal_client.acquire_token_for_client(resource)
        now = int(time.time())
        if result and "access_token" in result and "expires_in" in result:
            return AccessToken(result["access_token"], now + int(result["expires_in"]))
        error_message = self.get_unavailable_message()
        raise CredentialUnavailableError(error_message)

    def get_managed_identity(self, **kwargs: Any) -> msal.ManagedIdentity:
        if "client_id" in kwargs and kwargs["client_id"]:
            return msal.UserAssignedManagedIdentity(client_id=kwargs["client_id"])
        identity_config = kwargs.pop("identity_config", None) or {}
        if "client_id" in identity_config and identity_config["client_id"]:
            return msal.UserAssignedManagedIdentity(client_id=identity_config["client_id"])
        if "resource_id" in identity_config and identity_config["resource_id"]:
            return msal.UserAssignedManagedIdentity(resource_id=identity_config["resource_id"])
        if "object_id" in identity_config and identity_config["object_id"]:
            return msal.UserAssignedManagedIdentity(object_id=identity_config["object_id"])
        return msal.SystemAssignedManagedIdentity()
