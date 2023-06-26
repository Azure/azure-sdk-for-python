import pytest
from unittest.mock import AsyncMock
from azure.eventhub._pyamqp.aio import Connection

@pytest.mark.asyncio
async def test_connection_end_session_on_timeout():
    connection = Connection("fake.host.com")
    connection._process_outgoing_frame = AsyncMock(return_value=None)
    connection._network_trace_params = {'amqpSession':'test_name'}
    # create session on the Connection
    session = connection.create_session(network_trace=False)
    outgoing_channel = session.channel
    # after a BEGIN response from the server set up incoming endpoint
    incoming_channel = 0
    connection._incoming_endpoints[incoming_channel] = session
    assert outgoing_channel == connection._incoming_endpoints[incoming_channel].channel
    # typically after some inactivity(60,000 ms), the server will force a connection close
    # and will send across an END frame
    await connection._incoming_end(incoming_channel, None)
    # end points dont have the channels anymore and Session link is gone.
    assert outgoing_channel not in connection._outgoing_endpoints
    assert incoming_channel not in connection._incoming_endpoints