# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Public models for the typed Voice Live bridge host."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, Union


@dataclass(frozen=True)
class ResponseTimeouts:
    """Effective response deadlines advertised by the bridge.

    :param first_output_ms: Maximum time to first output or explicit decline.
    :param idle_ms: Maximum time between output progress messages.
    :param max_duration_ms: Absolute maximum response duration.
    """

    first_output_ms: int
    idle_ms: int
    max_duration_ms: int


@dataclass(frozen=True)
class InputTextPart:
    """One text part from an ordered ``user.message`` payload.

    :param text: Final recognized or application-supplied text.
    """

    text: str
    type: Literal["input_text"] = field(default="input_text", init=False)


@dataclass(frozen=True)
class InputImagePart:
    """One reference-only image part from ``user.message``.

    :param image_ref: Short-lived fetchable image reference.
    :param mime_type: Image media type.
    :param alt: Optional untrusted caller-provided caption.
    """

    image_ref: str
    mime_type: str
    alt: str | None = None
    type: Literal["input_image"] = field(default="input_image", init=False)


UserContentPart = Union[InputTextPart, InputImagePart]


@dataclass(frozen=True)
class ConversationHistoryItem:
    """One caller-app supplied user-role history item.

    :param item_id: Caller/bridge-allocated ``hi_`` identifier.
    :param content: Supported content parts in original order.
    """

    item_id: str
    content: tuple[UserContentPart, ...]
    role: Literal["user"] = field(default="user", init=False)


@dataclass(frozen=True)
class ConversationItemCreateEvent:
    """Non-response-producing history create request.

    :param request_id: Inbound envelope identifier used for result correlation.
    :param item: User-role history item to persist.
    :param previous_item_id: Insertion predecessor, ``root``, or ``None`` to append.
    """

    request_id: str
    item: ConversationHistoryItem
    previous_item_id: str | None = None


@dataclass(frozen=True)
class ConversationItemDeleteEvent:
    """Non-response-producing history delete request.

    :param request_id: Inbound envelope identifier used for result correlation.
    :param item_id: Existing history item to delete.
    """

    request_id: str
    item_id: str


@dataclass(frozen=True)
class SessionStartEvent:
    """Validated application-start event delivered before ``session.ready``.

    :param protocol_version: Exact accepted bridge protocol version.
    :param reconnect: Whether this transport reattaches the logical session.
    :param response_timeouts: Effective response deadlines.
    :param greeting: Optional bridge-owned greeting; absent on reconnect.
    :param no_input_timeout_ms: Optional user-silence threshold.
    :param caller: Deeply read-only, untrusted caller metadata.
    """

    protocol_version: str
    reconnect: bool
    response_timeouts: ResponseTimeouts
    greeting: str | None = None
    no_input_timeout_ms: int | None = None
    caller: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class UserMessageEvent:
    """Completed user turn with ordered content parts.

    :param item_id: Bridge-allocated ``in_`` input item identifier.
    :param content: Supported content parts in original wire order.
    """

    item_id: str
    content: tuple[UserContentPart, ...]

    @property
    def text(self) -> str:
        """Return all text parts joined with one space.

        :return: Convenience text projection preserving text-part order.
        :rtype: str
        """
        return " ".join(part.text for part in self.content if isinstance(part, InputTextPart))


@dataclass(frozen=True)
class UserNoInputEvent:
    """Bridge-generated silence turn.

    :param item_id: Bridge-allocated ``in_`` input item identifier.
    :param count: Consecutive no-input count.
    """

    item_id: str
    count: int


@dataclass(frozen=True)
class UserSpeechStartedEvent:
    """Advisory signal that caller speech began while no response was open."""


@dataclass(frozen=True)
class DtmfKeyEvent:
    """One raw session-scoped DTMF key.

    :param digit: Exactly one of ``0``–``9``, ``*``, or ``#``.
    """

    digit: str


@dataclass(frozen=True)
class DtmfCollectedEvent:
    """Completed DTMF collection delivered as a new response turn.

    :param item_id: Bridge-allocated ``in_`` input item identifier.
    :param collection_id: SDK-allocated ``dc_`` collection identifier.
    :param digits: Collected digits, excluding the terminator.
    :param completion_reason: Open-enum completion reason.
    """

    item_id: str
    collection_id: str
    digits: str
    completion_reason: str


@dataclass(frozen=True)
class DtmfCollectionRejectedEvent:
    """DTMF collection request that the bridge did not start.

    :param collection_id: Rejected ``dc_`` collection identifier.
    :param reason: Open-enum rejection reason.
    """

    collection_id: str
    reason: str


@dataclass(frozen=True)
class DtmfCollectionCancelledEvent:
    """Pending or active DTMF collection that ended without a result turn.

    :param collection_id: Cancelled ``dc_`` collection identifier.
    :param reason: Open-enum cancellation reason.
    """

    collection_id: str
    reason: str


@dataclass(frozen=True)
class HandoffFailedEvent:
    """Bridge-generated recovery turn after target activation failed.

    :param item_id: Bridge-allocated ``in_`` recovery item identifier.
    :param target: Same-project target agent name.
    :param code: Open-enum failure code.
    :param message: Optional sanitized diagnostic detail.
    """

    item_id: str
    target: str
    code: str
    message: str | None = None


@dataclass(frozen=True)
class BargeInEvent:
    """Caller interruption and playback outcome.

    :param response_id: Agent-owned response that was interrupted.
    :param heard_text: Approximate text played before the cut.
    :param item_id: Output item playing at the cut, when one existed.
    """

    response_id: str
    heard_text: str
    item_id: str | None = None


@dataclass(frozen=True)
class ResponseTimeoutEvent:
    """Terminal response-deadline notification.

    Exactly one of ``response_id`` and ``item_ids`` is populated.

    :param stage: Open-enum timeout stage.
    :param response_id: Open response terminated by the bridge.
    :param item_ids: Pending ordered input batch terminated before response open.
    """

    stage: str
    response_id: str | None = None
    item_ids: tuple[str, ...] | None = None


@dataclass(frozen=True)
class ResponseCancellationOutcome:
    """Winning playback outcome returned by ``VoiceResponse.cancel``.

    :param response_id: Response whose cancellation was requested.
    :param kind: Winning terminal, ``cancelled`` or caller ``barge_in``.
    :param heard_text: Approximate text played before the terminal.
    :param item_id: Output item playing at the terminal, when one existed.
    """

    response_id: str
    kind: Literal["cancelled", "barge_in"]
    heard_text: str
    item_id: str | None = None


@dataclass(frozen=True)
class SessionEndEvent:
    """Bridge-initiated session termination.

    :param reason: Open-enum termination reason.
    """

    reason: str
