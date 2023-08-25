# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from typing_extensions import (
    AnyStr,
    Mapping,
    NotRequired,
    MutableSequence,
    Any,
    Literal,
    TypedDict,
    Protocol,
    Optional,
    runtime_checkable
)

from dataclasses import dataclass, field, MISSING

from ._types_v2 import AMQPTypes

class FieldMetadata(TypedDict):
    type: AMQPTypes
    multiple: NotRequired[bool]


@runtime_checkable
class Performative(Protocol):
    _code: int

try:
    dataclass_decorator = dataclass(order=True, slots=True, weakref_slot=True)
except TypeError:
    # slots not supported < Python 3.10
    dataclass_decorator = dataclass(order=True)


@dataclass_decorator
class BeginFrame:
    """BEGIN performative. Begin a Session on a channel."""

    remote_channel: Optional[int]  = field(default=MISSING, metadata=FieldMetadata(type=AMQPTypes.ushort))
    """The remote channel for this Session.
        If a Session is locally initiated, the remote-channel MUST NOT be set.
        When an endpoint responds to a remotely initiated Session, the remote-channel MUST be set to the channel on which
        the remote Session sent the begin."""
    next_outgoing_id: int = field(default=MISSING, metadata=FieldMetadata(type=AMQPTypes.uint))
    """The transfer-id of the first transfer id the sender will send.
        The next-outgoing-id is used to assign a unique transfer-id to all outgoing transfer frames on a given
        session. The next-outgoing-id may be initialized to an arbitrary value and is incremented after each
        successive transfer according to RFC-1982 serial number arithmetic."""
    incoming_window: int = field(default=MISSING, metadata=FieldMetadata(type=AMQPTypes.uint))
    """The initial incoming-window of the sender.
        The incoming-window defines the maximum number of incoming transfer frames that the endpoint can currently
        receive. This identifies a current maximum incoming transfer-id that can be computed by subtracting one
        from the sum of incoming-window and next-incoming-id."""
    outgoing_window: int = field(default=MISSING, metadata=FieldMetadata(type=AMQPTypes.uint))
    """The initial outgoing-window of the sender.
        The outgoing-window defines the maximum number of outgoing transfer frames that the endpoint can currently
        send. This identifies a current maximum outgoing transfer-id that can be computed by subtracting one from
        the sum of outgoing-window and next-outgoing-id."""
    handle_max: int = field(default=4294967295, metadata=FieldMetadata(type=AMQPTypes.uint))
    """The maximum handle value that may be used on the Session.
        The handle-max value is the highest handle value that may be used on the Session. A peer MUST NOT attempt
        to attach a Link using a handle value outside the range that its partner can handle. A peer that receives
        a handle outside the supported range MUST close the Connection with the framing-error error-code."""
    offered_capabilities: Optional[MutableSequence[AnyStr]] = field(default=None, metadata=FieldMetadata(type=AMQPTypes.symbol, multiple=True))
    """The extension capabilities the sender supports.
        A list of commonly defined session capabilities and their meanings can be found
        here: http://www.amqp.org/specification/1.0/session-capabilities."""
    desired_capabilities: Optional[MutableSequence[AnyStr]] = field(default=None, metadata=FieldMetadata(type=AMQPTypes.symbol, multiple=True))
    """The extension capabilities the sender may use if the receiver supports them."""
    properties: Optional[Mapping[AnyStr, Any]] = field(default=None, metadata=FieldMetadata(type=AMQPTypes.fields))
    """Session properties.
        The properties map contains a set of fields intended to indicate information about the session and its
        container. A list of commonly defined session properties and their meanings can be found
        here: http://www.amqp.org/specification/1.0/session-properties."""
    _code: Literal[0x00000011] = field(default=0x00000011, init=False, repr=False, hash=False)
