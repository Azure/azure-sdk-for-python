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
    def _get_client_session(self, **kwargs):
        return MsalTransportAdapter(**kwargs)

    @wrap_exceptions
    async def _obtain_token(self, scopes: "Iterable[str]", fn: "Callable", **kwargs: "Any") -> "AccessToken":
        now = int(time.time())
        executor = kwargs.get("executor", None)
        loop = kwargs.get("loop", None) or asyncio.get_event_loop()
        response = await loop.run_in_executor(executor, fn)
        return self._process_response(response=response, scopes=scopes, now=now)
