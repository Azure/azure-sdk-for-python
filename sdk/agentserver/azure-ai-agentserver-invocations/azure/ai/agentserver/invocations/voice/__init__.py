# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Typed Voice Live Bridge Protocol host on the Invocations WebSocket transport."""

from ._host import VoiceAgentServerHost
from ._models import (
    BargeInEvent,
    HandoffFailedEvent,
    InputImagePart,
    InputTextPart,
    ResponseCancellationOutcome,
    ResponseTimeoutEvent,
    ResponseTimeouts,
    SessionEndEvent,
    SessionStartEvent,
    UserContentPart,
    UserMessageEvent,
    UserNoInputEvent,
    UserSpeechStartedEvent,
)
from ._protocol import (
    VoiceBridgeConnectionClosedError,
    VoiceBridgeProtocolError,
    VoiceProactiveResponseDroppedError,
)
from ._runtime import VoiceCancellationToken, VoiceResponse, VoiceSession, VoiceTextItem
from .._version import VERSION

__all__ = [
    "BargeInEvent",
    "HandoffFailedEvent",
    "InputImagePart",
    "InputTextPart",
    "ResponseCancellationOutcome",
    "ResponseTimeoutEvent",
    "ResponseTimeouts",
    "SessionEndEvent",
    "SessionStartEvent",
    "UserContentPart",
    "UserMessageEvent",
    "UserNoInputEvent",
    "UserSpeechStartedEvent",
    "VoiceAgentServerHost",
    "VoiceBridgeConnectionClosedError",
    "VoiceBridgeProtocolError",
    "VoiceCancellationToken",
    "VoiceProactiveResponseDroppedError",
    "VoiceResponse",
    "VoiceSession",
    "VoiceTextItem",
]
__version__ = VERSION
