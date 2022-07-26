from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient
from azure.eventhub import TransportType


def test_custom_endpoint_async():
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


def test_custom_certificate_async():
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
