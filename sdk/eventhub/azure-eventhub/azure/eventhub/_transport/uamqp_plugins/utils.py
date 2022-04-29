# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from .constants import AmqpMessageBodyType
import uamqp

def to_outgoing_amqp_message(annotated_message):
    message_header = None
    if annotated_message.header:
        message_header = uamqp.message.MessageHeader()
        message_header.delivery_count = annotated_message.header.delivery_count
        message_header.time_to_live = annotated_message.header.time_to_live
        message_header.first_acquirer = annotated_message.header.first_acquirer
        message_header.durable = annotated_message.header.durable
        message_header.priority = annotated_message.header.priority

    message_properties = None
    if annotated_message.properties:
        message_properties = uamqp.message.MessageProperties(
            message_id=annotated_message.properties.message_id,
            user_id=annotated_message.properties.user_id,
            to=annotated_message.properties.to,
            subject=annotated_message.properties.subject,
            reply_to=annotated_message.properties.reply_to,
            correlation_id=annotated_message.properties.correlation_id,
            content_type=annotated_message.properties.content_type,
            content_encoding=annotated_message.properties.content_encoding,
            creation_time=int(annotated_message.properties.creation_time)
                if annotated_message.properties.creation_time else None,
            absolute_expiry_time=int(annotated_message.properties.absolute_expiry_time)
            if annotated_message.properties.absolute_expiry_time else None,
            group_id=annotated_message.properties.group_id,
            group_sequence=annotated_message.properties.group_sequence,
            reply_to_group_id=annotated_message.properties.reply_to_group_id,
            encoding=annotated_message._encoding    # pylint: disable=protected-access
        )

    amqp_body_type = annotated_message.body_type  # pylint: disable=protected-access
    amqp_body = annotated_message.body
    if amqp_body_type == AmqpMessageBodyType.DATA:
        amqp_body_type = uamqp.MessageBodyType.Data
        amqp_body = list(amqp_body)
    elif amqp_body_type == AmqpMessageBodyType.SEQUENCE:
        amqp_body_type = uamqp.MessageBodyType.Sequence
        amqp_body = list(amqp_body)
    else:
        # amqp_body_type is type of AmqpMessageBodyType.VALUE
        amqp_body_type = uamqp.MessageBodyType.Value

    return uamqp.message.Message(
        body=amqp_body,
        body_type=amqp_body_type,
        header=message_header,
        properties=message_properties,
        application_properties=annotated_message.application_properties,
        annotations=annotated_message.annotations,
        delivery_annotations=annotated_message.delivery_annotations,
        footer=annotated_message.footer
    )
