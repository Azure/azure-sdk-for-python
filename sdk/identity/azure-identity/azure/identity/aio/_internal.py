# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# ------------------------------------------------------------------------
import os
from typing import Any, Optional

from azure.core import Configuration
from azure.core.credentials import AccessToken
from azure.core.pipeline.policies import ContentDecodePolicy, HeadersPolicy, NetworkTraceLoggingPolicy, AsyncRetryPolicy

from ._authn_client import AsyncAuthnClient
from ..constants import Endpoints, MSI_ENDPOINT, MSI_SECRET
from ..exceptions import AuthenticationError
from .._internal import _ManagedIdentityBase


class _AsyncManagedIdentityBase(_ManagedIdentityBase):
    def __init__(self, endpoint: str, config: Optional[Configuration] = None, **kwargs: Any) -> None:
        super().__init__(endpoint=endpoint, config=config, client_cls=AsyncAuthnClient, **kwargs)

    @staticmethod
    def create_config(**kwargs: Any) -> Configuration:  # type: ignore
        return _ManagedIdentityBase.create_config(retry_policy=AsyncRetryPolicy, **kwargs)


class AsyncImdsCredential(_AsyncManagedIdentityBase):
    def __init__(self, config: Optional[Configuration] = None, **kwargs: Any) -> None:
        super().__init__(endpoint=Endpoints.IMDS, config=config, **kwargs)
        self._endpoint_available = None  # type: Optional[bool]

    async def get_token(self, *scopes: str) -> AccessToken:
        if self._endpoint_available is None:
            # Lacking another way to determine whether the IMDS endpoint is listening,
            # we send a request it would immediately reject (missing header, wrong verb),
            # setting a short timeout. The timeout was chosen by benchmarking: of 2000
            # requests, the slowest was 14ms, 99th percentile was 7ms, mean was 3.7ms.
            try:
                await self._client.request_token(scopes, connection_timeout=0.17)
                self._endpoint_available = True
            except AuthenticationError:
                # received a response that couldn't be deserialized (because it was an error response)
                self._endpoint_available = True
            except Exception:  # pylint:disable=broad-except
                self._endpoint_available = False

        if not self._endpoint_available:
            raise AuthenticationError("IMDS endpoint unavailable")

        if len(scopes) != 1:
            raise ValueError("this credential supports one scope per request")

        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[: -len("/.default")]
            token = await self._client.request_token(
                scopes, method="GET", params={"api-version": "2018-02-01", "resource": resource}
            )
        return token


class AsyncMsiCredential(_AsyncManagedIdentityBase):
    def __init__(self, config: Optional[Configuration] = None, **kwargs: Any) -> None:
        endpoint = os.environ.get(MSI_ENDPOINT)
        self._endpoint_available = endpoint is not None
        if self._endpoint_available:
            super(AsyncMsiCredential, self).__init__(endpoint=endpoint, config=config, **kwargs)  # type: ignore

    async def get_token(self, *scopes: str) -> AccessToken:
        if not self._endpoint_available:
            raise AuthenticationError("MSI endpoint unavailable")

        if len(scopes) != 1:
            raise ValueError("this credential supports only one scope per request")

        token = self._client.get_cached_token(scopes)
        if not token:
            resource = scopes[0]
            if resource.endswith("/.default"):
                resource = resource[: -len("/.default")]

            # TODO: support user-assigned client id
            secret = os.environ.get(MSI_SECRET)
            if secret:
                # MSI_ENDPOINT and MSI_SECRET set -> app service
                token = await self._client.request_token(
                    scopes,
                    method="GET",
                    headers={"secret": secret},
                    params={"api-version": "2017-09-01", "resource": resource},
                )
            else:
                # only MSI_ENDPOINT set -> legacy-style MSI (Cloud Shell)
                token = await self._client.request_token(
                    scopes, method="POST", form_data={"resource": resource}, headers={"Metadata": "true"}
                )
        return token
