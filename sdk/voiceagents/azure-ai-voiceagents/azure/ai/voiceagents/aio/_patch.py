# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional, TYPE_CHECKING

import aiohttp

from ._client import VoiceAgentsClient as _GeneratedVoiceAgentsClient
from ._realtime import (
    AsyncRealtime,
    AsyncRealtimeConnection,
    AsyncRealtimeConnectionManager,
    ClientEvent,
    ConversationItem,
    ServerEvent,
)

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class VoiceAgentsClient(_GeneratedVoiceAgentsClient):  # pylint: disable=client-accepts-api-version-keyword
    """VoiceAgentsClient with a realtime streaming namespace.

    Adds the :attr:`realtime` namespace on top of the generated HTTP client, exposing
    ``connect(...)`` for realtime WebSocket sessions.
    """

    _realtime: Optional[AsyncRealtime] = None

    def __init__(
        self, endpoint: str, credential: "AsyncTokenCredential", *, api_version: Optional[str] = None, **kwargs: Any
    ) -> None:
        # Work around an azure-core/aiohttp limitation: azure-core disables
        # aiohttp's native decompression but only re-implements gzip/deflate,
        # while aiohttp advertises "br" by default. Supplying the session that
        # the default AioHttpTransport will adopt keeps Accept-Encoding limited
        # to encodings azure-core can actually decompress, without importing a
        # concrete transport type.
        if "transport" not in kwargs and "session" not in kwargs:
            kwargs["session"] = aiohttp.ClientSession(headers={"Accept-Encoding": "gzip, deflate"})
        if api_version is None:
            super().__init__(endpoint, credential, **kwargs)
        else:
            super().__init__(endpoint, credential, api_version=api_version, **kwargs)

    @property
    def realtime(self) -> AsyncRealtime:
        """Realtime streaming entry point.

        :return: The realtime namespace, exposing ``connect(...)``.
        :rtype: ~azure.ai.voiceagents.aio.AsyncRealtime
        """
        if self._realtime is None:
            self._realtime = AsyncRealtime(self)
        return self._realtime


__all__: list[str] = [
    "VoiceAgentsClient",
    "AsyncRealtime",
    "AsyncRealtimeConnection",
    "AsyncRealtimeConnectionManager",
    "ClientEvent",
    "ConversationItem",
    "ServerEvent",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
