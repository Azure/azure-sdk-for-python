#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
from azure.core.pipeline.policies import RetryMode
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient, TransportType


def test_custom_endpoint():
    producer = EventHubProducerClient(
        "fake.host.com",
        "fake_eh",
        None,
    )
    assert not producer._config.custom_endpoint_hostname
    assert producer._config.transport_type == TransportType.Amqp
    assert producer._config.connection_port == 5671

    producer = EventHubProducerClient(
        "fake.host.com",
        "fake_eh",
        None,
        custom_endpoint_address="https://12.34.56.78"
    )
    assert producer._config.custom_endpoint_hostname == '12.34.56.78'
    assert producer._config.transport_type == TransportType.AmqpOverWebsocket
    assert producer._config.connection_port == 443

    producer = EventHubProducerClient(
        "fake.host.com",
        "fake_eh",
        None,
        custom_endpoint_address="sb://fake.endpoint.com:443"
    )
    assert producer._config.custom_endpoint_hostname == 'fake.endpoint.com'
    assert producer._config.transport_type == TransportType.AmqpOverWebsocket
    assert producer._config.connection_port == 443

    producer = EventHubProducerClient(
        "fake.host.com",
        "fake_eh",
        None,
        custom_endpoint_address="https://fake.endpoint.com:200"
    )
    assert producer._config.custom_endpoint_hostname == 'fake.endpoint.com'
    assert producer._config.transport_type == TransportType.AmqpOverWebsocket
    assert producer._config.connection_port == 200

    producer = EventHubProducerClient(
        "fake.host.com",
        "fake_eh",
        None,
        custom_endpoint_address="fake.endpoint.com:200"
    )
    assert producer._config.custom_endpoint_hostname == 'fake.endpoint.com'
    assert producer._config.transport_type == TransportType.AmqpOverWebsocket
    assert producer._config.connection_port == 200

    consumer = EventHubConsumerClient(
        "fake.host.com",
        "fake_eh",
        "fake_group",
        None,
    )
    assert not consumer._config.custom_endpoint_hostname
    assert consumer._config.transport_type == TransportType.Amqp
    assert consumer._config.connection_port == 5671

    consumer = EventHubConsumerClient(
        "fake.host.com",
        "fake_eh",
        "fake_group",
        None,
        custom_endpoint_address="https://12.34.56.78/"
    )
    assert consumer._config.custom_endpoint_hostname == '12.34.56.78'
    assert consumer._config.transport_type == TransportType.AmqpOverWebsocket
    assert consumer._config.connection_port == 443

    consumer = EventHubConsumerClient(
        "fake.host.com",
        "fake_eh",
        "fake_group",
        None,
        custom_endpoint_address="sb://fake.endpoint.com:443"
    )
    assert consumer._config.custom_endpoint_hostname == 'fake.endpoint.com'
    assert consumer._config.transport_type == TransportType.AmqpOverWebsocket
    assert consumer._config.connection_port == 443

    consumer = EventHubConsumerClient(
        "fake.host.com",
        "fake_eh",
        "fake_group",
        None,
        custom_endpoint_address="https://fake.endpoint.com:200"
    )
    assert consumer._config.custom_endpoint_hostname == 'fake.endpoint.com'
    assert consumer._config.transport_type == TransportType.AmqpOverWebsocket
    assert consumer._config.connection_port == 200

    consumer = EventHubConsumerClient(
        "fake.host.com",
        "fake_eh",
        "fake_group",
        None,
        custom_endpoint_address="fake.endpoint.com:200"
    )
    assert consumer._config.custom_endpoint_hostname == 'fake.endpoint.com'
    assert consumer._config.transport_type == TransportType.AmqpOverWebsocket
    assert consumer._config.connection_port == 200


def test_custom_certificate():
    producer = EventHubProducerClient(
        "fake.host.com",
        "fake_eh",
        None,
        connection_verify='/usr/bin/local/cert'
    )
    assert producer._config.connection_verify == '/usr/bin/local/cert'

    consumer = EventHubConsumerClient(
        "fake.host.com",
        "fake_eh",
        "fake_group",
        None,
        connection_verify='D:/local/certfile'
    )
    assert consumer._config.connection_verify == 'D:/local/certfile'

def test_backoff_fixed_retry():
    client = EventHubProducerClient(
        'fake.host.com',
        'fake_eh',
        None,
        retry_mode='fixed'
    )
    backoff = client._config.backoff_factor
    start_time = time.time()
    client._backoff(retried_times=1, last_exception=Exception('fake'), timeout_time=None)
    sleep_time = time.time() - start_time
    # exp = 0.8 * (2 ** 1) = 1.6
    # time.sleep() in _backoff will take AT LEAST time 'exp' for 'exponential'
    # check that fixed is less than 'exp'
    assert sleep_time < backoff * (2 ** 1)

    client = EventHubProducerClient(
        'fake.host.com',
        'fake_eh',
        None,
        retry_mode=RetryMode.Fixed
    )
    backoff = client._config.backoff_factor
    start_time = time.time()
    client._backoff(retried_times=1, last_exception=Exception('fake'), timeout_time=None)
    sleep_time = time.time() - start_time
    # exp = 0.8 * (2 ** 1) = 1.6
    # time.sleep() in _backoff will take AT LEAST time 'exp' for 'exponential'
    # check that fixed is less than 'exp'
    assert sleep_time < backoff * (2 ** 1)
