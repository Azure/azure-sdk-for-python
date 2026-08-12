# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Thin connection context for explicit Voice event sends."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio

from starlette.websockets import WebSocket

from azure.ai.agentserver.core import experimental

from ._codec import encode_outbound_message
from ._models import OutboundVoiceMessage


@experimental
class Session:
    """Send-only context for one accepted Voice WebSocket connection.

    ``Session`` does not retain protocol or application lifecycle state. Agent
    code owns response IDs, pending work, generation tasks, terminal-event
    correlation, cancellation, history, and reconnect restoration.

    Instances are created by :class:`VoiceAgentServerHost` and supplied to
    registered callbacks.
    """

    __slots__ = ("_send_lock", "_websocket")
    _send_lock: asyncio.Lock
    _websocket: WebSocket

    def __init__(self) -> None:
        raise TypeError("Session instances are created by VoiceAgentServerHost")

    @classmethod
    def _create(cls, websocket: WebSocket) -> "Session":
        instance = object.__new__(cls)
        instance._websocket = websocket
        instance._send_lock = asyncio.Lock()
        return instance

    async def send(self, message: OutboundVoiceMessage) -> None:
        """Encode and send one explicit agent-to-Bridge event.

        Concurrent calls are serialized at the WebSocket write boundary. The
        method does not retry, infer commitment, or update protocol state.

        :param message: One immutable selected outbound message.
        :type message: OutboundVoiceMessage
        """
        frame = encode_outbound_message(message)
        async with self._send_lock:
            await self._websocket.send_text(frame)
