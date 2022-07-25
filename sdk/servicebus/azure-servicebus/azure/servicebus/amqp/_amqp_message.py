# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# from __future__ import annotations
import time
import uuid
from datetime import datetime
import warnings
from typing import Optional, Any, cast, Mapping, Union, Dict

from msrest.serialization import TZ_UTC
from .._pyamqp.message import Message, Header, Properties
from .._pyamqp.utils import normalized_data_body, normalized_sequence_body, amqp_long_value

from ._constants import AmqpMessageBodyType
from .._common.constants import (
    MAX_DURATION_VALUE,
    MAX_ABSOLUTE_EXPIRY_TIME,
    _X_OPT_SCHEDULED_ENQUEUE_TIME,
    _X_OPT_ENQUEUED_TIME,
    _X_OPT_LOCKED_UNTIL
)

_LONG_ANNOTATIONS = (
    _X_OPT_ENQUEUED_TIME,
    _X_OPT_SCHEDULED_ENQUEUE_TIME,
    _X_OPT_LOCKED_UNTIL
)


class DictMixin(object):
    def __setitem__(self, key, item):
        # type: (Any, Any) -> None
        self.__dict__[key] = item

    def __getitem__(self, key):
        # type: (Any) -> Any
        return self.__dict__[key]

    def __repr__(self):
        # type: () -> str
        return str(self)

    def __len__(self):
        # type: () -> int
        return len(self.keys())

    def __delitem__(self, key):
        # type: (Any) -> None
        self.__dict__[key] = None

    def __eq__(self, other):
        # type: (Any) -> bool
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        # type: (Any) -> bool
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        # type: () -> str
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})

    def has_key(self, k):
        # type: (Any) -> bool
        return k in self.__dict__

    def update(self, *args, **kwargs):
        # type: (Any, Any) -> None
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        # type: () -> list
        return [k for k in self.__dict__ if not k.startswith("_")]

    def values(self):
        # type: () -> list
        return [v for k, v in self.__dict__.items() if not k.startswith("_")]

    def items(self):
        # type: () -> list
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]

    def get(self, key, default=None):
        # type: (Any, Optional[Any]) -> Any
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class AmqpAnnotatedMessage(object):
    # pylint: disable=too-many-instance-attributes
    """
    The AMQP Annotated Message for advanced sending and receiving scenarios which allows you to
    access to low-level AMQP message sections. There should be one and only one of either data_body, sequence_body
    or value_body being set as the body of the AmqpAnnotatedMessage; if more than one body is set, `ValueError` will
    be raised.

    Please refer to the AMQP spec:
    http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-messaging-v1.0-os.html#section-message-format
    for more information on the message format.

    :keyword data_body: The body consists of one or more data sections and each section contains opaque binary data.
    :paramtype data_body: Union[str, bytes, List[Union[str, bytes]]]
    :keyword sequence_body: The body consists of one or more sequence sections and
     each section contains an arbitrary number of structured data elements.
    :paramtype sequence_body: List[Any]
    :keyword value_body: The body consists of one amqp-value section and the section contains a single AMQP value.
    :paramtype value_body: Any
    :keyword header: The amqp message header.
    :paramtype header: Optional[~azure.servicebus.amqp.AmqpMessageHeader]
    :keyword footer: The amqp message footer.
    :paramtype footer: Optional[Dict]
    :keyword properties: Properties to add to the amqp message.
    :paramtype properties: Optional[~azure.servicebus.amqp.AmqpMessageProperties]
    :keyword application_properties: Service specific application properties.
    :paramtype application_properties: Optional[Dict]
    :keyword annotations: Service specific message annotations.
    :paramtype annotations: Optional[Dict]
    :keyword delivery_annotations: Service specific delivery annotations.
    :paramtype delivery_annotations: Optional[Dict]
    """

    def __init__(
        self,
        *,
        header: Optional["AmqpMessageHeader"] = None,
        footer: Optional[Dict[str, Any]] = None,
        properties: Optional["AmqpMessageProperties"] = None,
        application_properties: Optional[Dict[str, Any]] = None,
        annotations: Optional[Dict[str, Any]] = None,
        delivery_annotations: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        self._message = kwargs.pop("message", None)
        self._encoding = kwargs.pop("encoding", "UTF-8")
        self._data_body = None
        self._sequence_body = None
        self._value_body = None
        self.body_type = None

        # internal usage only for service bus received message
        if self._message:
            self._from_amqp_message(self._message)
            return

        # manually constructed AMQPAnnotatedMessage
        input_count_validation = len([key for key in ("data_body", "sequence_body", "value_body") if key in kwargs])
        if input_count_validation != 1:
            raise ValueError(
                "There should be one and only one of either data_body, sequence_body "
                "or value_body being set as the body of the AmqpAnnotatedMessage."
            )

        if "data_body" in kwargs:
            self._data_body = normalized_data_body(kwargs.get("data_body"))
            self.body_type = AmqpMessageBodyType.DATA
        elif "sequence_body" in kwargs:
            self._sequence_body = normalized_sequence_body(kwargs.get("sequence_body"))
            self.body_type = AmqpMessageBodyType.SEQUENCE
        elif "value_body" in kwargs:
            self._value_body = kwargs.get("value_body")
            self.body_type = AmqpMessageBodyType.VALUE

        header_dict = cast(Mapping, header)
        self._header = AmqpMessageHeader(**header_dict) if header else None
        self._footer = footer
        properties_dict = cast(Mapping, properties)
        self._properties = AmqpMessageProperties(**properties_dict) if properties else None
        self._application_properties = application_properties
        self._annotations = annotations
        self._delivery_annotations = delivery_annotations

    def __str__(self) -> str:
        if self.body_type == AmqpMessageBodyType.DATA: # pylint:disable=no-else-return
            return "".join(d.decode(self._encoding) for d in self._data_body)
        elif self.body_type == AmqpMessageBodyType.SEQUENCE:
            return str(self._sequence_body)
        elif self.body_type == AmqpMessageBodyType.VALUE:
            return str(self._value_body)
        return ""

    def __repr__(self) -> str:
        # pylint: disable=bare-except
        message_repr = "body={}".format(
            str(self)
        )
        message_repr += ", body_type={}".format(self.body_type)
        try:
            message_repr += ", header={}".format(self.header)
        except:
            message_repr += ", header=<read-error>"
        try:
            message_repr += ", footer={}".format(self.footer)
        except:
            message_repr += ", footer=<read-error>"
        try:
            message_repr += ", properties={}".format(self.properties)
        except:
            message_repr += ", properties=<read-error>"
        try:
            message_repr += ", application_properties={}".format(self.application_properties)
        except:
            message_repr += ", application_properties=<read-error>"
        try:
            message_repr += ", delivery_annotations={}".format(self.delivery_annotations)
        except:
            message_repr += ", delivery_annotations=<read-error>"
        try:
            message_repr += ", annotations={}".format(self.annotations)
        except:
            message_repr += ", annotations=<read-error>"
        return "AmqpAnnotatedMessage({})".format(message_repr)[:1024]

    def _from_amqp_message(self, message):
        # populate the properties from an pyamqp message
        if message[5]:
            self.body_type = AmqpMessageBodyType.DATA
            self._data_body = message[5]
        elif message[6]:
            self.body_type = AmqpMessageBodyType.SEQUENCE
            self._sequence_body = message[6]
        else:
            self.body_type = AmqpMessageBodyType.VALUE
            self._value_body = message[7]

        self._properties = AmqpMessageProperties(
            message_id=message.properties.message_id,
            user_id=message.properties.user_id,
            to=message.properties.to,
            subject=message.properties.subject,
            reply_to=message.properties.reply_to,
            correlation_id=message.properties.correlation_id,
            content_type=message.properties.content_type,
            content_encoding=message.properties.content_encoding,
            absolute_expiry_time=message.properties.absolute_expiry_time,
            creation_time=message.properties.creation_time,
            group_id=message.properties.group_id,
            group_sequence=message.properties.group_sequence,
            reply_to_group_id=message.properties.reply_to_group_id,
        ) if message.properties else None
        self._header = AmqpMessageHeader(
            delivery_count=message.header.delivery_count,
            time_to_live=message.header.ttl,
            first_acquirer=message.header.first_acquirer,
            durable=message.header.durable,
            priority=message.header.priority
        ) if message.header else None
        self._footer = message.footer
        self._annotations = message.message_annotations
        self._delivery_annotations = message.delivery_annotations
        self._application_properties = message.application_properties

    def _to_outgoing_amqp_message(self):
        message_header = None
        ttl_set = False
        if self.header:
            message_header = Header(
                durable=self.header.durable,
                priority=self.header.priority,
                ttl=self.header.time_to_live,
                first_acquirer=self.header.first_acquirer,
                delivery_count=self.header.delivery_count
            )

            if self.header.time_to_live and self.header.time_to_live != MAX_DURATION_VALUE:
                ttl_set = True
                creation_time_from_ttl = int(time.mktime(datetime.now(TZ_UTC).timetuple()) * 1000)
                absolute_expiry_time_from_ttl = int(min(
                    MAX_ABSOLUTE_EXPIRY_TIME,
                    creation_time_from_ttl + self.header.time_to_live
                ))

        message_properties = None
        if self.properties:
            creation_time = None
            absolute_expiry_time = None
            if ttl_set:
                creation_time = creation_time_from_ttl
                absolute_expiry_time = absolute_expiry_time_from_ttl
            else:
                if self.properties.creation_time:
                    creation_time = int(self.properties.creation_time)
                if self.properties.absolute_expiry_time:
                    absolute_expiry_time = int(self.properties.absolute_expiry_time)

            message_properties = Properties(
                message_id=self.properties.message_id,
                user_id=self.properties.user_id,
                to=self.properties.to,
                subject=self.properties.subject,
                reply_to=self.properties.reply_to,
                correlation_id=self.properties.correlation_id,
                content_type=self.properties.content_type,
                content_encoding=self.properties.content_encoding,
                creation_time=creation_time,
                absolute_expiry_time=absolute_expiry_time,
                group_id=self.properties.group_id,
                group_sequence=self.properties.group_sequence,
                reply_to_group_id=self.properties.reply_to_group_id
            )
        elif ttl_set:
            message_properties = Properties(
                creation_time=creation_time_from_ttl if ttl_set else None,
                absolute_expiry_time=absolute_expiry_time_from_ttl if ttl_set else None,
            )
        annotations = None
        if self.annotations:
            # TODO: Investigate how we originally encoded annotations.
            annotations = dict(self.annotations)
            for key in _LONG_ANNOTATIONS:
                if key in self.annotations:
                    annotations[key] = amqp_long_value(self.annotations[key])
        return Message(
            header=message_header,
            delivery_annotations=self.delivery_annotations,
            message_annotations=annotations,
            properties=message_properties,
            application_properties=self.application_properties,
            data=self._data_body,
            sequence=self._sequence_body,
            value=self._value_body,
            footer=self.footer
        )

    def _to_outgoing_message(self, message_type):
        # convert to an outgoing ServiceBusMessage
        return message_type(body=None, raw_amqp_message=self)

    @property
    def body(self) -> Any:
        """The body of the Message. The format may vary depending on the body type:
        For :class:`azure.servicebus.amqp.AmqpMessageBodyType.DATA<azure.servicebus.amqp.AmqpMessageBodyType.DATA>`,
        the body could be bytes or Iterable[bytes].
        For
        :class:`azure.servicebus.amqp.AmqpMessageBodyType.SEQUENCE<azure.servicebus.amqp.AmqpMessageBodyType.SEQUENCE>`,
        the body could be List or Iterable[List].
        For :class:`azure.servicebus.amqp.AmqpMessageBodyType.VALUE<azure.servicebus.amqp.AmqpMessageBodyType.VALUE>`,
        the body could be any type.

        :rtype: Any
        """
        if self.body_type == AmqpMessageBodyType.DATA: # pylint:disable=no-else-return
            return (i for i in self._data_body)
        elif self.body_type == AmqpMessageBodyType.SEQUENCE:
            return (i for i in self._sequence_body)
        elif self.body_type == AmqpMessageBodyType.VALUE:
            return self._value_body
        return None

    @property
    def properties(self) -> Optional["AmqpMessageProperties"]:
        """
        Properties to add to the message.

        :rtype: Optional[~azure.servicebus.amqp.AmqpMessageProperties]
        """
        return self._properties

    @properties.setter
    def properties(self, value: "AmqpMessageProperties") -> None:
        self._properties = value

    @property
    def application_properties(self) -> Optional[Dict[Union[str, bytes], Any]]:
        """
        Service specific application properties.

        :rtype: Optional[dict]
        """
        return self._application_properties

    @application_properties.setter
    def application_properties(self, value: Optional[Dict[Union[str, bytes], Any]]) -> None:
        self._application_properties = value

    @property
    def annotations(self) -> Optional[Dict[Union[str, bytes], Any]]:
        """
        Service specific message annotations.

        :rtype: Optional[Dict]
        """
        return self._annotations

    @annotations.setter
    def annotations(self, value: Optional[Dict[Union[str, bytes], Any]]) -> None:
        self._annotations = value

    @property
    def delivery_annotations(self) -> Optional[Dict[Union[str, bytes], Any]]:
        """
        Delivery-specific non-standard properties at the head of the message.
        Delivery annotations convey information from the sending peer to the receiving peer.

        :rtype: Dict
        """
        return self._delivery_annotations

    @delivery_annotations.setter
    def delivery_annotations(self, value: Optional[Dict[Union[str, bytes], Any]]) -> None:
        self._delivery_annotations = value

    @property
    def header(self) -> Optional["AmqpMessageHeader"]:
        """
        The message header.

        :rtype: Optional[~azure.servicebus.amqp.AmqpMessageHeader]
        """
        return self._header

    @header.setter
    def header(self, value: "AmqpMessageHeader") -> None:
        self._header = value

    @property
    def footer(self) -> Optional[Dict[Any, Any]]:
        """
        The message footer.

        :rtype: Optional[Dict]
        """
        return self._footer

    @footer.setter
    def footer(self, value: Dict[Any, Any]) -> None:
        self._footer = value


class AmqpMessageHeader(DictMixin):
    """The Message header.
    The Message header. This is only used on received message, and not
    set on messages being sent. The properties set on any given message
    will depend on the Service and not all messages will have all properties.

    Please refer to the AMQP spec:
    http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-messaging-v1.0-os.html#type-header
    for more information on the message header.

    :keyword delivery_count: The number of unsuccessful previous attempts to deliver
     this message. If this value is non-zero it can be taken as an indication that the
     delivery might be a duplicate. On first delivery, the value is zero. It is
     incremented upon an outcome being settled at the sender, according to rules
     defined for each outcome.
    :paramtype delivery_count: Optional[int]
    :keyword time_to_live: Duration in milliseconds for which the message is to be considered "live".
     If this is set then a message expiration time will be computed based on the time of arrival
     at an intermediary. Messages that live longer than their expiration time will be discarded
     (or dead lettered). When a message is transmitted by an intermediary that was received
     with a ttl, the transmitted message's header SHOULD contain a ttl that is computed as the
     difference between the current time and the formerly computed message expiration time,
     i.e., the reduced ttl, so that messages will eventually die if they end up in a delivery loop.
    :paramtype time_to_live: Optional[int]
    :keyword durable: Durable messages MUST NOT be lost even if an intermediary is unexpectedly terminated
     and restarted. A target which is not capable of fulfilling this guarantee MUST NOT accept messages
     where the durable header is set to `True`: if the source allows the rejected outcome then the
     message SHOULD be rejected with the precondition-failed error, otherwise the link MUST be detached
     by the receiver with the same error.
    :paramtype durable: Optional[bool]
    :keyword first_acquirer: If this value is `True`, then this message has not been acquired
     by any other link. If this value is `False`, then this message MAY have previously
     been acquired by another link or links.
    :paramtype first_acquirer: Optional[bool]
    :keyword priority: This field contains the relative message priority. Higher numbers indicate higher
     priority messages. Messages with higher priorities MAY be delivered before those with lower priorities.
    :paramtype priority: Optional[int]

    :ivar delivery_count: The number of unsuccessful previous attempts to deliver
     this message. If this value is non-zero it can be taken as an indication that the
     delivery might be a duplicate. On first delivery, the value is zero. It is
     incremented upon an outcome being settled at the sender, according to rules
     defined for each outcome.
    :vartype delivery_count: Optional[int]
    :ivar time_to_live: Duration in milliseconds for which the message is to be considered "live".
     If this is set then a message expiration time will be computed based on the time of arrival
     at an intermediary. Messages that live longer than their expiration time will be discarded
     (or dead lettered). When a message is transmitted by an intermediary that was received
     with a ttl, the transmitted message's header SHOULD contain a ttl that is computed as the
     difference between the current time and the formerly computed message expiration time,
     i.e., the reduced ttl, so that messages will eventually die if they end up in a delivery loop.
    :vartype time_to_live: Optional[int]
    :ivar durable: Durable messages MUST NOT be lost even if an intermediary is unexpectedly terminated
     and restarted. A target which is not capable of fulfilling this guarantee MUST NOT accept messages
     where the durable header is set to `True`: if the source allows the rejected outcome then the
     message SHOULD be rejected with the precondition-failed error, otherwise the link MUST be detached
     by the receiver with the same error.
    :vartype durable: Optional[bool]
    :ivar first_acquirer: If this value is `True`, then this message has not been acquired
     by any other link. If this value is `False`, then this message MAY have previously
     been acquired by another link or links.
    :vartype first_acquirer: Optional[bool]
    :ivar priority: This field contains the relative message priority. Higher numbers indicate higher
     priority messages. Messages with higher priorities MAY be delivered before those with lower priorities.
    :vartype priority: Optional[int]
    """
    def __init__(
        self,
        *,
        delivery_count: Optional[int] = None,
        time_to_live: Optional[int] = None,
        durable: Optional[bool] = None,
        first_acquirer: Optional[bool] = None,
        priority: Optional[int] = None,
        **kwargs: Any
    ):
        if kwargs:
            warnings.warn(f"Unsupported keyword args: {kwargs}")
        self.delivery_count = delivery_count
        self.time_to_live = time_to_live
        self.first_acquirer = first_acquirer
        self.durable = durable
        self.priority = priority


class AmqpMessageProperties(DictMixin):
    # pylint: disable=too-many-instance-attributes
    """Message properties.
    The properties that are actually used will depend on the service implementation.
    Not all received messages will have all properties, and not all properties
    will be utilized on a sent message.

    Please refer to the AMQP spec:
    http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-messaging-v1.0-os.html#type-properties
    for more information on the message properties.

    :keyword message_id: Message-id, if set, uniquely identifies a message within the message system.
     The message producer is usually responsible for setting the message-id in such a way that it
     is assured to be globally unique. A broker MAY discard a message as a duplicate if the value
     of the message-id matches that of a previously received message sent to the same node.
    :paramtype message_id: Optional[Union[str, bytes, uuid.UUID]]
    :keyword user_id: The identity of the user responsible for producing the message. The client sets
     this value, and it MAY be authenticated by intermediaries.
    :paramtype user_id: Optional[Union[str, bytes]]
    :keyword to: The to field identifies the node that is the intended destination of the message.
     On any given transfer this might not be the node at the receiving end of the link.
    :paramtype to: Optional[Union[str, bytes]]
    :keyword subject: A common field for summary information about the message content and purpose.
    :paramtype subject: Optional[Union[str, bytes]]
    :keyword reply_to: The address of the node to send replies to.
    :paramtype reply_to: Optional[Union[str, bytes]]
    :keyword correlation_id: This is a client-specific id that can be used to mark or identify messages between clients.
    :paramtype correlation_id: Optional[Union[str, bytes]]
    :keyword content_type: The RFC-2046 MIME type for the message's application-data section (body).
    :paramtype content_type: Optional[Union[str, bytes]]
    :keyword content_encoding: The content-encoding property is used as a modifier to the content-type.
    :paramtype content_encoding: Optional[Union[str, bytes]]
    :keyword creation_time: An absolute time when this message was created.
    :paramtype creation_time: Optional[int]
    :keyword absolute_expiry_time: An absolute time when this message is considered to be expired.
    :paramtype absolute_expiry_time: Optional[int]
    :keyword group_id: Identifies the group the message belongs to.
    :paramtype group_id: Optional[Union[str, bytes]]
    :keyword group_sequence: The relative position of this message within its group.
    :paramtype group_sequence: Optional[int]
    :keyword reply_to_group_id: This is a client-specific id that is used so that client can send replies
     to this message to a specific group.
    :paramtype reply_to_group_id: Optional[Union[str, bytes]]

    :ivar message_id: Message-id, if set, uniquely identifies a message within the message system.
     The message producer is usually responsible for setting the message-id in such a way that it
     is assured to be globally unique. A broker MAY discard a message as a duplicate if the value
     of the message-id matches that of a previously received message sent to the same node.
    :vartype message_id: Optional[Union[str, bytes, uuid.UUID]]
    :ivar user_id: The identity of the user responsible for producing the message. The client sets
     this value, and it MAY be authenticated by intermediaries.
    :vartype user_id: Optional[Union[str, bytes]]
    :ivar to: The to field identifies the node that is the intended destination of the message.
     On any given transfer this might not be the node at the receiving end of the link.
    :vartype to: Optional[Union[str, bytes]]
    :ivar subject: A common field for summary information about the message content and purpose.
    :vartype subject: Optional[Union[str, bytes]]
    :ivar reply_to: The address of the node to send replies to.
    :vartype reply_to: Optional[Union[str, bytes]]
    :ivar correlation_id: his is a client-specific id that can be used to mark or identify messages between clients.
    :vartype correlation_id: Optional[Union[str, bytes]]
    :ivar content_type: The RFC-2046 MIME type for the message's application-data section (body).
    :vartype content_type: Optional[Union[str, bytes]]
    :ivar content_encoding: The content-encoding property is used as a modifier to the content-type.
    :vartype content_encoding: Optional[Union[str, bytes]]
    :ivar creation_time: An absolute time when this message was created.
    :vartype creation_time: Optional[int]
    :ivar absolute_expiry_time: An absolute time when this message is considered to be expired.
    :vartype absolute_expiry_time: Optional[int]
    :ivar group_id: Identifies the group the message belongs to.
    :vartype group_id: Optional[Union[str, bytes]]
    :ivar group_sequence: The relative position of this message within its group.
    :vartype group_sequence: Optional[int]
    :ivar reply_to_group_id: This is a client-specific id that is used so that client can send replies
     to this message to a specific group.
    :vartype reply_to_group_id: Optional[Union[str, bytes]]
    """
    def __init__(
        self,
        *,
        message_id: Optional[Union[str, bytes, uuid.UUID]] = None,
        user_id: Optional[Union[str, bytes]] = None,
        to: Optional[Union[str, bytes]] = None,
        subject: Optional[Union[str, bytes]] = None,
        reply_to: Optional[Union[str, bytes]] = None,
        correlation_id: Optional[Union[str, bytes]] = None,
        content_type: Optional[Union[str, bytes]] = None,
        content_encoding: Optional[Union[str, bytes]] = None,
        creation_time: Optional[int] = None,
        absolute_expiry_time: Optional[int] = None,
        group_id: Optional[Union[str, bytes]] = None,
        group_sequence: Optional[int] = None,
        reply_to_group_id: Optional[Union[str, bytes]] = None,
        **kwargs: Any
    ):
        if kwargs:
            warnings.warn(f"Unsupported keyword args: {kwargs}")
        self.message_id = message_id
        self.user_id = user_id
        self.to = to
        self.subject = subject
        self.reply_to = reply_to
        self.correlation_id = correlation_id
        self.content_type = content_type
        self.content_encoding = content_encoding
        self.creation_time = creation_time
        self.absolute_expiry_time = absolute_expiry_time
        self.group_id = group_id
        self.group_sequence = group_sequence
        self.reply_to_group_id = reply_to_group_id
