# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import logging
from typing import TYPE_CHECKING, Union, cast

from uamqp import errors

from ..exceptions import (
    _create_eventhub_exception,
    EventHubError,
    EventDataSendError,
    EventDataError,
)

if TYPE_CHECKING:
    from ._client_base_async import ClientBaseAsync, ConsumerProducerMixin

_LOGGER = logging.getLogger(__name__)


async def _handle_exception(  # pylint:disable=too-many-branches, too-many-statements
    exception: Exception, closable: Union["ClientBaseAsync", "ConsumerProducerMixin"]
) -> Exception:
    # pylint: disable=protected-access
    if isinstance(exception, asyncio.CancelledError):
        raise exception
    error = exception
    try:
        name = cast("ConsumerProducerMixin", closable)._name
    except AttributeError:
        name = cast("ClientBaseAsync", closable)._container_id
    if isinstance(exception, KeyboardInterrupt):  # pylint:disable=no-else-raise
        _LOGGER.info("%r stops due to keyboard interrupt", name)
        await cast("ConsumerProducerMixin", closable)._close_connection_async()
        raise error
    elif isinstance(exception, EventHubError):
        await cast("ConsumerProducerMixin", closable)._close_handler_async()
        raise error
    elif isinstance(
        exception,
        (
            errors.MessageAccepted,
            errors.MessageAlreadySettled,
            errors.MessageModified,
            errors.MessageRejected,
            errors.MessageReleased,
            errors.MessageContentTooLarge,
        ),
    ):
        _LOGGER.info("%r Event data error (%r)", name, exception)
        error = EventDataError(str(exception), exception)
        raise error
    elif isinstance(exception, errors.MessageException):
        _LOGGER.info("%r Event data send error (%r)", name, exception)
        error = EventDataSendError(str(exception), exception)
        raise error
    else:
        try:
            if isinstance(exception, errors.AuthenticationException):
                await closable._close_connection_async()
            elif isinstance(exception, errors.LinkDetach):
                await cast("ConsumerProducerMixin", closable)._close_handler_async()
            elif isinstance(exception, errors.ConnectionClose):
                await closable._close_connection_async()
            elif isinstance(exception, errors.MessageHandlerError):
                await cast("ConsumerProducerMixin", closable)._close_handler_async()
            else:  # errors.AMQPConnectionError, compat.TimeoutException, and any other errors
                await closable._close_connection_async()
        except AttributeError:
            pass
        return _create_eventhub_exception(exception)
