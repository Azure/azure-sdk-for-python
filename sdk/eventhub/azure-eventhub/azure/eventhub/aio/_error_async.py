# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import logging

from uamqp import errors, compat  # type: ignore

from ..exceptions import (
    _create_eventhub_exception,
    EventHubError,
    EventDataSendError,
    EventDataError
)

_LOGGER = logging.getLogger(__name__)


async def _handle_exception(exception, closable):  # pylint:disable=too-many-branches, too-many-statements
    if isinstance(exception, asyncio.CancelledError):
        raise exception
    try:
        name = closable._name  # pylint: disable=protected-access
    except AttributeError:
        name = closable._container_id  # pylint: disable=protected-access
    if isinstance(exception, KeyboardInterrupt):  # pylint:disable=no-else-raise
        _LOGGER.info("%r stops due to keyboard interrupt", name)
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
        _LOGGER.info("%r Event data error (%r)", name, exception)
        error = EventDataError(str(exception), exception)
        raise error
    elif isinstance(exception, errors.MessageException):
        _LOGGER.info("%r Event data send error (%r)", name, exception)
        error = EventDataSendError(str(exception), exception)
        raise error
    else:
        if isinstance(exception, errors.AuthenticationException):
            if hasattr(closable, "_close_connection_async"):
                await closable._close_connection_async()  # pylint:disable=protected-access
        elif isinstance(exception, errors.LinkDetach):
            if hasattr(closable, "_close_handler_async"):
                await closable._close_handler_async()  # pylint:disable=protected-access
        elif isinstance(exception, errors.ConnectionClose):
            if hasattr(closable, "_close_connection_async"):
                await closable._close_connection_async()  # pylint:disable=protected-access
        elif isinstance(exception, errors.MessageHandlerError):
            if hasattr(closable, "_close_handler_async"):
                await closable._close_handler_async()  # pylint:disable=protected-access
        elif isinstance(exception, errors.AMQPConnectionError):
            if hasattr(closable, "_close_connection_async"):
                await closable._close_connection_async()  # pylint:disable=protected-access
        elif isinstance(exception, compat.TimeoutException):
            pass  # Timeout doesn't need to recreate link or connection to retry
        else:
            if hasattr(closable, "_close_connection_async"):
                await closable._close_connection_async()  # pylint:disable=protected-access
        return _create_eventhub_exception(exception)
