#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending, receiving and parsing amqp annotated message(s) to Event Hubs.
"""

import os
from typing import TYPE_CHECKING
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient
from azure.eventhub.amqp import AmqpAnnotatedMessage, AmqpMessageBodyType

if TYPE_CHECKING:
    from typing import List, Dict, Any, Optional
    from azure.eventhub import EventDataBatch, PartitionContext, EventData


CONNECTION_STR: str = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME: str = os.environ['EVENT_HUB_NAME']

def send_data_message(producer: EventHubProducerClient) -> None:
    data_body: List[bytes] = [b'aa', b'bb', b'cc']
    application_properties: Dict[str, str] = {"body_type": "data"}
    delivery_annotations: Dict[str, str] = {"delivery_annotation_key": "value"}
    data_message: AmqpAnnotatedMessage = AmqpAnnotatedMessage(
        data_body=data_body,
        delivery_annotations=delivery_annotations,
        application_properties=application_properties
    )
    batch: EventDataBatch = producer.create_batch()
    batch.add(data_message)
    producer.send_batch(batch)
    print("Message of data body sent.")


def send_sequence_message(producer: EventHubProducerClient) -> None:
    sequence_body: List[Any] = [b'message', 123.456, True]
    footer:Dict[str, str] = {'footer_key': 'footer_value'}
    properties: Dict[str, str] = {"subject": "sequence"}
    application_properties: Dict[str, str] = {"body_type": "sequence"}
    sequence_message: AmqpAnnotatedMessage = AmqpAnnotatedMessage(
        sequence_body=sequence_body,
        footer=footer,
        properties=properties,
        application_properties=application_properties
    )
    producer.send_batch([sequence_message])
    print("Message of sequence body sent.")


def send_value_message(producer: EventHubProducerClient) -> None:
    value_body: Dict[bytes, Any] = {b"key": [-123, b'data', False]}
    header: Dict[str, int] = {"priority": 10}
    annotations: Dict[str, str] = {"annotation_key": "value"}
    application_properties: Dict[str, str] = {"body_type": "value"}
    value_message: AmqpAnnotatedMessage = AmqpAnnotatedMessage(
        value_body=value_body,
        header=header,
        annotations=annotations,
        application_properties=application_properties
    )
    producer.send_batch([value_message])
    print("Message of value body sent.")


def on_event(partition_context: PartitionContext, event: Optional[EventData]) -> None:
    # Put your code here.
    # If the operation is i/o intensive, multi-thread will have better performance.
    print(f"Received event from partition: {partition_context.partition_id}")
    raw_amqp_message: AmqpAnnotatedMessage = event.raw_amqp_message # type: ignore
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


def receive_and_parse_message(consumer: EventHubConsumerClient) -> None:
    with consumer:
        try:
            consumer.receive(
                on_event=on_event,
                starting_position="-1",  # "-1" is from the beginning of the partition.
            )
        except KeyboardInterrupt:
            print('Stopped receiving.')


producer: EventHubProducerClient = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME
)
with producer:
    send_data_message(producer)
    send_sequence_message(producer)
    send_value_message(producer)


consumer: EventHubConsumerClient = EventHubConsumerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    consumer_group='$Default',
    eventhub_name=EVENTHUB_NAME,
)
receive_and_parse_message(consumer)
