# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Immutable messages for the Voice Live Bridge text/control profile."""

from __future__ import annotations

import datetime
import math
import reprlib
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import MISSING, dataclass, field, fields
from enum import Enum
from types import MappingProxyType
from typing import Any, ClassVar, Literal

from azure.core import CaseInsensitiveEnumMeta

from azure.ai.agentserver.core import experimental


@experimental
def new_message_id() -> str:
    """Create one stateless Bridge message identifier.

    :return: A new ``m_`` identifier.
    :rtype: str
    """
    return f"m_{uuid.uuid4().hex}"


@experimental
def new_response_id() -> str:
    """Create one stateless agent response identifier.

    :return: A new ``r_`` identifier.
    :rtype: str
    """
    return f"r_{uuid.uuid4().hex}"


@experimental
def new_item_id() -> str:
    """Create one stateless agent output-item identifier.

    :return: A new ``it_`` identifier.
    :rtype: str
    """
    return f"it_{uuid.uuid4().hex}"


def new_timestamp() -> str:
    """Create one UTC RFC 3339 timestamp with millisecond precision.

    :return: The current UTC timestamp.
    :rtype: str
    """
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


_MAX_MODEL_REPR_LENGTH = 1024
_REDACTED_REPR = "<redacted>"
_SAFE_REPR_FIELDS = frozenset(
    {
        "admission_timeout_ms",
        "code",
        "count",
        "first_output_ms",
        "id",
        "idle_ms",
        "in_reply_to",
        "item_id",
        "item_ids",
        "max_duration_ms",
        "mode",
        "no_input_timeout_ms",
        "protocol_version",
        "reconnect",
        "response_id",
        "response_timeouts",
        "retriable",
        "stage",
        "ts",
        "type",
    }
)
_MODEL_REPR = reprlib.Repr()
_MODEL_REPR.maxstring = 128
_MODEL_REPR.maxother = 128


def _voice_model_repr(self: Any) -> str:
    """Return a bounded representation that redacts payload fields by default.

    :return: The safe representation of the Voice model.
    :rtype: str
    """
    values = []
    for model_field in fields(self):
        value = getattr(self, model_field.name)
        if model_field.name not in _SAFE_REPR_FIELDS and value is not None:
            value_repr = _REDACTED_REPR
        else:
            value_repr = _MODEL_REPR.repr(value)
        values.append(f"{model_field.name}={value_repr}")

    rendered = f"{type(self).__name__}({', '.join(values)})"
    if len(rendered) <= _MAX_MODEL_REPR_LENGTH:
        return rendered
    return f"{rendered[:_MAX_MODEL_REPR_LENGTH - 4]}...)"


def _freeze_json(value: Any, name: str, *, require_finite_numbers: bool = False) -> Any:
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise TypeError(f"{name} keys must be strings")
        return MappingProxyType(
            {
                key: _freeze_json(item, name, require_finite_numbers=require_finite_numbers)
                for key, item in value.items()
            }
        )
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(_freeze_json(item, name, require_finite_numbers=require_finite_numbers) for item in value)
    if require_finite_numbers and isinstance(value, float) and not math.isfinite(value):
        raise TypeError(f"{name} must contain only finite numbers")
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError(f"{name} must contain only JSON-compatible values")


def _document_dataclass_defaults(*model_types: type[Any]) -> None:
    """Attach accurate defaults to generated dataclass constructor docs.

    :param model_types: Voice dataclass types whose generated constructors need documentation.
    :type model_types: type
    """
    for model_type in model_types:
        default_lines = []
        for model_field in fields(model_type):
            if not model_field.init:
                continue
            if model_field.default_factory is not MISSING:
                default_value = "..."
            elif model_field.default is MISSING:
                continue
            elif model_field.default is None:
                default_value = "None"
            else:
                default_value = "..."
            default_lines.append(f":param {model_field.name}: Default value is {default_value}.")
        if default_lines:
            model_type.__init__.__doc__ = "\n".join(default_lines) + "\n\n"


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class ResponseTimeouts:
    """Response deadlines selected by the Bridge.

    :ivar first_output_ms: Maximum milliseconds until first output.
    :vartype first_output_ms: int
    :ivar idle_ms: Maximum milliseconds between output progress messages.
    :vartype idle_ms: int
    :ivar max_duration_ms: Absolute maximum response duration in milliseconds.
    :vartype max_duration_ms: int
    """

    first_output_ms: int
    idle_ms: int
    max_duration_ms: int
    __repr__ = _voice_model_repr


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class InputTextPart:
    """One text part from an ordered ``user.message``.

    :ivar text: Final recognized or application-supplied text.
    :vartype text: str
    :ivar type: Content-part discriminator. Always ``"input_text"``.
    :vartype type: str
    """

    text: str
    type: Literal["input_text"] = field(default="input_text", init=False)
    __repr__ = _voice_model_repr


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class SessionDisconnected:
    """Local transport-disconnect event.

    This event is not a Bridge wire message. It lets application code release
    connection-scoped work after the peer or proxy closes the WebSocket.

    :ivar code: RFC 6455 close code reported by the transport.
    :vartype code: int
    :ivar reason: Optional close reason reported by the transport.
    :vartype reason: str or None
    """

    code: int
    reason: str | None = None
    __repr__ = _voice_model_repr


@dataclass(frozen=True, kw_only=True, repr=False)
class _InboundMessage:
    """Common fields received from the Bridge."""

    id: str
    ts: str
    type: ClassVar[str]
    __repr__ = _voice_model_repr


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class SessionStart(_InboundMessage):
    """Bridge application-start event.

    :ivar id: Wire message identifier.
    :vartype id: str
    :ivar ts: Sender timestamp.
    :vartype ts: str
    :ivar protocol_version: Exact Bridge protocol version.
    :vartype protocol_version: str
    :ivar reconnect: Whether this transport reattaches the logical session.
    :vartype reconnect: bool
    :ivar response_timeouts: Effective response deadlines.
    :vartype response_timeouts: ResponseTimeouts
    :ivar greeting: Optional Bridge-owned greeting.
    :vartype greeting: str or None
    :ivar no_input_timeout_ms: Optional user-silence threshold.
    :vartype no_input_timeout_ms: int or None
    :ivar caller: Optional immutable caller context.
    :vartype caller: Mapping[str, Any] or None
    """

    type: ClassVar[str] = "session.start"
    protocol_version: str
    reconnect: bool
    response_timeouts: ResponseTimeouts
    greeting: str | None = None
    no_input_timeout_ms: int | None = None
    caller: Mapping[str, Any] | None = None

    def __init__(
        self,
        *,
        id: str,
        ts: str,
        protocol_version: str,
        reconnect: bool,
        response_timeouts: ResponseTimeouts,
        greeting: str | None = None,
        no_input_timeout_ms: int | None = None,
        caller: Mapping[str, Any] | None = None,
    ) -> None:
        if caller is not None:
            if not isinstance(caller, Mapping):
                raise TypeError("caller must be a mapping")
            caller = _freeze_json(caller, "caller", require_finite_numbers=True)
        _InboundMessage.__init__(self, id=id, ts=ts)
        object.__setattr__(self, "protocol_version", protocol_version)
        object.__setattr__(self, "reconnect", reconnect)
        object.__setattr__(self, "response_timeouts", response_timeouts)
        object.__setattr__(self, "greeting", greeting)
        object.__setattr__(self, "no_input_timeout_ms", no_input_timeout_ms)
        object.__setattr__(self, "caller", caller)


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class UserMessage(_InboundMessage):
    """Completed user text turn.

    :ivar id: Wire message identifier.
    :vartype id: str
    :ivar ts: Sender timestamp.
    :vartype ts: str
    :ivar item_id: Bridge-allocated input item identifier.
    :vartype item_id: str
    :ivar content: Supported text parts in wire order.
    :vartype content: tuple[InputTextPart, ...]
    """

    type: ClassVar[str] = "user.message"
    item_id: str
    content: tuple[InputTextPart, ...]


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class UserNoInput(_InboundMessage):
    """Bridge-generated user-silence turn.

    :ivar id: Wire message identifier.
    :vartype id: str
    :ivar ts: Sender timestamp.
    :vartype ts: str
    :ivar item_id: Bridge-allocated input item identifier.
    :vartype item_id: str
    :ivar count: Consecutive no-input count.
    :vartype count: int
    """

    type: ClassVar[str] = "user.no_input"
    item_id: str
    count: int


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class UserSpeechStarted(_InboundMessage):
    """Advisory signal that caller speech began while no response was open.

    :ivar id: Wire message identifier.
    :vartype id: str
    :ivar ts: Sender timestamp.
    :vartype ts: str
    """

    type: ClassVar[str] = "user.speech_started"


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class BargeIn(_InboundMessage):
    """Caller interruption and playback snapshot.

    :ivar id: Wire message identifier.
    :vartype id: str
    :ivar ts: Sender timestamp.
    :vartype ts: str
    :ivar response_id: Interrupted response identifier.
    :vartype response_id: str
    :ivar heard_text: Text played before the interruption.
    :vartype heard_text: str
    :ivar item_id: Output item playing at the interruption, if any.
    :vartype item_id: str or None
    """

    type: ClassVar[str] = "barge_in"
    response_id: str
    heard_text: str
    item_id: str | None = None


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class ResponseAccepted(_InboundMessage):
    """Bridge acceptance of a proactive response admission request.

    :ivar id: Wire message identifier.
    :vartype id: str
    :ivar ts: Sender timestamp.
    :vartype ts: str
    :ivar response_id: Accepted proactive response identifier.
    :vartype response_id: str
    """

    type: ClassVar[str] = "response.accepted"
    response_id: str


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class ResponseDropped(_InboundMessage):
    """Bridge rejection or expiry of a proactive response request.

    :ivar id: Wire message identifier.
    :vartype id: str
    :ivar ts: Sender timestamp.
    :vartype ts: str
    :ivar response_id: Dropped proactive response identifier.
    :vartype response_id: str
    :ivar reason: Open-enum drop reason supplied by the Bridge.
    :vartype reason: str
    """

    type: ClassVar[str] = "response.dropped"
    response_id: str
    reason: str


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class ResponseCancelled(_InboundMessage):
    """Winning self-cancel playback outcome from the Bridge.

    :ivar id: Wire message identifier.
    :vartype id: str
    :ivar ts: Sender timestamp.
    :vartype ts: str
    :ivar response_id: Cancelled response identifier.
    :vartype response_id: str
    :ivar heard_text: Text played before cancellation completed.
    :vartype heard_text: str
    :ivar item_id: Output item playing at cancellation, if any.
    :vartype item_id: str or None
    """

    type: ClassVar[str] = "response.cancelled"
    response_id: str
    heard_text: str
    item_id: str | None = None


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class ResponseTimeout(_InboundMessage):
    """Bridge response or pending-input timeout event.

    :ivar id: Wire message identifier.
    :vartype id: str
    :ivar ts: Sender timestamp.
    :vartype ts: str
    :ivar stage: Open-enum timeout stage.
    :vartype stage: str
    :ivar response_id: Timed-out response identifier, when a response was open.
    :vartype response_id: str or None
    :ivar item_ids: Timed-out input identifiers before response creation.
    :vartype item_ids: tuple[str, ...] or None
    """

    type: ClassVar[str] = "response.timeout"
    stage: str
    response_id: str | None = None
    item_ids: tuple[str, ...] | None = None


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class SessionEnd(_InboundMessage):
    """Bridge-initiated session termination event.

    :ivar id: Wire message identifier.
    :vartype id: str
    :ivar ts: Sender timestamp.
    :vartype ts: str
    :ivar reason: Open-enum session termination reason.
    :vartype reason: str
    """

    type: ClassVar[str] = "session.end"
    reason: str


InboundVoiceMessage = (
    SessionStart
    | UserMessage
    | UserNoInput
    | UserSpeechStarted
    | BargeIn
    | ResponseAccepted
    | ResponseDropped
    | ResponseCancelled
    | ResponseTimeout
    | SessionEnd
)


@dataclass(frozen=True, kw_only=True, repr=False)
class _OutboundMessage:
    """Common fields generated independently for each outbound message."""

    id: str = field(default_factory=new_message_id)
    ts: str = field(default_factory=new_timestamp)
    type: ClassVar[str]
    __repr__ = _voice_model_repr


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class SessionReady(_OutboundMessage):
    """Explicit positive application-readiness acknowledgement.

    :ivar id: Generated wire message identifier.
    :vartype id: str
    :ivar ts: Generated sender timestamp.
    :vartype ts: str
    """

    type: ClassVar[str] = "session.ready"


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class SessionRejected(_OutboundMessage):
    """Explicit negative application-readiness acknowledgement.

    :ivar id: Generated wire message identifier.
    :vartype id: str
    :ivar ts: Generated sender timestamp.
    :vartype ts: str
    :ivar code: Open-enum rejection code.
    :vartype code: str
    :ivar retriable: Whether the Bridge may retry activation.
    :vartype retriable: bool
    :ivar message: Optional sanitized diagnostic detail.
    :vartype message: str or None
    """

    type: ClassVar[str] = "session.rejected"
    code: str
    retriable: bool
    message: str | None = None


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class ResponseCreated(_OutboundMessage):
    """Open a reply response or request proactive admission.

    :ivar id: Generated wire message identifier.
    :vartype id: str
    :ivar ts: Generated sender timestamp.
    :vartype ts: str
    :ivar response_id: Agent-allocated response identifier.
    :vartype response_id: str
    :ivar in_reply_to: Ordered input prefix for a reply, or None for proactive admission.
    :vartype in_reply_to: tuple[str, ...] or None
    :ivar admission_timeout_ms: Optional proactive admission timeout.
    :vartype admission_timeout_ms: int or None
    :ivar supersede_key: Optional proactive supersession key.
    :vartype supersede_key: str or None
    """

    type: ClassVar[str] = "response.created"
    response_id: str
    in_reply_to: tuple[str, ...] | None = None
    admission_timeout_ms: int | None = None
    supersede_key: str | None = None


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class ResponseNone(_OutboundMessage):
    """Explicitly decline an ordered input prefix.

    :ivar id: Generated wire message identifier.
    :vartype id: str
    :ivar ts: Generated sender timestamp.
    :vartype ts: str
    :ivar in_reply_to: Non-empty ordered input prefix being declined.
    :vartype in_reply_to: tuple[str, ...]
    :ivar reason: Optional open-enum decline reason.
    :vartype reason: str or None
    """

    type: ClassVar[str] = "response.none"
    in_reply_to: tuple[str, ...]
    reason: str | None = None


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class ResponseOutputTextDelta(_OutboundMessage):
    """One streaming text increment for an output item.

    :ivar id: Generated wire message identifier.
    :vartype id: str
    :ivar ts: Generated sender timestamp.
    :vartype ts: str
    :ivar response_id: Owning response identifier.
    :vartype response_id: str
    :ivar item_id: Output item identifier.
    :vartype item_id: str
    :ivar delta: Non-empty text increment.
    :vartype delta: str
    :ivar voice: Optional immutable Voice Live synthesis merge patch.
    :vartype voice: Mapping[str, Any] or None
    """

    type: ClassVar[str] = "response.output_text.delta"
    response_id: str
    item_id: str
    delta: str
    voice: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.voice is not None:
            object.__setattr__(self, "voice", _freeze_json(self.voice, "voice"))


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class ResponseOutputTextDone(_OutboundMessage):
    """Complete one streamed or non-streamed output item.

    :ivar id: Generated wire message identifier.
    :vartype id: str
    :ivar ts: Generated sender timestamp.
    :vartype ts: str
    :ivar response_id: Owning response identifier.
    :vartype response_id: str
    :ivar item_id: Output item identifier.
    :vartype item_id: str
    :ivar text: Complete output item text.
    :vartype text: str
    :ivar voice: Optional immutable Voice Live synthesis merge patch.
    :vartype voice: Mapping[str, Any] or None
    """

    type: ClassVar[str] = "response.output_text.done"
    response_id: str
    item_id: str
    text: str
    voice: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.voice is not None:
            object.__setattr__(self, "voice", _freeze_json(self.voice, "voice"))


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class ResponseDone(_OutboundMessage):
    """Explicit normal response-level terminator.

    :ivar id: Generated wire message identifier.
    :vartype id: str
    :ivar ts: Generated sender timestamp.
    :vartype ts: str
    :ivar response_id: Completed response identifier.
    :vartype response_id: str
    """

    type: ClassVar[str] = "response.done"
    response_id: str


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class ResponseCancel(_OutboundMessage):
    """Request cancellation of an open or pending proactive response.

    :ivar id: Generated wire message identifier.
    :vartype id: str
    :ivar ts: Generated sender timestamp.
    :vartype ts: str
    :ivar response_id: Response or pending proactive request to cancel.
    :vartype response_id: str
    :ivar reason: Optional open-enum cancellation reason.
    :vartype reason: str or None
    """

    type: ClassVar[str] = "response.cancel"
    response_id: str
    reason: str | None = None


@experimental
class EndCallMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Closed call-ending mode."""

    DRAIN = "drain"
    IMMEDIATE = "immediate"


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class EndCall(_OutboundMessage):
    """Ask the Bridge to end the call.

    :ivar id: Generated wire message identifier.
    :vartype id: str
    :ivar ts: Generated sender timestamp.
    :vartype ts: str
    :ivar reason: Non-empty call-ending reason.
    :vartype reason: str
    :ivar mode: Closed call-ending mode.
    :vartype mode: EndCallMode
    """

    type: ClassVar[str] = "end_call"
    reason: str
    mode: EndCallMode = EndCallMode.DRAIN


@experimental
@dataclass(frozen=True, kw_only=True, repr=False)
class AgentError(_OutboundMessage):
    """Report an explicit response- or session-scoped agent failure.

    :ivar id: Generated wire message identifier.
    :vartype id: str
    :ivar ts: Generated sender timestamp.
    :vartype ts: str
    :ivar code: Open-enum agent error code.
    :vartype code: str
    :ivar message: Sanitized diagnostic detail.
    :vartype message: str
    :ivar response_id: Related response identifier, when response-scoped.
    :vartype response_id: str or None
    :ivar item_id: Related output item identifier, when available.
    :vartype item_id: str or None
    """

    type: ClassVar[str] = "error"
    code: str
    message: str
    response_id: str | None = None
    item_id: str | None = None


_document_dataclass_defaults(
    ResponseTimeouts,
    InputTextPart,
    SessionDisconnected,
    SessionStart,
    UserMessage,
    UserNoInput,
    UserSpeechStarted,
    BargeIn,
    ResponseAccepted,
    ResponseDropped,
    ResponseCancelled,
    ResponseTimeout,
    SessionEnd,
    SessionReady,
    SessionRejected,
    ResponseCreated,
    ResponseNone,
    ResponseOutputTextDelta,
    ResponseOutputTextDone,
    ResponseDone,
    ResponseCancel,
    EndCall,
    AgentError,
)


OutboundVoiceMessage = (
    SessionReady
    | SessionRejected
    | ResponseCreated
    | ResponseNone
    | ResponseOutputTextDelta
    | ResponseOutputTextDone
    | ResponseDone
    | ResponseCancel
    | EndCall
    | AgentError
)
