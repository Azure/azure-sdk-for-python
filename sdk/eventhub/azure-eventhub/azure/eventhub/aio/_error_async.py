# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import logging
from typing import TYPE_CHECKING, Union, cast

from ..exceptions import (
    _create_eventhub_exception,
    EventHubError,
    EventDataSendError,
    EventDataError,
)

from .._pyamqp import error as errors

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
    # TODO: The following errors seem to be useless in EH
    # elif isinstance(
    #     exception,
    #     (
    #         errors.MessageAccepted,
    #         errors.MessageAlreadySettled,
    #         errors.MessageModified,
    #         errors.MessageRejected,
    #         errors.MessageReleased,
    #         errors.MessageContentTooLarge,
    #     ),
    # ):
    #     _LOGGER.info("%r Event data error (%r)", name, exception)
    #     error = EventDataError(str(exception), exception)
    #     raise error
    elif isinstance(exception, errors.MessageException):
        _LOGGER.info("%r Event data send error (%r)", name, exception)
        error = EventDataSendError(str(exception), exception)
        raise error
    else:
        try:
            if isinstance(exception, errors.AuthenticationException):
                await closable._close_connection_async()  # pylint:disable=protected-access
            elif isinstance(exception, errors.AMQPLinkError):
                await closable._close_handler_async()  # pylint:disable=protected-access
            elif isinstance(exception, errors.AMQPConnectionError):
                await closable._close_connection_async()  # pylint:disable=protected-access
            # TODO: add MessageHandlerError in amqp?
            # elif isinstance(exception, errors.MessageHandlerError):
            #     if hasattr(closable, "_close_handler"):
            #         closable._close_handler()  # pylint:disable=protected-access
            else:  # errors.AMQPConnectionError, compat.TimeoutException
                await closable._close_connection_async()  # pylint:disable=protected-access
            return _create_eventhub_exception(exception)
        except AttributeError:
            pass
        return _create_eventhub_exception(exception)
