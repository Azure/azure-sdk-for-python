# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Any, MutableMapping, TypeVar, cast

from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.transport import HttpRequest as LegacyHttpRequest
from azure.core.rest import HttpRequest
from azure.core.credentials import AccessToken

from ..http_constants import HttpHeaders

HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)


class AsyncCosmosBearerTokenCredentialPolicy(AsyncBearerTokenCredentialPolicy):

    @staticmethod
    def _update_headers(headers: MutableMapping[str, str], token: str) -> None:
        """Updates the Authorization header with the bearer token.

        :param MutableMapping[str, str] headers: The HTTP Request headers
        :param str token: The OAuth token.
        """
        headers[HttpHeaders.Authorization] = f"type=aad&ver=1.0&sig={token}"

    async def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        """Adds a bearer token Authorization header to request and sends request to next policy.

        :param request: The pipeline request object to be modified.
        :type request: ~azure.core.pipeline.PipelineRequest
        :raises: :class:`~azure.core.exceptions.ServiceRequestError`
        """
        await super().on_request(request)
        # The None-check for self._token is done in the parent on_request
        self._update_headers(request.http_request.headers, cast(AccessToken, self._token).token)

    async def authorize_request(self, request: PipelineRequest[HTTPRequestType], *scopes: str, **kwargs: Any) -> None:
        """Acquire a token from the credential and authorize the request with it.

        Keyword arguments are passed to the credential's get_token method. The token will be cached and used to
        authorize future requests.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        :param str scopes: required scopes of authentication
        """
        await super().authorize_request(request, *scopes, **kwargs)
        # The None-check for self._token is done in the parent authorize_request
        self._update_headers(request.http_request.headers, cast(AccessToken, self._token).token)
