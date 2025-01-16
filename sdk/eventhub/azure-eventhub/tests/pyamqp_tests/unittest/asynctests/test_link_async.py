import asyncio
import sys

from azure.eventhub._pyamqp.error import AMQPLinkError

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

@pytest.mark.asyncio
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
async def test_detach_with_error(frame):
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
    await link._set_state(LinkState.DETACH_RCVD)
    await link._incoming_detach(frame)

    with pytest.raises(AMQPLinkError) as ae:
        await link.get_state()
        assert ae.description == frame[2][1]
        assert ae.info == frame[2][2]