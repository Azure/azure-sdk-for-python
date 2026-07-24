# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Optional

from ._client import VoiceAgentsClient as _GeneratedVoiceAgentsClient
from ._realtime import (
    AsyncRealtime,
    AsyncRealtimeConnection,
    AsyncRealtimeConnectionManager,
)


class VoiceAgentsClient(_GeneratedVoiceAgentsClient):
    """VoiceAgentsClient with an interface-only realtime namespace.

    Adds the :attr:`realtime` namespace on top of the generated HTTP client.
    Realtime connections are not yet available and ``connect()`` currently raises
    :class:`NotImplementedError`.
    """

    _realtime: Optional[AsyncRealtime] = None

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
