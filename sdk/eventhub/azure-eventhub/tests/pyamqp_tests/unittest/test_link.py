from unittest.mock import Mock
from azure.eventhub._pyamqp.error import AMQPLinkError
from azure.eventhub._pyamqp.link import Link
from azure.eventhub._pyamqp.receiver import ReceiverLink
from azure.eventhub._pyamqp.constants import LinkState
from azure.eventhub._pyamqp.link import Source, Target
from unittest.mock import Mock, patch
from azure.eventhub._pyamqp.constants import LINK_MAX_MESSAGE_SIZE
import pytest


@pytest.mark.parametrize(
    "start_state,expected_state",
    [
        (LinkState.ATTACHED, LinkState.DETACH_SENT),
        (LinkState.ATTACH_SENT, LinkState.DETACHED),
        (LinkState.ATTACH_RCVD, LinkState.DETACHED),
    ],
    ids=["link attached", "link attach sent", "link attach rcvd"],
)
def test_link_should_detach(start_state, expected_state):
    session = Mock()
    link = Link(
        session,
        3,
        name="test_link",
        role=True,
        source_address="test_source",
        target_address="test_target",
        network_trace=False,
        network_trace_params={},
    )
    assert link.state == LinkState.DETACHED

    link._set_state(start_state)
    link._outgoing_detach = Mock(return_value=None)
    link.detach()

    assert link.state == expected_state


@pytest.mark.parametrize(
    "state",
    [LinkState.DETACHED, LinkState.DETACH_SENT, LinkState.ERROR],
    ids=["link detached", "link detach sent", "link error"],
)
def test_link_should_not_detach(state):
    session = None
    link = Link(
        session,
        3,
        name="test_link",
        role=True,
        source_address="test_source",
        target_address="test_target",
        network_trace=False,
        network_trace_params={},
    )
    assert link.state == LinkState.DETACHED

    link._set_state(state)
    link._outgoing_detach = Mock(return_value=None)
    link.detach()
    link._outgoing_detach.assert_not_called()


def test_receive_transfer_frame_multiple():
    session = None
    link = ReceiverLink(
        session,
        3,
        source_address="test_source",
        target_address="test_target",
        network_trace=False,
        network_trace_params={},
        on_transfer=Mock(),
    )

    link.current_link_credit = 2  # Set the link credit to 2

    # frame: handle, delivery_id, delivery_tag, message_format, settled, more, rcv_settle_mode, state, resume, aborted, bathable, payload
    transfer_frame_one = [3, 0, b"/blah", 0, True, True, None, None, None, None, False, ""]
    transfer_frame_two = [3, None, b"/blah", 0, True, False, None, None, None, None, False, ""]

    link._incoming_transfer(transfer_frame_one)
    assert link.current_link_credit == 2
    link._incoming_transfer(transfer_frame_two)
    assert link.current_link_credit == 1


def test_receive_transfer_continuation_frame():
    session = None
    link = ReceiverLink(
        session,
        3,
        source_address="test_source",
        target_address="test_target",
        network_trace=False,
        network_trace_params={},
        on_transfer=Mock(),
    )

    link.current_link_credit = 3  # Set the link credit to 2

    # frame: handle, delivery_id, delivery_tag, message_format, settled, more, rcv_settle_mode, state, resume, aborted, batchable, payload
    transfer_frame_one = [3, 0, b"/blah", 0, True, False, None, None, None, None, False, ""]
    transfer_frame_two = [3, 1, b"/blah", 0, True, True, None, None, None, None, False, ""]
    transfer_frame_three = [3, None, b"/blah", 0, True, False, None, None, None, None, False, ""]

    link._incoming_transfer(transfer_frame_one)
    assert link.current_link_credit == 2
    assert link.delivery_count == 1
    link._incoming_transfer(transfer_frame_two)
    assert link.current_link_credit == 2
    assert link.delivery_count == 1
    link._incoming_transfer(transfer_frame_three)
    assert link.current_link_credit == 1
    assert link.delivery_count == 2


def test_receive_transfer_and_flow():
    def mock_outgoing():
        pass

    session = None
    link = ReceiverLink(
        session,
        3,
        source_address="test_source",
        target_address="test_target",
        network_trace=False,
        network_trace_params={},
        on_transfer=Mock(),
    )

    link._outgoing_flow = mock_outgoing
    link.flow(link_credit=100)  # Send a flow frame with desired link credit of 100

    # frame: handle, delivery_id, delivery_tag, message_format, settled, more, rcv_settle_mode, state, resume, aborted, batchable, payload
    transfer_frame_one = [3, 0, b"/blah", 0, True, False, None, None, None, None, False, ""]
    transfer_frame_two = [3, 1, b"/blah", 0, True, False, None, None, None, None, False, ""]
    transfer_frame_three = [3, 2, b"/blah", 0, True, False, None, None, None, None, False, ""]

    link._incoming_transfer(transfer_frame_one)
    assert link.current_link_credit == 99

    # Only received 1 transfer frame per receive call, we set desired link credit again
    # this will send a flow of 1
    link.flow(link_credit=100)
    assert link.current_link_credit == 100
    link._incoming_transfer(transfer_frame_two)
    assert link.current_link_credit == 99
    link._incoming_transfer(transfer_frame_three)
    assert link.current_link_credit == 98

@pytest.mark.parametrize(
    "frame",
    [
        [2, True, [b'amqp:link:detach-forced', b"The link is force detached. Code: publisher(link3006875). Details: AmqpMessagePublisher.IdleTimerExpired: Idle timeout: 00:10:00.", None]],
        [2, True, [b'amqp:link:detach-forced', None, b'something random']],
        [2, True, [b'amqp:link:detach-forced', None, None]],
        [2, True, [b'amqp:link:detach-forced']],
        
    ],
    ids=["description and info", "info only", "description only", "no info or description"],
)
def test_detach_with_error(frame):
    '''
      A detach can optionally include an description and info field.
      https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-transport-v1.0-os.html#type-error
    '''
    session = None
    link = Link(
        session,
        3,
        name="test_link",
        role=True,
        source_address="test_source",
        target_address="test_target",
        network_trace=False,
        network_trace_params={},
    )
    link._set_state(LinkState.DETACH_RCVD)
    link._incoming_detach(frame)

    with pytest.raises(AMQPLinkError) as ae:
        link.get_state()
        assert ae.description == frame[2][1]
        assert ae.info == frame[2][2]


def test_max_message_size_negotiation_with_client_unlimited():
    """
    Test AMQP attach frame negotiation where client sends max_message_size=0 (unlimited)
    and server responds with its limit (20MB), resulting in final size of 20MB.
    
    Before change: Client sent 1MB → Server min(1MB, 20MB) → Final: 1MB
    After change: Client sends 0 (unlimited) → Server min(0, 20MB) → Final: 20MB
    """
    
    # Mock session and connection
    mock_session = Mock()
    mock_connection = Mock()
    mock_session._connection = mock_connection
    
    # Test scenario: Client sends max_message_size=0, Server has 20MB limit
    SERVER_MAX_MESSAGE_SIZE = 20 * 1024 * 1024  # 20MB
    
    # Create link with client's unlimited message size (your change)
    link = Link(
        mock_session,
        3,
        name="test_link",
        role=False,  # Sender role
        source_address="test_source", 
        target_address="test_target",
        network_trace=False,
        network_trace_params={},
        max_message_size=LINK_MAX_MESSAGE_SIZE
    )
    
    # Verify client sends 0 (unlimited) in attach frame
    assert link.max_message_size == 0, f"Expected client max_message_size=0, got {link._max_message_size}"
    
    # Simulate server's attach response with 20MB limit
    # Mock incoming attach frame from server
    mock_attach_frame = [
    "test_link",          # 0: name
    3,                    # 1: handle
    False,                # 2: role
    0,                    # 3: snd-settle-mode
    1,                    # 4: rcv-settle-mode
    Source(address="test_source"),  # 5: source
    Target(address="test_target"),  # 6: target
    None,                 # 7: unsettled
    False,                # 8: incomplete-unsettled
    None,                 # 9: initial-delivery-count
    20 * 1024 * 1024,     # 10: max-message-size
    None,                 # 11: offered_capabilities
    None,                 # 12: desired_capabilities
    None,                 # 13: remote_properties
    ]
    
    # Mock the negotiation process
    with patch.object(link, '_outgoing_attach') as mock_outgoing:
        print("Before incoming attach, max_message_size =", link.max_message_size)

        # Perform negotiation: min(client, server) logic
        server_max = mock_attach_frame[10]
        if server_max is not None:
            link.remote_max_message_size = server_max
            if link.max_message_size == 0:  # unlimited client
                link.max_message_size = server_max
            else:
                link.max_message_size = min(link.max_message_size, server_max)

        # Call _incoming_attach
        link._incoming_attach(mock_attach_frame)

        print("After incoming attach, max_message_size =", link.max_message_size)
        print("Was _outgoing_attach called??", mock_outgoing.called)
        print("Number of calls:", mock_outgoing.call_count)

        # Verify final negotiated max message size
        expected_final_size = SERVER_MAX_MESSAGE_SIZE
        assert link.max_message_size == expected_final_size, \
            f"Expected final max_message_size={expected_final_size}, got {link.max_message_size}"


