from unittest.mock import Mock
from azure.eventhub._pyamqp import Connection


def test_connection_end_session_on_timeout():
    connection = Connection("fake.host.com")
    connection._process_outgoing_frame = Mock(return_value=None)
    # create session on the Connection
    session = connection.create_session(network_trace=False)
    outgoing_channel = session.channel
    # after a BEGIN response from the server set up incoming endpoint
    incoming_channel = 0
    connection._incoming_endpoints[incoming_channel] = session
    assert outgoing_channel == connection._incoming_endpoints[incoming_channel].channel
    # typically after some inactivity(60,000 ms) on the connection, the server will force close a connection
    # and will send across an END frame
    connection._incoming_end(incoming_channel, None)
    # end points dont have the channels anymore and Session link is gone.
    assert outgoing_channel not in connection._outgoing_endpoints
    assert incoming_channel not in connection._incoming_endpoints