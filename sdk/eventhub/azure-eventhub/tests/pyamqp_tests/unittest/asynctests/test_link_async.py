import asyncio
import sys

if sys.version_info >= (3, 8, 0):
    from unittest.mock import AsyncMock
from azure.eventhub._pyamqp.aio import Link
from azure.eventhub._pyamqp.constants import LinkState
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "start_state,expected_state",
    [
        (LinkState.ATTACHED, LinkState.DETACH_SENT),
        (LinkState.ATTACH_SENT, LinkState.DETACHED),
        (LinkState.ATTACH_RCVD, LinkState.DETACHED),
    ],
    ids=["link attached", "link attach sent", "link attach rcvd"],
)
async def test_link_should_detach(start_state, expected_state):
    if sys.version_info < (3, 8, 0):
        pytest.skip("AsyncMock is not available in Python 3.7")
    session = AsyncMock()
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

    await link._set_state(start_state)
    link._outgoing_detach = AsyncMock(return_value=None)
    await link.detach()

    assert link.state == expected_state


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "state",
    [LinkState.DETACHED, LinkState.DETACH_SENT, LinkState.ERROR],
    ids=["link detached", "link detach sent", "link error"],
)
async def test_link_should_not_detach(state):
    if sys.version_info < (3, 8, 0):
        pytest.skip("AsyncMock is not available in Python 3.7")
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

    await link._set_state(state)
    link._outgoing_detach = AsyncMock(return_value=None)
    await link.detach()
    link._outgoing_detach.assert_not_called()
