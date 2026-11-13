# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""A broken management or $cbs link pair surfaces its AMQP cause, so the retry policy can classify it."""

import asyncio
import logging
import threading
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.servicebus._pyamqp import cbs, client, management_operation
from azure.servicebus._pyamqp.aio import _cbs_async, _client_async, _management_operation_async
from azure.servicebus._pyamqp.constants import CbsState, LinkState, ManagementLinkState, ManagementOpenResult
from azure.servicebus._pyamqp.error import AMQPConnectionError, AMQPLinkError, ErrorCondition
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus.exceptions import (
    ServiceBusAuthorizationError,
    ServiceBusConnectionError,
    ServiceBusServerBusyError,
)

_LOGGER = logging.getLogger(__name__)
DETACH_FORCED = AMQPLinkError(condition=ErrorCondition.LinkDetachForced, description="idle")
UNAUTHORIZED = AMQPLinkError(condition=ErrorCondition.UnauthorizedAccess, description="token revoked")
CONNECTION_FORCED = AMQPConnectionError(condition=ErrorCondition.ConnectionCloseForced, description="gateway restart")
SERVER_BUSY = AMQPLinkError(condition=b"com.microsoft:server-busy", description="busy")
# What Link._incoming_detach records for a detach without an error.
DETACHED_WITHOUT_ERROR = AMQPLinkError(
    condition=ErrorCondition.UnknownError, description="Link detached unexpectedly.", retryable=True
)


def _stub_link(asynchronous):
    link = MagicMock(_error=None)
    if asynchronous:
        link.attach, link.detach = AsyncMock(), AsyncMock()
    return link


def _session(asynchronous):
    """A session whose request/response link pair is a real ManagementLink over stub links."""
    from azure.servicebus._pyamqp.aio._management_link_async import ManagementLink as AsyncManagementLink
    from azure.servicebus._pyamqp.management_link import ManagementLink

    link_cls = AsyncManagementLink if asynchronous else ManagementLink
    session = MagicMock()
    session._connection._error = None
    session.create_sender_link.side_effect = lambda *_, **__: _stub_link(asynchronous)
    session.create_receiver_link.side_effect = lambda *_, **__: _stub_link(asynchronous)
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
    "link_error, expected",
    [
        (DETACH_FORCED, (ServiceBusConnectionError, True)),
        (UNAUTHORIZED, (ServiceBusAuthorizationError, False)),
        (None, (ServiceBusConnectionError, True)),
    ],
)
async def test_broken_cbs_link_raises_instead_of_waiting_forever(asynchronous, link_error, expected):
    module = _cbs_async if asynchronous else cbs
    authenticator = module.CBSAuthenticator(_session(asynchronous), MagicMock(), auth_timeout=0)
    authenticator.state = CbsState.ERROR
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
async def test_failed_management_link_is_evicted_and_reopened(asynchronous, monkeypatch):
    module = _client_async if asynchronous else client
    operation_cls = module.ManagementOperation
    created = []

    def create_operation(session, **kwargs):
        created.append(operation_cls(session, **kwargs))
        return created[-1]

    def listen(**_):
        if len(created) == 1:  # The peer detaches the first link pair with a retryable server-busy.
            created[0]._mgmt_link._request_link._error = SERVER_BUSY
            return _break_link_pair(created[0]._mgmt_link)
        raise TimeoutError("slow")  # Not a link failure: the fresh operation stays cached.

    async def listen_async(**kwargs):
        broken = listen(**kwargs)
        if broken:
            await broken

    monkeypatch.setattr(module, "ManagementOperation", create_operation)
    client_cls = module.AMQPClientAsync if asynchronous else module.AMQPClient
    amqp_client = client_cls.__new__(client_cls)  # Only the state mgmt_request uses.
    amqp_client._mgmt_links = {}
    amqp_client._session = _session(asynchronous)
    if asynchronous:
        amqp_client._mgmt_link_lock_async = asyncio.Lock()
        amqp_client.auth_complete_async = AsyncMock(return_value=True)
        amqp_client._connection = MagicMock(listen=listen_async)
    else:
        amqp_client._mgmt_link_lock = threading.Lock()
        amqp_client.auth_complete = MagicMock(return_value=True)
        amqp_client._connection = MagicMock(listen=listen)

    async def mgmt_request():
        if asynchronous:
            return await amqp_client.mgmt_request_async(MagicMock())
        return amqp_client.mgmt_request(MagicMock())

    with pytest.raises(AMQPLinkError) as raised:
        await mgmt_request()
    assert raised.value is SERVER_BUSY
    assert _classify(raised.value) == (ServiceBusServerBusyError, True)
    assert amqp_client._mgmt_links == {}
    assert created[0]._mgmt_link.state == ManagementLinkState.IDLE

    with pytest.raises(TimeoutError):
        await mgmt_request()
    assert len(created) == 2
    assert amqp_client._mgmt_links == {"$management": created[1]}


@pytest.mark.parametrize("asynchronous", [False, True])
def test_failure_cause_prefers_a_specific_condition(asynchronous):
    link = _session(asynchronous).create_request_response_link_pair("$management")
    link._request_link._error = DETACHED_WITHOUT_ERROR
    link._response_link._error = UNAUTHORIZED
    assert link.failure_cause() is UNAUTHORIZED

    link._response_link._error = None
    assert link.failure_cause() is DETACHED_WITHOUT_ERROR
