from unittest.mock import Mock
from azure.eventhub._pyamqp import Connection


def test_connection_begin_session():
    connection = Connection("sb://fake.host.com")
    connection._process_outgoing_frame = Mock(return_value=None)
    # create session on the Connection
    session = connection.create_session(network_trace=False)
    outgoing_channel = session.channel
    # mock starting a begin session to the server
    session.begin = Mock(return_value=None)
    session.begin()
    # in response from the server we should get back a BEGIN frame
    incoming_channel = 0
    incoming_frame = (1, 0, 0, 0, 0, 0, 0, 0)
    connection.listen = Mock(side_effect=connection._incoming_begin(incoming_channel, incoming_frame))
    connection.listen()
    assert incoming_channel in connection._incoming_endpoints
    assert outgoing_channel in connection._outgoing_endpoints
    assert outgoing_channel == connection._incoming_endpoints[incoming_channel].channel
    assert connection._incoming_endpoints[incoming_channel] == connection._outgoing_endpoints[outgoing_channel]


def test_connection_end_session_on_timeout():
    connection = Connection("sb://fake.host.com")
    connection._process_outgoing_frame = Mock(return_value=None)
    # create session on the Connection
    session = connection.create_session(network_trace=False)
    outgoing_channel = session.channel
    # mock starting a begin session to the server
    session.begin = Mock(return_value=None)
    session.begin()
    # in response from the server we should get back a BEGIN frame
    incoming_channel = 0
    incoming_frame = (1, 0, 0, 0, 0, 0, 0, 0)
    connection.listen = Mock(side_effect=connection._incoming_begin(incoming_channel, incoming_frame))
    connection.listen()
    assert outgoing_channel == connection._incoming_endpoints[incoming_channel].channel
    # typically after some inactivity(60,000 ms) on the connection, the server will force close a connection
    # and will send across an END frame
    connection.listen = Mock(side_effect=connection._incoming_end(incoming_channel, None))
    connection.listen()
    # end points dont have the channels anymore and Session link is gone.
    assert outgoing_channel not in connection._outgoing_endpoints
    assert incoming_channel not in connection._incoming_endpoints
