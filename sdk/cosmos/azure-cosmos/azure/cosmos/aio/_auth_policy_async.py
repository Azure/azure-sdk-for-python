# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio # pylint: disable=do-not-import-asyncio
import logging
from typing import Any, MutableMapping, TypeVar, cast, Optional, Union
from weakref import WeakKeyDictionary

from azure.core.credentials_async import AsyncTokenCredential, AsyncSupportsTokenInfo
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.transport import HttpRequest as LegacyHttpRequest
from azure.core.rest import HttpRequest
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError

from ..http_constants import HttpHeaders
from .._constants import _Constants as Constants

HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)
logger = logging.getLogger("azure.cosmos.AsyncCosmosBearerTokenCredentialPolicy")
_credential_locks: "WeakKeyDictionary[Union[AsyncTokenCredential, AsyncSupportsTokenInfo], asyncio.Lock]" = WeakKeyDictionary()

def _get_credential_lock(credential: Union[AsyncTokenCredential, AsyncSupportsTokenInfo]) -> asyncio.Lock:
    lock = _credential_locks.get(credential)
    if lock is None:
        lock = asyncio.Lock()
        _credential_locks[credential] = lock
    return lock

# NOTE: This class accesses protected members (_scopes, _token) of the parent class
# to implement fallback and scope-switching logic not exposed by the public API.
# Composition was considered, but still required accessing protected members, so inheritance is retained
# for seamless Azure SDK pipeline integration.
class AsyncCosmosBearerTokenCredentialPolicy(AsyncBearerTokenCredentialPolicy):
    AadDefaultScope = Constants.AAD_DEFAULT_SCOPE

    def __init__(self, credential: AsyncTokenCredential, account_scope: str, override_scope: Optional[str] = None):
        self._account_scope = account_scope
        self._override_scope = override_scope
        self._current_scope = override_scope or account_scope
        self._credential_lock = _get_credential_lock(credential)
        super().__init__(credential, self._current_scope)

    async def setup(self) -> None:
        # have to also support get_token info
        self._credential_lock = _get_credential_lock(self._credential)
        # initialize the cache by requesting a token for the current scope (thread-safe)
        async with self._credential_lock:
            try:
                await self._get_token()
            except Exception: #pylint: disable=broad-exception-caught
                logger.warning("Failed to acquire initial token for scope '%s'. Cache was not populated.",
                               self._current_scope, exc_info=True)


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
        tried_fallback = False
        while True:
            try:
                await super().on_request(request)
                # The None-check for self._token is done in the parent on_request
                self._update_headers(request.http_request.headers, cast(AccessToken, self._token).token)
                break
            except HttpResponseError as ex:
                # Only fallback if not using override, not already tried, and error is AADSTS500011
                if (
                        not self._override_scope and
                        not tried_fallback and
                        self._current_scope != self.AadDefaultScope and
                        "AADSTS500011" in str(ex)
                ):
                    logger.warning(
                        "Received AADSTS500011 error when using scope '%s'. Falling back to default scope '%s'.",
                        self._current_scope,
                        self.AadDefaultScope
                    )
                    self._scopes = (self.AadDefaultScope,)
                    self._current_scope = self.AadDefaultScope
                    tried_fallback = True
                    continue
                raise

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
