# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import logging

from uamqp import errors, compat  # type: ignore
from ..error import EventHubError, EventDataSendError, \
    EventDataError, ConnectError, ConnectionLostError, AuthenticationError


log = logging.getLogger(__name__)


def _create_eventhub_exception(exception):
    if isinstance(exception, errors.AuthenticationException):
        error = AuthenticationError(str(exception), exception)
    elif isinstance(exception, errors.VendorLinkDetach):
        error = ConnectError(str(exception), exception)
    elif isinstance(exception, errors.LinkDetach):
        error = ConnectionLostError(str(exception), exception)
    elif isinstance(exception, errors.ConnectionClose):
        error = ConnectionLostError(str(exception), exception)
    elif isinstance(exception, errors.MessageHandlerError):
        error = ConnectionLostError(str(exception), exception)
    elif isinstance(exception, errors.AMQPConnectionError):
        error_type = AuthenticationError if str(exception).startswith("Unable to open authentication session") \
            else ConnectError
        error = error_type(str(exception), exception)
    elif isinstance(exception, compat.TimeoutException):
        error = ConnectionLostError(str(exception), exception)
    else:
        error = EventHubError(str(exception), exception)
    return error


async def _handle_exception(exception, closable):  # pylint:disable=too-many-branches, too-many-statements
    if isinstance(exception, asyncio.CancelledError):
        raise exception
    try:
        name = closable._name  # pylint: disable=protected-access
    except AttributeError:
        name = closable._container_id  # pylint: disable=protected-access
    if isinstance(exception, KeyboardInterrupt):  # pylint:disable=no-else-raise
        log.info("%r stops due to keyboard interrupt", name)
        await closable.close()
        raise exception
    elif isinstance(exception, EventHubError):
        await closable.close()
        raise exception
    elif isinstance(exception, (
            errors.MessageAccepted,
            errors.MessageAlreadySettled,
            errors.MessageModified,
            errors.MessageRejected,
            errors.MessageReleased,
            errors.MessageContentTooLarge)
            ):
        log.info("%r Event data error (%r)", name, exception)
        error = EventDataError(str(exception), exception)
        raise error
    elif isinstance(exception, errors.MessageException):
        log.info("%r Event data send error (%r)", name, exception)
        error = EventDataSendError(str(exception), exception)
        raise error
    else:
        if isinstance(exception, errors.AuthenticationException):
            if hasattr(closable, "_close_connection"):
                await closable._close_connection()  # pylint:disable=protected-access
        elif isinstance(exception, errors.LinkDetach):
            if hasattr(closable, "_close_handler"):
                await closable._close_handler()  # pylint:disable=protected-access
        elif isinstance(exception, errors.ConnectionClose):
            if hasattr(closable, "_close_connection"):
                await closable._close_connection()  # pylint:disable=protected-access
        elif isinstance(exception, errors.MessageHandlerError):
            if hasattr(closable, "_close_handler"):
                await closable._close_handler()  # pylint:disable=protected-access
        elif isinstance(exception, errors.AMQPConnectionError):
            if hasattr(closable, "_close_connection"):
                await closable._close_connection()  # pylint:disable=protected-access
        elif isinstance(exception, compat.TimeoutException):
            pass  # Timeout doesn't need to recreate link or connection to retry
        else:
            if hasattr(closable, "_close_connection"):
                await closable._close_connection()  # pylint:disable=protected-access
        return _create_eventhub_exception(exception)
