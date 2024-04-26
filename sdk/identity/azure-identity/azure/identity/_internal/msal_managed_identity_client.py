# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Optional, Dict
import time

import msal
from azure.core.credentials import AccessToken

from .msal_client import MsalClient
from .._internal import _scopes_to_resource
from .._exceptions import CredentialUnavailableError


class MsalManagedIdentityClient:  # pylint: disable=too-many-instance-attributes
    """Base class for managed identity client wrapping MSAL ManagedIdentityClient.
    """

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self._settings = kwargs
        self._client = MsalClient(**kwargs)
        managed_identity = self.get_managed_identity(**kwargs)
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

    def get_managed_identity(self, **kwargs: Any):
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

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        # Remove the non-picklable entries
        del state["_msal_client"]
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)
        # Re-create the unpickable entries
        managed_identity = self.get_managed_identity(**self._settings)
        self._msal_client = msal.ManagedIdentityClient(managed_identity, http_client=self._client)