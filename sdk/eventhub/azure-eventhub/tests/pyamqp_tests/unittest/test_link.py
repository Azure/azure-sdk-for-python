from unittest.mock import Mock
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

# Test to receive transfer frames from the server
def test_receive_transfer_frame_multiple():
    session = None
    link = ReceiverLink(
        session,
        3,
        source_address="test_source",
        target_address="test_target",
        network_trace=False,
        network_trace_params={},
    )

    link.current_link_credit = 2 # Set the link credit to 2

    # frame: handle, delivery_id, delivery_tag, messge_format, settled, more, rcv_settle_mode, state, resume, aborted, bathable, payload
    transfer_frame_one = [3, 0, b'/blah', 0, None, True, None, None, None, False, b"test1"]
    transfer_frame_two = [3, None, b'/blah', 0, None, False, None, None, None, False, b"test2"]

    link._incoming_transfer(transfer_frame_one)
    assert link.current_link_credit == 2
    link._incoming_transfer(transfer_frame_two)
    assert link.current_link_credit == 1
