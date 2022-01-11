# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING, Any

from azure.core.pipeline.policies import AsyncHTTPPolicy

from ._async_anonymous_exchange_client import AnonymousACRExchangeClient
from ._async_exchange_client import ACRExchangeClient
from .._helpers import _enforce_https

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.pipeline import PipelineRequest, PipelineResponse


class ContainerRegistryChallengePolicy(AsyncHTTPPolicy):
    """Authentication policy for ACR which accepts a challenge"""

    def __init__(self, credential: "AsyncTokenCredential", endpoint: str, **kwargs: Any) -> None:
        super().__init__()
        self._credential = credential
        if self._credential is None:
            self._exchange_client = AnonymousACRExchangeClient(endpoint)
        else:
            self._exchange_client = ACRExchangeClient(endpoint, self._credential, **kwargs)

    async def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Called before the policy sends a request.
        The base implementation authorizes the request with a bearer token.
        :param ~azure.core.pipeline.PipelineRequest request: the request
        """
        # Future caching implementation will be included here
        pass  # pylint: disable=unnecessary-pass

    async def send(self, request):
        # type: (PipelineRequest) -> PipelineResponse
        """Authorizes a request with a bearer token, possibly handling an authentication challenge
        :param ~azure.core.pipeline.PipelineRequest request: the request
        """
        _enforce_https(request)

        await self.on_request(request)

        response = await self.next.send(request)

        if response.http_response.status_code == 401:
            challenge = response.http_response.headers.get("WWW-Authenticate")
            if challenge and await self.on_challenge(request, response, challenge):
                response = await self.next.send(request)

        return response

    async def on_challenge(self, request, response, challenge):
        # type: (PipelineRequest, PipelineResponse, str) -> bool
        """Authorize request according to an authentication challenge
        This method is called when the resource provider responds 401 with a WWW-Authenticate header.
        :param ~azure.core.pipeline.PipelineRequest request: the request which elicited an authentication challenge
        :param ~azure.core.pipeline.PipelineResponse response: the resource provider's response
        :param str challenge: response's WWW-Authenticate header, unparsed. It may contain multiple challenges.
        :returns: a bool indicating whether the policy should send the request
        """
        # pylint:disable=unused-argument,no-self-use

        access_token = await self._exchange_client.get_acr_access_token(challenge)
        request.http_request.headers["Authorization"] = "Bearer " + access_token
        return access_token is not None

    async def __aenter__(self):
        await self._exchange_client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._exchange_client.__aexit__()
