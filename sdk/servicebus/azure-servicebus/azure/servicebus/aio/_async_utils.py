# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import sys

import asyncio  # pylint:disable=do-not-import-asyncio
import logging
import functools

from .._common.constants import JWT_TOKEN_SCOPE, TOKEN_TYPE_JWT, TOKEN_TYPE_SASTOKEN
from .._common.utils import get_time_until_deadline
from ..exceptions import OperationTimeoutError

_log = logging.getLogger(__name__)


def get_running_loop():
    try:
        return asyncio.get_running_loop()
    except AttributeError:  # 3.5 / 3.6
        loop = None
        try:
            loop = asyncio._get_running_loop()  # pylint: disable=protected-access
        except AttributeError:
            _log.warning("This version of Python is deprecated, please upgrade to >= v3.5.3")
        if loop is None:
            _log.warning("No running event loop")
            loop = asyncio.get_event_loop()
        return loop
    except RuntimeError:
        # For backwards compatibility, create new event loop
        _log.warning("No running event loop")
        return asyncio.get_event_loop()


async def create_authentication(client):
    # pylint: disable=protected-access
    try:
        # ignore mypy's warning because token_type is Optional
        token_type = client._credential.token_type  # type: ignore
    except AttributeError:
        token_type = TOKEN_TYPE_JWT
    if token_type == TOKEN_TYPE_SASTOKEN:
        return await client._amqp_transport.create_token_auth_async(
            client._auth_uri,
            get_token=functools.partial(client._credential.get_token, client._auth_uri),
            token_type=token_type,
            config=client._config,
            update_token=True,
        )
    return await client._amqp_transport.create_token_auth_async(
        client._auth_uri,
        get_token=functools.partial(client._credential.get_token, JWT_TOKEN_SCOPE),
        token_type=token_type,
        config=client._config,
        update_token=False,
    )


def get_dict_with_loop_if_needed(loop):
    if sys.version_info >= (3, 10):
        if loop:
            raise ValueError("Starting Python 3.10, asyncio no longer supports loop as a parameter.")
    elif loop:
        return {"loop": loop}
    return {}


async def open_handler_with_deadline(handler, connection, deadline):
    """Open the AMQP handler, cancelling the open itself once the deadline passes.

    The sync path can only check the deadline once `open()` returns, because a blocking
    open cannot be interrupted. An async open can be cancelled, so here the budget bounds
    the open rather than merely detecting an overrun afterwards.

    :param AMQPClientAsync handler: The AMQP client to open.
    :param Connection or None connection: An existing connection to reuse, or None.
    :param float or None deadline: The absolute deadline, or None when unbounded.
    :raises ~azure.servicebus.exceptions.OperationTimeoutError: If the open outlives the deadline.
    """
    if deadline is None:
        await handler.open_async(connection=connection)
        return
    try:
        await asyncio.wait_for(handler.open_async(connection=connection), timeout=get_time_until_deadline(deadline))
    except (asyncio.TimeoutError, TimeoutError):
        raise OperationTimeoutError(message="Timed out waiting for the AMQP link to open.") from None


async def close_handler_with_deadline(handler, deadline):
    """Close a previous AMQP handler, cancelling the close once the deadline passes.

    Closing awaits several shutdown operations - link detach, CBS close, session end and
    connection close - so a stalled handler would otherwise hold link acquisition past the
    attempt budget. The handler is being replaced either way, so a cancelled close only
    leaves state that is about to be discarded.

    :param AMQPClientAsync handler: The AMQP client to close.
    :param float or None deadline: The absolute deadline, or None when unbounded.
    :raises ~azure.servicebus.exceptions.OperationTimeoutError: If the close outlives the deadline.
    """
    if deadline is None:
        await handler.close_async()
        return
    try:
        await asyncio.wait_for(handler.close_async(), timeout=get_time_until_deadline(deadline))
    except (asyncio.TimeoutError, TimeoutError):
        raise OperationTimeoutError(message="Timed out closing the previous AMQP link.") from None


async def close_handler_for_cleanup(close_coro, deadline):
    """Run handler cleanup on an error path, bounded and without hiding the original error.

    The receiver override drains the link before closing, and both steps do network I/O, so
    unbounded cleanup can hold an attempt open long past its budget. Cleanup also runs while
    another exception is propagating: a stall or failure here must not become the error the
    caller sees, so anything raised is logged and dropped.

    :param coroutine close_coro: The cleanup coroutine to await.
    :param float or None deadline: The absolute deadline, or None when unbounded.
    """
    try:
        if deadline is None:
            await close_coro
        else:
            await asyncio.wait_for(close_coro, timeout=get_time_until_deadline(deadline))
    except Exception:  # pylint: disable=broad-except
        _log.warning("Handler cleanup did not complete; preserving the original error.", exc_info=True)


async def await_with_deadline(coro, deadline, timeout_message):
    """Await a coroutine, cancelling it once the deadline passes.

    :param coroutine coro: The coroutine to await.
    :param float or None deadline: The absolute deadline, or None when unbounded.
    :param str timeout_message: Message for the raised error.
    :rtype: any
    :returns: Whatever the coroutine returns.
    :raises ~azure.servicebus.exceptions.OperationTimeoutError: If the await outlives the deadline.
    """
    if deadline is None:
        return await coro
    try:
        return await asyncio.wait_for(coro, timeout=get_time_until_deadline(deadline))
    except (asyncio.TimeoutError, TimeoutError):
        raise OperationTimeoutError(message=timeout_message) from None
