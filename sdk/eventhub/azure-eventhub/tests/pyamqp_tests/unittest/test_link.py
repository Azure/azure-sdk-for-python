from unittest.mock import Mock
from azure.eventhub._pyamqp.error import AMQPLinkError
from azure.eventhub._pyamqp.link import Link
from azure.eventhub._pyamqp.receiver import ReceiverLink
from azure.eventhub._pyamqp.constants import LinkState
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



