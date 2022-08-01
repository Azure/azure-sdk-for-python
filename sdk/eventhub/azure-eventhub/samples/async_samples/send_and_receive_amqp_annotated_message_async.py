#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending, receiving and parsing amqp annotated message(s) to Event Hubs.
"""

# pylint: disable=C0111

import os
import asyncio
from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient
from azure.eventhub.amqp import AmqpAnnotatedMessage, AmqpMessageBodyType


CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

async def send_data_message(producer):
    data_body = [b'aa', b'bb', b'cc']
    application_properties = {"body_type": "data"}
    delivery_annotations = {"delivery_annotation_key": "value"}
    data_message = AmqpAnnotatedMessage(
        data_body=data_body,
        delivery_annotations=delivery_annotations,
        application_properties=application_properties
    )
    batch = await producer.create_batch()
    batch.add(data_message)
    await producer.send_batch(batch)
    print("Message of data body sent.")


async def send_sequence_message(producer):
    sequence_body = [b'message', 123.456, True]
    footer = {'footer_key': 'footer_value'}
    properties = {"subject": "sequence"}
    application_properties = {"body_type": "sequence"}
    sequence_message = AmqpAnnotatedMessage(
        sequence_body=sequence_body,
        footer=footer,
        properties=properties,
        application_properties=application_properties
    )
    await producer.send_batch([sequence_message])
    print("Message of sequence body sent.")


async def send_value_message(producer):
    value_body = {b"key": [-123, b'data', False]}
    header = {"priority": 10}
    annotations = {"annotation_key": "value"}
    application_properties = {"body_type": "value"}
    value_message = AmqpAnnotatedMessage(
        value_body=value_body,
        header=header,
        annotations=annotations,
        application_properties=application_properties
    )
    await producer.send_batch([value_message])
    print("Message of value body sent.")


async def on_event(partition_context, event):
    # Put your code here.
    # If the operation is i/o intensive, multi-thread will have better performance.
    print("Received event from partition: {}".format(partition_context.partition_id))
    raw_amqp_message = event.raw_amqp_message
    if raw_amqp_message.body_type == AmqpMessageBodyType.DATA:
        print("Message of data body received. Body is:")
        for data_section in raw_amqp_message.body:
            print(data_section)
    elif raw_amqp_message.body_type == AmqpMessageBodyType.SEQUENCE:
        print("Message of sequence body received. Body is:")
        for sequence_section in raw_amqp_message.body:
            print(sequence_section)
    elif raw_amqp_message.body_type == AmqpMessageBodyType.VALUE:
        print("Message of value body received. Body is:")
        print(raw_amqp_message.body)


async def receive_and_parse_message(consumer):
    async with consumer:
        try:
            await consumer.receive(
                on_event=on_event,
                starting_position="-1",  # "-1" is from the beginning of the partition.
            )
        except KeyboardInterrupt:
            print('Stopped receiving.')


async def main():
    # Send AmqpAnnotatedMessage
    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENTHUB_NAME
    )
    async with producer:
        await send_data_message(producer)
        await send_sequence_message(producer)
        await send_value_message(producer)

    # Receive
    consumer = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group='$Default',
        eventhub_name=EVENTHUB_NAME,
    )
    await receive_and_parse_message(consumer)

if __name__ == '__main__':
    asyncio.run(main())
