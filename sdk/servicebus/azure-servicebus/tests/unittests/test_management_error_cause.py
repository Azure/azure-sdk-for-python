# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""A broken management or $cbs link pair surfaces its AMQP cause, so the retry policy can classify it."""

import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.servicebus._pyamqp import cbs, management_operation
from azure.servicebus._pyamqp.aio import _cbs_async, _management_operation_async
from azure.servicebus._pyamqp.constants import CbsState, LinkState, ManagementLinkState, ManagementOpenResult
from azure.servicebus._pyamqp.error import AMQPConnectionError, AMQPLinkError, ErrorCondition
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus.exceptions import (
    ServiceBusAuthorizationError,
    ServiceBusConnectionError,
)

_LOGGER = logging.getLogger(__name__)
DETACH_FORCED = AMQPLinkError(condition=ErrorCondition.LinkDetachForced, description="idle")
UNAUTHORIZED = AMQPLinkError(condition=ErrorCondition.UnauthorizedAccess, description="token revoked")
CONNECTION_FORCED = AMQPConnectionError(condition=ErrorCondition.ConnectionCloseForced, description="gateway restart")


def _session(asynchronous):
    """A session whose request/response link pair is a real ManagementLink over stub links."""
    from azure.servicebus._pyamqp.aio._management_link_async import ManagementLink as AsyncManagementLink
    from azure.servicebus._pyamqp.management_link import ManagementLink

    link_cls = AsyncManagementLink if asynchronous else ManagementLink
    session = MagicMock()
    session._connection._error = None
    session.create_sender_link.return_value = MagicMock(_error=None)
    session.create_receiver_link.return_value = MagicMock(_error=None)
    session.create_request_response_link_pair.side_effect = lambda endpoint, **kw: link_cls(session, endpoint, **kw)
    return session


def _break_link_pair(link):
    """The peer detached the request link of an open pair (as Link._incoming_detach reports it).

    Returns the callback's coroutine for the async link, None for the sync one.
    """
    link.state = ManagementLinkState.OPEN
    return link._on_sender_state_change(LinkState.ATTACHED, LinkState.ERROR)


def _classify(error):
    sb_error = PyamqpTransport.create_servicebus_exception(_LOGGER, error)
    return type(sb_error), sb_error._retryable


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "link_error, connection_error, expected",
    [
        (DETACH_FORCED, None, (ServiceBusConnectionError, True)),
        (UNAUTHORIZED, None, (ServiceBusAuthorizationError, False)),
        (None, CONNECTION_FORCED, (ServiceBusConnectionError, True)),
        (None, None, (ServiceBusConnectionError, True)),
    ],
)
async def test_broken_management_link_raises_its_cause(asynchronous, link_error, connection_error, expected):
    module = _management_operation_async if asynchronous else management_operation
    session = _session(asynchronous)
    operation = module.ManagementOperation(session)
    operation._mgmt_link_open_status = ManagementOpenResult.OK
    operation._mgmt_link._request_link._error = link_error

    broken = _break_link_pair(operation._mgmt_link)
    if asynchronous:
        await broken
    # A connection Close records its error only after its links changed state; it must still be found.
    session._connection._error = connection_error

    with pytest.raises((AMQPLinkError, AMQPConnectionError)) as raised:
        if asynchronous:
            await operation.ready()
        else:
            operation.ready()

    if link_error or connection_error:
        assert raised.value is (link_error or connection_error)
    assert _classify(raised.value) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_link_failure_during_pending_request_raises_its_cause(asynchronous):
    module = _management_operation_async if asynchronous else management_operation
    session = _session(asynchronous)
    operation = module.ManagementOperation(session)
    link = operation._mgmt_link

    def detach_while_waiting(*_, **__):
        link._request_link._error = DETACH_FORCED
        return _break_link_pair(link)

    if asynchronous:
        link.execute_operation = AsyncMock(return_value=None)

        async def detach_while_waiting_async(*_, **__):
            await detach_while_waiting()

        session._connection.listen = AsyncMock(side_effect=detach_while_waiting_async)
        with pytest.raises(AMQPLinkError) as raised:
            await operation.execute(MagicMock(), timeout=5)
    else:
        link.execute_operation = MagicMock(return_value=None)
        session._connection.listen.side_effect = detach_while_waiting
        with pytest.raises(AMQPLinkError) as raised:
            operation.execute(MagicMock(), timeout=5)

    assert raised.value is DETACH_FORCED
    assert operation._responses == {}


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "state, link_error, expected",
    [
        (CbsState.ERROR, DETACH_FORCED, (ServiceBusConnectionError, True)),
        (CbsState.ERROR, UNAUTHORIZED, (ServiceBusAuthorizationError, False)),
        (CbsState.ERROR, None, (ServiceBusConnectionError, True)),
        (CbsState.CLOSED, UNAUTHORIZED, (ServiceBusAuthorizationError, False)),
    ],
)
async def test_broken_cbs_link_raises_instead_of_waiting_forever(asynchronous, state, link_error, expected):
    module = _cbs_async if asynchronous else cbs
    authenticator = module.CBSAuthenticator(_session(asynchronous), MagicMock(), auth_timeout=0)
    authenticator.state = state
    authenticator._mgmt_link._response_link._error = link_error

    with pytest.raises(AMQPLinkError) as raised:
        if asynchronous:
            await authenticator.handle_token()
        else:
            authenticator.handle_token()

    if link_error:
        assert raised.value is link_error
    assert _classify(raised.value) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_opening_cbs_link_keeps_waiting(asynchronous):
    module = _cbs_async if asynchronous else cbs
    authenticator = module.CBSAuthenticator(_session(asynchronous), MagicMock(), auth_timeout=0)
    authenticator.state = CbsState.OPENING

    ready = await authenticator._cbs_link_ready() if asynchronous else authenticator._cbs_link_ready()

    assert ready is False
