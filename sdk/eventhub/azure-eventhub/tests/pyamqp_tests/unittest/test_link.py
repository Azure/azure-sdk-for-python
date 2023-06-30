from unittest.mock import Mock
from azure.eventhub._pyamqp.link import Link
from azure.eventhub._pyamqp.constants import LinkState
import pytest


@pytest.mark.parametrize("state", [LinkState.ATTACHED, LinkState.ERROR], ids=["link attached", "link error"])
def test_link_should_detach(state):
    session = Mock()
    link = Link(
        session, 
        3, 
        name="test_link", 
        role=True, 
        source_address="test_source", 
        target_address="test_target",
        network_trace=False,
        network_trace_params={})
    assert link.state == LinkState.DETACHED
    
    # lets pretend the link gets attached
    link._set_state(state)
    link._outgoing_detach = Mock(return_value=None)
    link.detach()

    assert link.state == LinkState.DETACH_SENT


@pytest.mark.parametrize("state", [LinkState.DETACHED, LinkState.DETACH_SENT], ids=["link detached", "link detach sent"])
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
        network_trace_params={})
    assert link.state == LinkState.DETACHED
    
    # lets pretend the link gets in to an error state
    link._set_state(state)
    link._outgoing_detach = Mock(return_value=None)
    link.detach()
    link._outgoing_detach.assert_not_called()