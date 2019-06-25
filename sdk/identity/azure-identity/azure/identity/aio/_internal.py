# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# ------------------------------------------------------------------------
import os
from typing import Any, Optional

from azure.core import Configuration
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.core.pipeline.policies import ContentDecodePolicy, HeadersPolicy, NetworkTraceLoggingPolicy, AsyncRetryPolicy

from ._authn_client import AsyncAuthnClient
from ..constants import Endpoints, EnvironmentVariables
from .._internal import _ManagedIdentityBase


class _AsyncManagedIdentityBase(_ManagedIdentityBase):
    def __init__(self, endpoint: str, config: Optional[Configuration] = None, **kwargs: Any) -> None:
        super().__init__(endpoint=endpoint, config=config, client_cls=AsyncAuthnClient, **kwargs)

    @staticmethod
    def create_config(**kwargs: Any) -> Configuration:  # type: ignore
        """
        Build a default configuration for the credential's HTTP pipeline.

        :rtype: :class:`azure.core.configuration`
        """
        return _ManagedIdentityBase.create_config(retry_policy=AsyncRetryPolicy, **kwargs)


class ImdsCredential(_AsyncManagedIdentityBase):
    """
    Asynchronously authenticates with a managed identity via the IMDS endpoint.

    :param config: optional configuration for the underlying HTTP pipeline
    :type config: :class:`azure.core.configuration`
    """

    def __init__(self, config: Optional[Configuration] = None, **kwargs: Any) -> None:
        super().__init__(endpoint=Endpoints.IMDS, config=config, **kwargs)
        self._endpoint_available = None  # type: Optional[bool]

    async def get_token(self, *scopes: str) -> AccessToken:
        """
        Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        if self._endpoint_available is None:
            # Lacking another way to determine whether the IMDS endpoint is listening,
            # we send a request it would immediately reject (missing a required header),
            # setting a short timeout.
            try:
                await self._client.request_token(scopes, method="GET", connection_timeout=0.3, retry_total=0)
                self._endpoint_available = True
            except (ClientAuthenticationError, HttpResponseError):
                # received a response a pipeline policy choked on (HttpResponseError)
                # or that couldn't be deserialized by AuthnClient (AuthenticationError)
                self._endpoint_available = True
            except Exception:  # pylint:disable=broad-except
                # if anything else was raised, assume the endpoint is unavailable
                self._endpoint_available = False

        if not self._endpoint_available:
            raise ClientAuthenticationError(message="IMDS endpoint unavailable")

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
    """
    Authenticates via the MSI endpoint in an App Service or Cloud Shell environment.

    :param config: optional configuration for the underlying HTTP pipeline
    :type config: :class:`azure.core.configuration`
    """

    def __init__(self, config: Optional[Configuration] = None, **kwargs: Any) -> None:
        endpoint = os.environ.get(EnvironmentVariables.MSI_ENDPOINT)
        self._endpoint_available = endpoint is not None
        if self._endpoint_available:
            super().__init__(endpoint=endpoint, config=config, **kwargs)  # type: ignore

    async def get_token(self, *scopes: str) -> AccessToken:
        """
        Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        if not self._endpoint_available:
            raise ClientAuthenticationError(message="MSI endpoint unavailable")

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
            params["client_id"] = self._client_id
        return await self._client.request_token(scopes, method="GET", headers={"secret": secret}, params=params)

    async def _request_legacy_token(self, scopes, resource):
        form_data = {"resource": resource}
        if self._client_id:
            form_data["client_id"] = self._client_id
        return await self._client.request_token(scopes, method="POST", form_data=form_data)
