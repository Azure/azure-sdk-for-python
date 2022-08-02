# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from __future__ import annotations
from typing import Optional, Any, cast, Mapping, Dict, Union

from ._amqp_utils import normalized_data_body, normalized_sequence_body
from ._constants import AmqpMessageBodyType
from .._mixin import DictMixin


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
    :paramtype header: Optional[~azure.eventhub.amqp.AmqpMessageHeader]
    :keyword footer: The amqp message footer.
    :paramtype footer: Optional[Dict]
    :keyword properties: Properties to add to the amqp message.
    :paramtype properties: Optional[~azure.eventhub.amqp.AmqpMessageProperties]
    :keyword application_properties: Service specific application properties.
    :paramtype application_properties: Optional[Dict]
    :keyword annotations: Service specific message annotations.
    :paramtype annotations: Optional[Dict]
    :keyword delivery_annotations: Service specific delivery annotations.
    :paramtype delivery_annotations: Optional[Dict]
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        self._encoding = kwargs.pop("encoding", "UTF-8")
        self._data_body = None
        self._sequence_body = None
        self._value_body = None

        # internal usage only for Event Hub received message
        message = kwargs.pop("message", None)
        if message:
            self._from_amqp_message(message)
            return

        # manually constructed AMQPAnnotatedMessage
        input_count_validation = len(
            [
                key
                for key in ("data_body", "sequence_body", "value_body")
                if key in kwargs
            ]
        )
        if input_count_validation != 1:
            raise ValueError(
                "There should be one and only one of either data_body, sequence_body "
                "or value_body being set as the body of the AmqpAnnotatedMessage."
            )

        self._body_type = None
        if "data_body" in kwargs:
            self._data_body = normalized_data_body(kwargs.get("data_body"))
            self._body_type = AmqpMessageBodyType.DATA
        elif "sequence_body" in kwargs:
            self._sequence_body = normalized_sequence_body(kwargs.get("sequence_body"))
            self._body_type = AmqpMessageBodyType.SEQUENCE
        elif "value_body" in kwargs:
            self._value_body = kwargs.get("value_body")
            self._body_type = AmqpMessageBodyType.VALUE

        header_dict = cast(Mapping, kwargs.get("header"))
        self._header = AmqpMessageHeader(**header_dict) if "header" in kwargs else None
        self._footer = kwargs.get("footer")
        properties_dict = cast(Mapping, kwargs.get("properties"))
        self._properties = (
            AmqpMessageProperties(**properties_dict) if "properties" in kwargs else None
        )
        self._application_properties = kwargs.get("application_properties")
        self._annotations = kwargs.get("annotations")
        self._delivery_annotations = kwargs.get("delivery_annotations")

    def __str__(self) -> str:
        if self._body_type == AmqpMessageBodyType.DATA:
            return "".join(d.decode(self._encoding) for d in self._data_body)
        if self._body_type == AmqpMessageBodyType.SEQUENCE:
            return str(self._sequence_body)
        if self._body_type == AmqpMessageBodyType.VALUE:
            return str(self._value_body)
        return ""

    def __repr__(self) -> str:
        # pylint: disable=bare-except
        message_repr = "body={}".format(str(self))
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
            message_repr += ", application_properties={}".format(
                self.application_properties
            )
        except:
            message_repr += ", application_properties=<read-error>"
        try:
            message_repr += ", delivery_annotations={}".format(
                self.delivery_annotations
            )
        except:
            message_repr += ", delivery_annotations=<read-error>"
        try:
            message_repr += ", annotations={}".format(self.annotations)
        except:
            message_repr += ", annotations=<read-error>"
        return "AmqpAnnotatedMessage({})".format(message_repr)[:1024]

    def _from_amqp_message(self, message):
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
        self._footer = message.footer if message.footer else {}
        self._annotations = message.message_annotations if message.message_annotations else {}
        self._delivery_annotations = message.delivery_annotations if message.delivery_annotations else {}
        self._application_properties = message.application_properties if message.application_properties else {}
        if message.data:
            self._data_body = list(message.data)
            self._body_type = AmqpMessageBodyType.DATA
        elif message.sequence:
            self._sequence_body = list(message.sequence)
            self._body_type = AmqpMessageBodyType.SEQUENCE
        else:
            self._value_body = message.value
            self._body_type = AmqpMessageBodyType.VALUE

    @property
    def body(self) -> Any:
        """The body of the Message. The format may vary depending on the body type:
        For ~azure.eventhub.AmqpMessageBodyType.DATA, the body could be bytes or Iterable[bytes]
        For ~azure.eventhub.AmqpMessageBodyType.SEQUENCE, the body could be List or Iterable[List]
        For ~azure.eventhub.AmqpMessageBodyType.VALUE, the body could be any type.
        :rtype: Any
        """
        if self._body_type == AmqpMessageBodyType.DATA: # pylint:disable=no-else-return
            return (i for i in self._data_body)
        elif self._body_type == AmqpMessageBodyType.SEQUENCE:
            return (i for i in self._sequence_body)
        elif self._body_type == AmqpMessageBodyType.VALUE:
            return self._value_body
        return None

    @property
    def body_type(self) -> AmqpMessageBodyType:
        """The body type of the underlying AMQP message.
        rtype: ~azure.eventhub.amqp.AmqpMessageBodyType
        """
        return self._body_type

    @property
    def properties(self) -> Optional[AmqpMessageProperties]:
        """
        Properties to add to the message.
        :rtype: Optional[~azure.eventhub.amqp.AmqpMessageProperties]
        """
        return self._properties

    @properties.setter
    def properties(self, value: AmqpMessageProperties) -> None:
        self._properties = value

    @property
    def application_properties(self) -> Optional[Dict[Union[str, bytes], Any]]:
        """
        Service specific application properties.

        :rtype: Optional[Dict]
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
    def header(self) -> Optional[AmqpMessageHeader]:
        """
        The message header.
        :rtype: Optional[~azure.eventhub.amqp.AmqpMessageHeader]
        """
        return self._header

    @header.setter
    def header(self, value: AmqpMessageHeader) -> None:
        self._header = value

    @property
    def footer(self) -> Optional[Dict[Any, Any]]:
        """
        The message footer.

        :rtype: Optional[Dict]
        """
        return self._footer

    @footer.setter
    def footer(self, value: Optional[Dict[Any, Any]]) -> None:
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

    def __init__(self, **kwargs):
        self.delivery_count = kwargs.get("delivery_count")
        self.time_to_live = kwargs.get("time_to_live")
        self.first_acquirer = kwargs.get("first_acquirer")
        self.durable = kwargs.get("durable")
        self.priority = kwargs.get("priority")


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
    :vartype message_id: Optional[bytes]
    :ivar user_id: The identity of the user responsible for producing the message. The client sets
     this value, and it MAY be authenticated by intermediaries.
    :vartype user_id: Optional[bytes]
    :ivar to: The to field identifies the node that is the intended destination of the message.
     On any given transfer this might not be the node at the receiving end of the link.
    :vartype to: Optional[bytes]
    :ivar subject: A common field for summary information about the message content and purpose.
    :vartype subject: Optional[bytes]
    :ivar reply_to: The address of the node to send replies to.
    :vartype reply_to: Optional[bytes]
    :ivar correlation_id: his is a client-specific id that can be used to mark or identify messages between clients.
    :vartype correlation_id: Optional[bytes]
    :ivar content_type: The RFC-2046 MIME type for the message's application-data section (body).
    :vartype content_type: Optional[bytes]
    :ivar content_encoding: The content-encoding property is used as a modifier to the content-type.
    :vartype content_encoding: Optional[bytes]
    :ivar creation_time: An absolute time when this message was created.
    :vartype creation_time: Optional[int]
    :ivar absolute_expiry_time: An absolute time when this message is considered to be expired.
    :vartype absolute_expiry_time: Optional[int]
    :ivar group_id: Identifies the group the message belongs to.
    :vartype group_id: Optional[bytes]
    :ivar group_sequence: The relative position of this message within its group.
    :vartype group_sequence: Optional[int]
    :ivar reply_to_group_id: This is a client-specific id that is used so that client can send replies
     to this message to a specific group.
    :vartype reply_to_group_id: Optional[bytes]
    """

    def __init__(self, **kwargs):
        self.message_id = kwargs.get("message_id")
        self.user_id = kwargs.get("user_id")
        self.to = kwargs.get("to")
        self.subject = kwargs.get("subject")
        self.reply_to = kwargs.get("reply_to")
        self.correlation_id = kwargs.get("correlation_id")
        self.content_type = kwargs.get("content_type")
        self.content_encoding = kwargs.get("content_encoding")
        self.creation_time = kwargs.get("creation_time")
        self.absolute_expiry_time = kwargs.get("absolute_expiry_time")
        self.group_id = kwargs.get("group_id")
        self.group_sequence = kwargs.get("group_sequence")
        self.reply_to_group_id = kwargs.get("reply_to_group_id")
