# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Settling on a receive link the service already detached falls back to the management link."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.servicebus._common.constants import MESSAGE_COMPLETE
from azure.servicebus._pyamqp.constants import LinkState
from azure.servicebus._pyamqp.error import AMQPLinkError, ErrorCondition
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus.aio._transport._pyamqp_transport_async import PyamqpTransportAsync

DETACH_FORCED = AMQPLinkError(condition=ErrorCondition.LinkDetachForced, description="idle")


def _receive_handler(is_closed, state, error=None):
    handler = MagicMock(_link=MagicMock(_is_closed=is_closed, state=state, _error=error))
    handler.settle_messages_async = AsyncMock()
    return handler


async def _settle_via_receiver_link(asynchronous, handler):
    message = MagicMock(_delivery_id=1, _delivery_tag=b"tag")
    if asynchronous:
        return await PyamqpTransportAsync.settle_message_via_receiver_link_async(handler, message, MESSAGE_COMPLETE)
    return PyamqpTransport.settle_message_via_receiver_link(handler, message, MESSAGE_COMPLETE)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "is_closed, state, error",
    [
        (True, LinkState.ERROR, DETACH_FORCED),  # the service detached the link with an error
        (True, LinkState.DETACHED, None),
        (False, LinkState.DETACHED, None),  # the session was discarded
    ],
)
async def test_settle_on_detached_receive_link_falls_back_to_management_link(asynchronous, is_closed, state, error):
    # The receiver's _settle_message settles over the management link on RuntimeError.
    handler = _receive_handler(is_closed, state, error)
    with pytest.raises(RuntimeError) as raised:
        await _settle_via_receiver_link(asynchronous, handler)
    assert raised.value.__cause__ is error
    handler.settle_messages.assert_not_called()
    handler.settle_messages_async.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_settle_on_attached_receive_link_uses_the_receive_link(asynchronous):
    handler = _receive_handler(False, LinkState.ATTACHED)
    await _settle_via_receiver_link(asynchronous, handler)
    settle = handler.settle_messages_async if asynchronous else handler.settle_messages
    settle.assert_called_once()
