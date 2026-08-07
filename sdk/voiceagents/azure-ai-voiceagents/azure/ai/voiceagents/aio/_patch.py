# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional, TYPE_CHECKING

from ._client import VoiceAgentsClient as _GeneratedVoiceAgentsClient
from ._realtime import AsyncRealtime, AsyncRealtimeConnection, AsyncRealtimeConnectionManager

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
        # Work around an azure-core/aiohttp limitation: azure-core's AioHttpTransport
        # disables aiohttp's native response decompression and only re-implements
        # gzip/deflate itself (no brotli support), while aiohttp advertises
        # "Accept-Encoding: br" by default. If the service responds with a
        # brotli-compressed body, azure-core fails to decode it. Unless the caller
        # already supplied their own transport or session, default to only
        # advertising the encodings azure-core can actually decompress.
        if "transport" not in kwargs and "session" not in kwargs:
            try:
                import aiohttp
                import azure.core.pipeline.transport as transport_module

                kwargs["transport"] = transport_module.AioHttpTransport(
                    session=aiohttp.ClientSession(auto_decompress=False, headers={"Accept-Encoding": "gzip, deflate"})
                )
            except ImportError:
                pass
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
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
