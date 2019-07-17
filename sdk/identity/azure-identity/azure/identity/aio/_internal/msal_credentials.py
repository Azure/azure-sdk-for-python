# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""An async credential which wraps an MSAL ConfidentialClientApplication and delegates token acquisition and caching to
it. This entails monkeypatching MSAL's OAuth client with an adapter substituting an azure-core pipeline for Requests.
Wrapping MSAL in async code and replacing its (synchronous) transport with an async pipeline is complicated because
MSAL has no async support.

This is what happens when a new token is required to service a get_token call:
  1. The credential submits the appropriate MSAL token acquisition method to an Executor, receiving a future.
  2. The credential awaits the future's completion, freeing the caller's event loop until the MSAL method returns.
  3. MSAL calls into the transport adapter in whatever context the Executor provided (a non-main thread by default).
  4. The adapter schedules an async pipeline run on the get_token caller's loop, and blocks on the result.
  5. The adapter wraps the pipeline response in the shape MSAL expects (requests.Response) and returns it.
  6. The MSAL token acquisition method returns; the future obtained in step 1 completes.
  7. The credential packages the future's result as an AccessToken and returns it to the caller.

The upshot is, this looks like an ordinary get_token coroutine to whomever holds the credential. The async transport
looks like an ordinary Requests session to MSAL.
"""

import asyncio
import functools
import time
from typing import TYPE_CHECKING
from unittest import mock

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Dict, Optional, Union
    from concurrent.futures import Executor

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
import msal

from .msal_transport_adapter import AsyncMsalTransportAdapter


class MsalCredential:
    """Base class for async credentials wrapping MSAL applications"""

    def __init__(
        self,
        client_id: str,
        authority: str,
        app_class: msal.ClientApplication,
        client_credential: "Optional[Union[str, Dict[str,str]]]",
        **kwargs: "Any"
    ):
        super().__init__(**kwargs)

        self._authority = authority
        self._client_id = client_id
        self._client_credential = client_credential

        self._lock = asyncio.Lock()
        self._adapter = kwargs.pop("msal_adapter", None) or AsyncMsalTransportAdapter(**kwargs)

        # postpone creating the wrapped application because its initializer uses the network
        self._app_class = app_class
        self._msal_app = None  # type: Optional[msal.ClientApplication]

    async def _app(self, executor: "Optional[Executor]" = None) -> msal.ClientApplication:
        if not self._msal_app:
            async with self._lock:
                # TODO: double-check?
                await self._create_msal_app(executor)
        return self._msal_app

    async def _create_msal_app(self, executor: "Optional[Executor]" = None) -> msal.ClientApplication:
        if self._msal_app:
            return self._msal_app

        self._adapter.loop = asyncio.get_event_loop()
        initializer = functools.partial(
            self._app_class,
            client_id=self._client_id,
            client_credential=self._client_credential,
            authority=self._authority,
        )

        # application initializers use msal.authority to send requests to AAD
        with mock.patch("msal.authority.requests", self._adapter):
            self._msal_app = await self._adapter.loop.run_in_executor(executor, initializer)

        # replace the client's requests.Session with adapter
        self._msal_app.client.session = self._adapter


class ConfidentialClientCredential(MsalCredential):
    """Wraps an MSAL ConfidentialClientApplication with the TokenCredential API"""

    def __init__(self, **kwargs: "Any") -> None:
        super().__init__(app_class=msal.ConfidentialClientApplication, **kwargs)

    async def get_token(self, *scopes: str, executor: "Optional[Executor]" = None):
        """Get a token from the wrapped MSAL application"""

        scopes = list(scopes)
        now = int(time.time())

        # try to get a cached access token or if a refresh token is cached, redeem it for an access token
        try:
            app = await self._app(executor)
            # TODO: if we have a refresh token, acquire_token_silent will use the network
            result = app.acquire_token_silent(scopes, account=None)
            if not result:
                # cache miss -> acquire new token
                self._adapter.loop = asyncio.get_event_loop()
                acquire_token = functools.partial(app.acquire_token_for_client, scopes=scopes)
                result = await self._adapter.loop.run_in_executor(executor, acquire_token)
        except Exception as ex:
            raise ClientAuthenticationError(message=str(ex))

        if "access_token" not in result:
            raise ClientAuthenticationError(
                message="authentication failed: '{}'".format(result.get("error_description"))
            )

        return AccessToken(result["access_token"], now + int(result["expires_in"]))
