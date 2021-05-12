# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import copy
from typing import Optional, Any

import uamqp

from ._constants import AMQP_MESSAGE_BODY_TYPE_MAP, AMQPMessageBodyType


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


class AMQPAnnotatedMessage(object):
    """
    The AMQP Annotated Message for advanced sending and receiving scenarios which allows you to
    access to low-level AMQP message sections.
    Please refer to the AMQP spec:
    http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-messaging-v1.0-os.html#section-message-format
    for more information on the message format.

    :keyword data_body: The body consists of one or more data sections and each section contains opaque binary data.
    :paramtype data_body: Optional[Union[str, bytes, List[Union[str, bytes]]]]
    :keyword sequence_body: The body consists of one or more sequence sections and
     each section contains an arbitrary number of structured data elements.
    :paramtype sequence_body: Optional[List[Any]]
    :keyword value_body: The body consists of one amqp-value section and the section contains a single AMQP value.
    :paramtype value_body: Any
    :keyword header: The amqp message header.
    :paramtype header: Optional[~azure.servicebus.amqp.AMQPMessageHeader]
    :keyword footer: The amqp message footer.
    :paramtype footer: Optional[dict]
    :keyword properties: Properties to add to the amqp message.
    :paramtype properties: Optional[~azure.servicebus.amqp.AMQPMessageProperties]
    :keyword application_properties: Service specific application properties.
    :paramtype application_properties: Optional[dict]
    :keyword annotations: Service specific message annotations.
    :paramtype annotations: Optional[dict]
    :keyword delivery_annotations: Service specific delivery annotations.
    :paramtype delivery_annotations: Optional[dict]
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        self._message = kwargs.pop("message", None)

        if self._message:
            # internal usage only for service bus received message
            return

        input_count_validation = len([key for key in ("data_body", "sequence_body", "value_body") if key in kwargs])
        if input_count_validation != 1:
            raise ValueError(
                "There should be one and only one of either data_body, sequence_body "
                "or value_body being set as the body of the AMQPAnnotatedMessage."
            )

        body, body_type = None, None
        if "data_body" in kwargs:
            body = kwargs.get("data_body")
            body_type = uamqp.MessageBodyType.Data
        elif "sequence_body" in kwargs:
            body = kwargs.get("sequence_body")
            body_type = uamqp.MessageBodyType.Sequence
        elif "value_body" in kwargs:
            body = kwargs.get("value_body")
            body_type = uamqp.MessageBodyType.Value

        header = kwargs.get("header")
        footer = kwargs.get("footer")
        properties = kwargs.get("properties")
        application_properties = kwargs.get("application_properties")
        annotations = kwargs.get("annotations")
        delivery_annotations = kwargs.get("delivery_annotations")

        message_header = None
        message_properties = None
        if header:
            message_header = uamqp.message.MessageHeader()
            message_header.delivery_count = header.get("delivery_count", 0)
            message_header.time_to_live = header.get("time_to_live")
            message_header.first_acquirer = header.get("first_acquirer")
            message_header.durable = header.get("durable")
            message_header.priority = header.get("priority")

        if properties:
            message_properties = uamqp.message.MessageProperties(**properties)

        self._message = uamqp.message.Message(
            body=body,
            body_type=body_type,
            header=message_header,
            footer=footer,
            properties=message_properties,
            application_properties=application_properties,
            annotations=annotations,
            delivery_annotations=delivery_annotations,
        )

    @property
    def body(self):
        # type: () -> Any
        """The body of the Message. The format may vary depending
        on the body type:
        For ~azure.servicebus.AMQPMessageBodyType.DATA, the body could be bytes or Iterable[bytes]
        For ~azure.servicebus.AMQPMessageBodyType.SEQUENCE, the body could be List or Iterable[List]
        For ~azure.servicebus.AMQPMessageBodyType.VALUE, the body could be any type.

        :rtype: Any
        """
        return self._message.get_data()

    @property
    def body_type(self):
        # type: () -> Optional[AMQPMessageBodyType]
        """The body type of the underlying AMQP message.

        rtype: Optional[~azure.servicebus.amqp.AMQPMessageBodyType]
        """
        return AMQP_MESSAGE_BODY_TYPE_MAP.get(
            self._message._body.type  # pylint: disable=protected-access
        )

    @property
    def properties(self):
        # type: () -> Optional[AMQPMessageProperties]
        """
        Properties to add to the message.

        :rtype: Optional[~azure.servicebus.amqp.AMQPMessageProperties]
        """
        if self._message.properties:
            return AMQPMessageProperties(
                message_id=self._message.properties.message_id,
                user_id=self._message.properties.user_id,
                to=self._message.properties.to,
                subject=self._message.properties.subject,
                reply_to=self._message.properties.reply_to,
                correlation_id=self._message.properties.correlation_id,
                content_type=self._message.properties.content_type,
                content_encoding=self._message.properties.content_encoding,
                absolute_expiry_time=self._message.properties.absolute_expiry_time,
                creation_time=self._message.properties.creation_time,
                group_id=self._message.properties.group_id,
                group_sequence=self._message.properties.group_sequence,
                reply_to_group_id=self._message.properties.reply_to_group_id,
            )
        return None

    # NOTE: These are disabled pending arch. design and cross-sdk consensus on
    # how we will expose sendability of amqp focused messages. To undo, uncomment and remove deepcopies/workarounds.
    #
    # @properties.setter
    # def properties(self, value):
    #    self._message.properties = value

    @property
    def application_properties(self):
        # type: () -> Optional[dict]
        """
        Service specific application properties.

        :rtype: Optional[dict]
        """
        return copy.deepcopy(self._message.application_properties)

    # @application_properties.setter
    # def application_properties(self, value):
    #    self._message.application_properties = value

    @property
    def annotations(self):
        # type: () -> Optional[dict]
        """
        Service specific message annotations.

        :rtype: Optional[dict]
        """
        return copy.deepcopy(self._message.annotations)

    # @annotations.setter
    # def annotations(self, value):
    #    self._message.annotations = value

    @property
    def delivery_annotations(self):
        # type: () -> Optional[dict]
        """
        Delivery-specific non-standard properties at the head of the message.
        Delivery annotations convey information from the sending peer to the receiving peer.

        :rtype: dict
        """
        return copy.deepcopy(self._message.delivery_annotations)

    # @delivery_annotations.setter
    # def delivery_annotations(self, value):
    #    self._message.delivery_annotations = value

    @property
    def header(self):
        # type: () -> Optional[AMQPMessageHeader]
        """
        The message header.

        :rtype: Optional[~azure.servicebus.amqp.AMQPMessageHeader]
        """
        if self._message.header:
            return AMQPMessageHeader(
                delivery_count=self._message.header.delivery_count,
                time_to_live=self._message.header.time_to_live,
                first_acquirer=self._message.header.first_acquirer,
                durable=self._message.header.durable,
                priority=self._message.header.priority
            )
        return None

    # @header.setter
    # def header(self, value):
    #    self._message.header = value

    @property
    def footer(self):
        # type: () -> Optional[dict]
        """
        The message footer.

        :rtype: Optional[dict]
        """
        return copy.deepcopy(self._message.footer)

    # @footer.setter
    # def footer(self, value):
    #    self._message.footer = value


class AMQPMessageHeader(DictMixin):
    """The Message header.
    The Message header. This is only used on received message, and not
    set on messages being sent. The properties set on any given message
    will depend on the Service and not all messages will have all properties.

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


class AMQPMessageProperties(DictMixin):
    """Message properties.
    The properties that are actually used will depend on the service implementation.
    Not all received messages will have all properties, and not all properties
    will be utilized on a sent message.

    :keyword message_id:
    :paramtype message_id: Optional[Union[str, bytes, uuid.UUID]]
    :keyword user_id:
    :paramtype user_id: Optional[Union[str, bytes]]
    :keyword to:
    :paramtype to: Optional[Union[str, bytes]]
    :keyword subject:
    :paramtype subject: Optional[Union[str, bytes]]
    :keyword reply_to:
    :paramtype reply_to: Optional[Union[str, bytes]]
    :keyword correlation_id:
    :paramtype correlation_id: Optional[Union[str, bytes]]
    :keyword content_type:
    :paramtype content_type: Optional[Union[str, bytes]]
    :keyword content_encoding:
    :paramtype content_encoding: Optional[Union[str, bytes]]
    :keyword creation_time:
    :paramtype creation_time: Optional[int]
    :keyword absolute_expiry_time:
    :paramtype absolute_expiry_time: Optional[int]
    :keyword group_id:
    :paramtype group_id: Optional[Union[str, bytes]]
    :keyword group_sequence:
    :paramtype group_sequence: Optional[int]
    :keyword reply_to_group_id:
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
    :ivar subject:
    :vartype subject: Optional[Union[str, bytes]]
    :ivar reply_to:
    :vartype reply_to: Optional[Union[str, bytes]]
    :ivar correlation_id:
    :vartype correlation_id: Optional[Union[str, bytes]]
    :ivar content_type:
    :vartype content_type: Optional[Union[str, bytes]]
    :ivar content_encoding:
    :vartype content_encoding: Optional[Union[str, bytes]]
    :ivar creation_time:
    :vartype creation_time: Optional[int]
    :ivar absolute_expiry_time:
    :vartype absolute_expiry_time: Optional[int]
    :ivar group_id:
    :vartype group_id: Optional[Union[str, bytes]]
    :ivar group_sequence:
    :vartype group_sequence: Optional[int]
    :ivar reply_to_group_id:
    :vartype reply_to_group_id: Optional[Union[str, bytes]]
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
