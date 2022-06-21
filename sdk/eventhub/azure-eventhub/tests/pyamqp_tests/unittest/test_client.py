import pytest
import types
from azure.eventhub._pyamqp.client import AMQPClient
from azure.eventhub._pyamqp.authentication import SASTokenAuth

@pytest.mark.skip
def test_keep_alive_thread_fail_to_start():

    class MockThread:
        def __init__(self):
            pass

        def start(self):
            raise RuntimeError("Fail to start")

        def join(self):
            raise RuntimeError("Fail to join")

    def hack_open(ins):
        ins._keep_alive_thread = MockThread()
        ins._keep_alive_thread.start()

    sas_auth = SASTokenAuth(
        "sb://fake/fake", "fake", "fake", "fake")
    target = "amqps://{}/{}".format("fake", "fake")
    client = AMQPClient(target, auth=sas_auth, keep_alive_interval=10)
    client.open = types.MethodType(hack_open, client)
    try:
        client.open()
    except Exception as exc:
        assert type(exc) == RuntimeError
        client.close()
        assert not client._keep_alive_thread

#Keep alive thread still exists after client is closed 