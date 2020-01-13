# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""A thin wrapper around MSAL's token cache and OAuth 2 client"""

import asyncio
import time
from typing import TYPE_CHECKING

from azure.identity._internal import AadClientBase
from .msal_transport_adapter import MsalTransportAdapter
from .exception_wrapper import wrap_exceptions

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Iterable
    from azure.core.credentials import AccessToken


class AadClient(AadClientBase):
    async def __aenter__(self):
        await self._client.session.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self) -> None:
        """Close the client's transport session."""

        await self._client.session.__aexit__()

    # pylint:disable=arguments-differ
    def obtain_token_by_authorization_code(
        self, *args: "Any", loop: "asyncio.AbstractEventLoop" = None, **kwargs: "Any"
    ) -> "AccessToken":
        # 'loop' will reach the transport adapter as a kwarg, so here we ensure it's passed
        loop = loop or asyncio.get_event_loop()
        return super().obtain_token_by_authorization_code(*args, loop=loop, **kwargs)

    def obtain_token_by_refresh_token(self, *args, loop: "asyncio.AbstractEventLoop" = None, **kwargs) -> "AccessToken":
        # 'loop' will reach the transport adapter as a kwarg, so here we ensure it's passed
        loop = loop or asyncio.get_event_loop()
        return super().obtain_token_by_refresh_token(*args, loop=loop, **kwargs)

    def _get_client_session(self, **kwargs):
        return MsalTransportAdapter(**kwargs)

    @wrap_exceptions
    async def _obtain_token(
        self, scopes: "Iterable[str]", fn: "Callable", loop: "asyncio.AbstractEventLoop", executor=None, **kwargs: "Any"
    ) -> "AccessToken":
        now = int(time.time())
        response = await loop.run_in_executor(executor, fn)
        return self._process_response(response=response, scopes=scopes, now=now)
