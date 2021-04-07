# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
import time
from typing import TYPE_CHECKING

from azure.core.pipeline.policies import AsyncHTTPPolicy, SansIOHTTPPolicy
from azure.core.pipeline.policies._authentication import _BearerTokenCredentialPolicyBase, _enforce_https

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.credentials import AccessToken
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline import PipelineRequest, PipelineResponse


class AsyncBearerTokenCredentialPolicy(_BearerTokenCredentialPolicyBase, SansIOHTTPPolicy):
    # pylint:disable=too-few-public-methods
    """Adds a bearer token Authorization header to requests.

    :param credential: The credential.
    :type credential: ~azure.core.credentials.TokenCredential
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self, credential, *scopes, **kwargs):
        super().__init__(credential, *scopes, **kwargs)
        self._lock = asyncio.Lock()

    async def on_request(self, request: "PipelineRequest"):  # pylint:disable=invalid-overridden-method
        """Adds a bearer token Authorization header to request and sends request to next policy.

        :param request: The pipeline request object to be modified.
        :type request: ~azure.core.pipeline.PipelineRequest
        :raises: :class:`~azure.core.exceptions.ServiceRequestError`
        """
        self._enforce_https(request)

        async with self._lock:
            if self._need_new_token:
                self._token = await self._credential.get_token(*self._scopes)  # type: ignore
        self._update_headers(request.http_request.headers, self._token.token)


class AsyncChallengeAuthenticationPolicy(AsyncHTTPPolicy):
    """Base class for policies that authorize requests with bearer tokens and expect authentication challenges

    :param ~azure.core.credentials.AsyncTokenCredential credential: an object which can asynchronously provide access
        tokens, such as a credential from :mod:`azure.identity.aio`
    :param str scopes: required authentication scopes
    """

    def __init__(self, credential: "AsyncTokenCredential", *scopes: str, **kwargs: "Any") -> None:
        # pylint:disable=unused-argument
        super().__init__()
        self._credential = credential
        self._lock = asyncio.Lock()
        self._scopes = scopes
        self._token = None  # type: Optional[AccessToken]

    def _need_new_token(self) -> bool:
        return not self._token or self._token.expires_on - time.time() < 300

    async def on_request(self, request: "PipelineRequest") -> None:
        """Called before the policy sends a request.

        The base implementation authorizes the request with a bearer token.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        """

        if self._token is None or self._need_new_token():
            async with self._lock:
                # double check because another coroutine may have acquired a token while we waited to acquire the lock
                if not self._token or self._need_new_token():
                    self._token = await self._credential.get_token(*self._scopes)

        request.http_request.headers["Authorization"] = "Bearer " + self._token.token

    async def authorize_request(self, request: "PipelineRequest", *scopes: str, **kwargs: "Any") -> None:
        """Acquire a token from the credential and authorize the request with it.

        Keyword arguments are passed to the credential's get_token method. The token will be cached and used to
        authorize future requests.

        :param ~azure.core.pipeline.PipelineRequest request: the request
        :param str scopes: required scopes of authentication
        """

        async with self._lock:
            self._token = await self._credential.get_token(*scopes, **kwargs)
        request.http_request.headers["Authorization"] = "Bearer " + self._token.token

    async def send(self, request: "PipelineRequest") -> "PipelineResponse":
        """Authorizes a request with a bearer token, possibly handling an authentication challenge

        :param ~azure.core.pipeline.PipelineRequest request: The request
        """
        _enforce_https(request)

        await self.on_request(request)

        response = await self.next.send(request)

        if response.http_response.status_code == 401:
            self._token = None  # any cached token is invalid
            if "WWW-Authenticate" in response.http_response.headers:
                request_authorized = await self.on_challenge(request, response)
                if request_authorized:
                    response = await self.next.send(request)

        return response

    async def on_challenge(self, request: "PipelineRequest", response: "PipelineResponse") -> bool:
        """Authorize request according to an authentication challenge

        This method is called when the resource provider responds 401 with a WWW-Authenticate header.

        :param ~azure.core.pipeline.PipelineRequest request: the request which elicited an authentication challenge
        :param ~azure.core.pipeline.PipelineResponse response: the resource provider's response
        :returns: a bool indicating whether the policy should send the request
        """
        # pylint:disable=unused-argument,no-self-use
        return False
