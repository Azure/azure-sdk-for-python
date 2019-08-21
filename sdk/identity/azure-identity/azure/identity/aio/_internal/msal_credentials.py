# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async credentials wrapping MSAL ClientApplications, delegating token acquisition and caching to them.

This entails monkeypatching MSAL's OAuth client with an adapter substituting an (async) azure-core pipeline for
Requests. Wrapping MSAL in async code and replacing its (synchronous) transport with an async pipeline is complicated
because MSAL has no async support.

This is what happens when a new token is required to service a ``get_token`` call:
  1. The credential submits the appropriate MSAL token acquisition method to an Executor, receiving a future.
  2. The credential awaits the future's completion, freeing the caller's event loop until the MSAL method returns.
  3. MSAL calls into the transport adapter in whatever context the Executor provided (a non-main thread by default).
  4. The adapter schedules an async pipeline run on the ``get_token`` caller's loop, and blocks on the result.
  5. The adapter wraps the pipeline response in the shape MSAL expects (requests.Response) and returns it.
  6. The MSAL token acquisition method returns; the future obtained in step 1 completes.
  7. The credential packages the future's result as an AccessToken and returns it to the caller.

The upshot is, this looks like an ordinary ``get_token`` coroutine to whomever holds the credential. The async
transport looks like an ordinary Requests session to MSAL.
"""

import abc
import asyncio
import functools
import time
from typing import TYPE_CHECKING
from unittest import mock

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Dict, Optional, Type, Union
    from concurrent.futures import Executor

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
import msal

from .msal_transport_adapter import AsyncMsalTransportAdapter


class MsalCredential(abc.ABC):
    """Base class for async credentials wrapping MSAL applications"""

    def __init__(
        self, client_id: str, authority: str, client_credential: "Optional[Union[str, Dict[str,str]]]", **kwargs: "Any"
    ) -> None:
        self._authority = authority
        self._client_credential = client_credential
        self._client_id = client_id

        self._lock = asyncio.Lock()
        self._adapter = kwargs.pop("msal_adapter", None) or AsyncMsalTransportAdapter(**kwargs)

        # postpone creating the wrapped application because its initializer uses the network
        self._msal_app = None  # type: Optional[msal.ClientApplication]

    @abc.abstractmethod
    def get_token(self, *scopes: str) -> AccessToken:
        pass

    @abc.abstractmethod
    def _get_app(self) -> msal.ClientApplication:
        pass

    async def _create_app(
        self, cls: "Type[msal.ClientApplication]", executor: "Optional[Executor]" = None
    ) -> msal.ClientApplication:
        """Creates an MSAL application, patching msal.authority to use an azure-core pipeline during tenant discovery"""

        if self._msal_app:
            return self._msal_app

        initializer = functools.partial(
            cls,
            client_id=self._client_id,
            client_credential=self._client_credential,
            authority=self._authority,
            validate_authority=False,
        )

        loop = asyncio.get_event_loop()

        # patch msal.authority so the MSAL app's init's network requests are received by the adapter
        with mock.patch("msal.authority.requests", self._adapter) as adapter:
            # We want the adapter to schedule transport on the event loop executing this method, so we need to pass
            # the loop to the adapter. No argument passed to the MSAL app's init is passed through to the transport.
            # So, we reluctantly use an instance attribute on the adapter. This should be safe because this method
            # is called only from _get_app, and therefore within an asyncio Lock.
            adapter.loop = loop
            app = await loop.run_in_executor(executor, initializer)

        # replace the client's requests.Session with adapter
        app.client.session = self._adapter

        return app


class ConfidentialClientCredential(MsalCredential):
    """Wraps an MSAL ConfidentialClientApplication with the TokenCredential API"""

    async def get_token(self, *scopes: str, executor: "Optional[Executor]" = None):
        """Get a token from the wrapped MSAL application"""

        # MSAL requires scopes be a list
        scopes = list(scopes)  # type: ignore
        now = int(time.time())

        # try to get a cached access token or if a refresh token is cached, redeem it for an access token
        try:
            app = await self._get_app(executor)
            # TODO: if we have a refresh token, acquire_token_silent will use the network
            result = app.acquire_token_silent(scopes, account=None)
            if not result:  # cache miss -> acquire new token
                # Provide the loop executing this code to the adapter so the adapter can schedule transport on it.
                # This relies on MSAL passing kwargs from its user-facing API to its transport layer.
                loop = asyncio.get_event_loop()
                acquire_token = functools.partial(app.acquire_token_for_client, scopes=scopes, loop=loop)
                result = await loop.run_in_executor(executor, acquire_token)
        except Exception as ex:
            raise ClientAuthenticationError(message=str(ex)) from ex

        if "access_token" not in result:
            raise ClientAuthenticationError(
                message="authentication failed: '{}'".format(result.get("error_description"))
            )

        return AccessToken(result["access_token"], now + int(result["expires_in"]))

    async def _get_app(self, executor: "Optional[Executor]" = None) -> msal.ConfidentialClientApplication:
        if not self._msal_app:
            async with self._lock:
                self._msal_app = await self._create_app(msal.ConfidentialClientApplication, executor)
        return self._msal_app
