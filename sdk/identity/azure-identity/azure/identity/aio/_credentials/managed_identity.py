# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
import os
from typing import TYPE_CHECKING

from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import AsyncRetryPolicy

from azure.identity._credentials.managed_identity import _ManagedIdentityBase
from .base import AsyncCredentialBase
from .._authn_client import AsyncAuthnClient
from ... import CredentialUnavailableError
from ..._constants import Endpoints, EnvironmentVariables

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.configuration import Configuration


class ManagedIdentityCredential(object):
    """Authenticates with an Azure managed identity in any hosting environment which supports managed identities.

    See the Azure Active Directory documentation for more information about managed identities:
    https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview

    :keyword str client_id: ID of a user-assigned identity. Leave unspecified to use a system-assigned identity.
    """

    def __new__(cls, *args, **kwargs):
        if os.environ.get(EnvironmentVariables.MSI_ENDPOINT):
            return MsiCredential(*args, **kwargs)
        return ImdsCredential(*args, **kwargs)

    # the below methods are never called, because ManagedIdentityCredential can't be instantiated;
    # they exist so tooling gets accurate signatures for Imds- and MsiCredential
    def __init__(self, **kwargs: "Any") -> None:
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):
        pass

    async def close(self):
        """Close the credential's transport session."""

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":  # pylint:disable=unused-argument
        """Asynchronously request an access token for `scopes`.

        .. note:: This method is called by Azure SDK clients. It isn't intended for use in application code.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: managed identity isn't available in the hosting environment
        """
        return AccessToken()


class _AsyncManagedIdentityBase(_ManagedIdentityBase, AsyncCredentialBase):
    def __init__(self, endpoint: str, **kwargs: "Any") -> None:
        super().__init__(endpoint=endpoint, client_cls=AsyncAuthnClient, **kwargs)

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        await self._client.__aexit__()

    @abc.abstractmethod
    async def get_token(self, *scopes, **kwargs):
        pass

    @staticmethod
    def _create_config(**kwargs: "Any") -> "Configuration":
        """Build a default configuration for the credential's HTTP pipeline."""
        return _ManagedIdentityBase._create_config(retry_policy=AsyncRetryPolicy, **kwargs)


class ImdsCredential(_AsyncManagedIdentityBase):
    """Asynchronously authenticates with a managed identity via the IMDS endpoint.

    :keyword str client_id: ID of a user-assigned identity. Leave unspecified to use a system-assigned identity.
    """

    def __init__(self, **kwargs: "Any") -> None:
        super().__init__(endpoint=Endpoints.IMDS, **kwargs)
        self._endpoint_available = None  # type: Optional[bool]

    async def get_token(self, *scopes: str, **kwargs: "Any") -> AccessToken:  # pylint:disable=unused-argument
        """Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: the IMDS endpoint is unreachable
        """
        if self._endpoint_available is None:
            # Lacking another way to determine whether the IMDS endpoint is listening,
            # we send a request it would immediately reject (missing a required header),
            # setting a short timeout.
            try:
                await self._client.request_token(scopes, method="GET", connection_timeout=0.3, retry_total=0)
                self._endpoint_available = True
            except HttpResponseError:
                # received a response, choked on it
                self._endpoint_available = True
            except Exception:  # pylint:disable=broad-except
                # if anything else was raised, assume the endpoint is unavailable
                self._endpoint_available = False

        if not self._endpoint_available:
            raise CredentialUnavailableError(message="IMDS endpoint unavailable")

        if len(scopes) != 1:
            raise ValueError("this credential supports one scope per request")

        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[: -len("/.default")]
            params = {"api-version": "2018-02-01", "resource": resource}
            if self._client_id:
                params["client_id"] = self._client_id
            token = await self._client.request_token(scopes, method="GET", params=params)
        return token


class MsiCredential(_AsyncManagedIdentityBase):
    """Authenticates via the MSI endpoint in an App Service or Cloud Shell environment.

    :keyword str client_id: ID of a user-assigned identity. Leave unspecified to use a system-assigned identity.
    """

    def __init__(self, **kwargs: "Any") -> None:
        self._endpoint = os.environ.get(EnvironmentVariables.MSI_ENDPOINT)
        if self._endpoint:
            super().__init__(endpoint=self._endpoint, **kwargs)

    async def get_token(self, *scopes: str, **kwargs: "Any") -> AccessToken:  # pylint:disable=unused-argument
        """Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.identity.CredentialUnavailableError: the MSI endpoint is unavailable
        """
        if not self._endpoint:
            raise CredentialUnavailableError(message="MSI endpoint unavailable")

        if len(scopes) != 1:
            raise ValueError("this credential supports only one scope per request")

        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[: -len("/.default")]

            secret = os.environ.get(EnvironmentVariables.MSI_SECRET)
            if secret:
                # MSI_ENDPOINT and MSI_SECRET set -> App Service
                token = await self._request_app_service_token(scopes=scopes, resource=resource, secret=secret)
            else:
                # only MSI_ENDPOINT set -> legacy-style MSI (Cloud Shell)
                token = await self._request_legacy_token(scopes=scopes, resource=resource)
        return token

    async def _request_app_service_token(self, scopes, resource, secret):
        params = {"api-version": "2017-09-01", "resource": resource}
        if self._client_id:
            params["clientid"] = self._client_id
        return await self._client.request_token(scopes, method="GET", headers={"secret": secret}, params=params)

    async def _request_legacy_token(self, scopes, resource):
        form_data = {"resource": resource}
        if self._client_id:
            form_data["client_id"] = self._client_id
        return await self._client.request_token(scopes, method="POST", form_data=form_data)
