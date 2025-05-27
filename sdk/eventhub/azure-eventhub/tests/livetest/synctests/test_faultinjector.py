import ssl
import threading
import pytest

from azure.eventhub import EventData
from azure.eventhub import EventHubConsumerClient


@pytest.mark.liveTest
def test_receive_partition_using_fault_injector_detach_after_delay(
    auth_credential_senders,
    faultinjector_detach_after_delay,
):
    fault_injector_config = faultinjector_detach_after_delay

    if not fault_injector_config:
        pytest.skip(
            "Fault injector not enabled. See conftest.py::faultinjector for requirements."
        )

    fully_qualified_namespace, eventhub_name, credential, senders = (
        auth_credential_senders
    )

    senders[0].send(EventData("Test EventData"))

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # Uncomment to enable DEBUG logging to get more information on frames.
    # logger = logging.getLogger('azure.eventhub')
    # logger.setLevel(logging.DEBUG)
    # client_args["logging_enable"] = True

    client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=credential(),
        consumer_group="$default",
        transport_type=fault_injector_config["transport_type"],
        custom_endpoint_address=fault_injector_config["custom_endpoint_address"],
        ssl_context=fault_injector_config["sslcontext"],
        retry_total=0,
    )

    def on_event(partition_context, _):
        on_event.received += 1
        on_event.partition_id = partition_context.partition_id
        on_event.consumer_group = partition_context.consumer_group
        on_event.fully_qualified_namespace = partition_context.fully_qualified_namespace
        on_event.eventhub_name = partition_context.eventhub_name

    on_event.received = 0

    with client:
        worker = threading.Thread(
            target=client.receive,
            args=(on_event,),
            kwargs={"starting_position": "-1", "partition_id": "0"},
        )
        worker.start()
        worker.join(timeout=10)

        assert on_event.received == 1
        assert on_event.partition_id == "0"
        assert on_event.consumer_group == "$default"
        assert on_event.fully_qualified_namespace == fully_qualified_namespace
        assert on_event.eventhub_name == eventhub_name
