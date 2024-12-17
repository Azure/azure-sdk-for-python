# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum
from typing import (
    Callable,
    cast,
    TYPE_CHECKING,
    Any,
    List,
    Optional,
    Dict,
    Union,
)
from typing_extensions import Protocol

from ._encode import encode_payload
from .utils import get_message_encoded_size
from .error import AMQPError
from .message import Header, Properties

if TYPE_CHECKING:
    from ..amqp._amqp_message import AmqpAnnotatedMessage, AmqpMessageProperties, AmqpMessageHeader
    from .message import Message
    from .error import ErrorCondition

    class Settler(Protocol):
        def settle_messages(
            self,
            delivery_id: Optional[int],
            delivery_tag: Optional[bytes],
            outcome: str,
            *,
            error: Optional[AMQPError] = None,
            **kwargs: Any
        ) -> None: ...


def _encode_property(value):
    try:
        return value.encode("UTF-8")
    except AttributeError:
        return value


class MessageState(Enum):
    WaitingToBeSent = 0
    WaitingForSendAck = 1
    SendComplete = 2
    SendFailed = 3
    ReceivedUnsettled = 4
    ReceivedSettled = 5

    def __eq__(self, __o: object) -> bool:
        try:
            return self.value == cast(Enum, __o).value
        except AttributeError:
            return super().__eq__(__o)


class MessageAlreadySettled(Exception):
    pass


DONE_STATES = (MessageState.SendComplete, MessageState.SendFailed)
RECEIVE_STATES = (MessageState.ReceivedSettled, MessageState.ReceivedUnsettled)
PENDING_STATES = (MessageState.WaitingForSendAck, MessageState.WaitingToBeSent)


class LegacyMessage(object):  # pylint: disable=too-many-instance-attributes
    def __init__(self, message: "AmqpAnnotatedMessage", *, to_outgoing_amqp_message: Callable, **kwargs: Any) -> None:
        self._message: "AmqpAnnotatedMessage" = message
        self.state: "MessageState" = MessageState.SendComplete
        self.idle_time: int = 0
        self.retries: int = 0
        self._settler: Optional["Settler"] = kwargs.pop("settler", None)
        self._encoding = kwargs.get("encoding")
        self.delivery_no: Optional[int] = kwargs.get("delivery_no")
        self.delivery_tag: Optional[bytes] = kwargs.get("delivery_tag") or None
        self.on_send_complete: Optional[Callable] = None
        self.properties: Optional[LegacyMessageProperties] = (
            LegacyMessageProperties(self._message.properties) if self._message.properties else None
        )
        self.application_properties: Optional[Dict[Union[str, bytes], Any]] = (
            self._message.application_properties
            if self._message.application_properties and any(self._message.application_properties)
            else None
        )
        self.annotations: Optional[Dict[Union[str, bytes], Any]] = (
            self._message.annotations if self._message.annotations and any(self._message.annotations) else None
        )
        self.header: Optional[LegacyMessageHeader] = (
            LegacyMessageHeader(self._message.header) if self._message.header else None
        )
        self.footer: Optional[Dict[Any, Any]] = self._message.footer
        self.delivery_annotations: Optional[Dict[Union[str, bytes], Any]] = self._message.delivery_annotations
        if self._settler:
            self.state = MessageState.ReceivedUnsettled
        elif self.delivery_no:
            self.state = MessageState.ReceivedSettled
        self._to_outgoing_amqp_message = to_outgoing_amqp_message

    def __str__(self) -> str:
        return str(self._message)

    def _can_settle_message(self):
        if self.state not in RECEIVE_STATES:
            raise TypeError("Only received messages can be settled.")
        if self.settled:
            return False
        return True

    @property
    def settled(self) -> bool:
        if self.state == MessageState.ReceivedUnsettled:
            return False
        return True

    def get_message_encoded_size(self) -> int:
        return get_message_encoded_size(self._to_outgoing_amqp_message(self._message))

    def encode_message(self) -> bytes:
        output = bytearray()
        # to maintain the same behavior as uamqp, app prop values will not be decoded
        if isinstance(self._message.application_properties, dict):
            self.application_properties = self._message.application_properties.copy()
        else:
            self.application_properties = None
        encode_payload(output, self._to_outgoing_amqp_message(self._message))
        return bytes(output)

    def get_data(self) -> Any:
        return self._message.body

    def gather(self) -> List["LegacyMessage"]:
        if self.state in RECEIVE_STATES:
            raise TypeError("Only new messages can be gathered.")
        if not self._message:
            raise ValueError("Message data already consumed.")
        if self.state in DONE_STATES:
            raise MessageAlreadySettled()
        return [self]

    def get_message(self) -> "Message":
        return self._to_outgoing_amqp_message(self._message)

    def accept(self) -> bool:
        if self._can_settle_message() and self._settler:
            self._settler.settle_messages(self.delivery_no, self.delivery_tag, "accepted")
            self.state = MessageState.ReceivedSettled
            return True
        return False

    def reject(
        self,
        condition: Optional[Union[bytes, "ErrorCondition"]] = None,
        description: Optional[str] = None,
        info: Optional[Dict[Any, Any]] = None,
    ) -> bool:
        if self._can_settle_message() and self._settler:
            self._settler.settle_messages(
                self.delivery_no,
                self.delivery_tag,
                "rejected",
                error=AMQPError(condition=condition, description=description, info=info),
            )
            self.state = MessageState.ReceivedSettled
            return True
        return False

    def release(self) -> bool:
        if self._can_settle_message() and self._settler:
            self._settler.settle_messages(self.delivery_no, self.delivery_tag, "released")
            self.state = MessageState.ReceivedSettled
            return True
        return False

    def modify(
        self, failed: bool, deliverable: bool, annotations: Optional[Dict[Union[str, bytes], Any]] = None
    ) -> bool:
        if self._can_settle_message() and self._settler:
            self._settler.settle_messages(
                self.delivery_no,
                self.delivery_tag,
                "modified",
                delivery_failed=failed,
                undeliverable_here=deliverable,
                message_annotations=annotations,
            )
            self.state = MessageState.ReceivedSettled
            return True
        return False


class LegacyBatchMessage(LegacyMessage):
    batch_format = 0x80013700
    max_message_length = 1024 * 1024
    size_offset = 0


class LegacyMessageProperties(object):  # pylint: disable=too-many-instance-attributes
    def __init__(self, properties: "AmqpMessageProperties"):
        self.message_id: Optional[bytes] = _encode_property(properties.message_id)
        self.user_id: Optional[bytes] = _encode_property(properties.user_id)
        self.to: Optional[bytes] = _encode_property(properties.to)
        self.subject: Optional[bytes] = _encode_property(properties.subject)
        self.reply_to: Optional[bytes] = _encode_property(properties.reply_to)
        self.correlation_id: Optional[bytes] = _encode_property(properties.correlation_id)
        self.content_type: Optional[bytes] = _encode_property(properties.content_type)
        self.content_encoding: Optional[bytes] = _encode_property(properties.content_encoding)
        self.absolute_expiry_time: Optional[int] = properties.absolute_expiry_time
        self.creation_time: Optional[int] = properties.creation_time
        self.group_id: Optional[bytes] = _encode_property(properties.group_id)
        self.group_sequence: Optional[int] = properties.group_sequence
        self.reply_to_group_id: Optional[bytes] = _encode_property(properties.reply_to_group_id)

    def __str__(self) -> str:
        return str(
            {
                "message_id": self.message_id,
                "user_id": self.user_id,
                "to": self.to,
                "subject": self.subject,
                "reply_to": self.reply_to,
                "correlation_id": self.correlation_id,
                "content_type": self.content_type,
                "content_encoding": self.content_encoding,
                "absolute_expiry_time": self.absolute_expiry_time,
                "creation_time": self.creation_time,
                "group_id": self.group_id,
                "group_sequence": self.group_sequence,
                "reply_to_group_id": self.reply_to_group_id,
            }
        )

    def get_properties_obj(self) -> Properties:
        return Properties(
            self.message_id,
            self.user_id,
            self.to,
            self.subject,
            self.reply_to,
            self.correlation_id,
            self.content_type,
            self.content_encoding,
            self.absolute_expiry_time,
            self.creation_time,
            self.group_id,
            self.group_sequence,
            self.reply_to_group_id,
        )


class LegacyMessageHeader(object):
    def __init__(self, header: "AmqpMessageHeader") -> None:
        self.delivery_count: int = header.delivery_count or 0
        self.time_to_live: Optional[int] = header.time_to_live
        self.first_acquirer: Optional[bool] = header.first_acquirer
        self.durable: Optional[bool] = header.durable
        self.priority: Optional[int] = header.priority

    def __str__(self) -> str:
        return str(
            {
                "delivery_count": self.delivery_count,
                "time_to_live": self.time_to_live,
                "first_acquirer": self.first_acquirer,
                "durable": self.durable,
                "priority": self.priority,
            }
        )

    def get_header_obj(self) -> Header:
        # TODO: uamqp returned object has property: `time_to_live`.
        # This Header has `ttl`.
        return Header(
            self.durable,
            self.priority,
            self.time_to_live,
            self.first_acquirer,
            self.delivery_count,
        )
