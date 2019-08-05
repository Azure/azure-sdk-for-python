import asyncio
import time
import logging

from uamqp import errors, compat
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


async def _handle_exception(exception, retry_count, max_retries, closable, timeout_time=None):
    if isinstance(exception, asyncio.CancelledError):
        raise
    try:
        name = closable.name
    except AttributeError:
        name = closable.container_id
    if isinstance(exception, KeyboardInterrupt):
        log.info("%r stops due to keyboard interrupt", name)
        closable.close()
        raise
    elif isinstance(exception, EventHubError):
        closable.close()
        raise
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
    elif retry_count >= max_retries:
        error = _create_eventhub_exception(exception)
        log.info("%r has exhausted retry. Exception still occurs (%r)", name, exception)
        raise error
    else:
        if isinstance(exception, errors.AuthenticationException):
            if hasattr(closable, "_close_connection"):
                await closable._close_connection()
        elif isinstance(exception, errors.LinkRedirect):
            log.info("%r link redirect received. Redirecting...", name)
            redirect = exception
            if hasattr(closable, "_redirect"):
                await closable._redirect(redirect)
        elif isinstance(exception, errors.LinkDetach):
            if hasattr(closable, "_close_handler"):
                await closable._close_handler()
        elif isinstance(exception, errors.ConnectionClose):
            if hasattr(closable, "_close_connection"):
                await closable._close_connection()
        elif isinstance(exception, errors.MessageHandlerError):
            if hasattr(closable, "_close_handler"):
                await closable._close_handler()
        elif isinstance(exception, errors.AMQPConnectionError):
            if hasattr(closable, "_close_connection"):
                await closable._close_connection()
        elif isinstance(exception, compat.TimeoutException):
            pass  # Timeout doesn't need to recreate link or connection to retry
        else:
            if hasattr(closable, "_close_connection"):
                await closable._close_connection()
        # start processing retry delay
        try:
            backoff_factor = closable.client.config.backoff_factor
            backoff_max = closable.client.config.backoff_max
        except AttributeError:
            backoff_factor = closable.config.backoff_factor
            backoff_max = closable.config.backoff_max
        backoff = backoff_factor * 2 ** retry_count
        if backoff <= backoff_max and (timeout_time is None or time.time() + backoff <= timeout_time):
            await asyncio.sleep(backoff)
            log.info("%r has an exception (%r). Retrying...", format(name), exception)
            return _create_eventhub_exception(exception)
        else:
            error = _create_eventhub_exception(exception)
            log.info("%r operation has timed out. Last exception before timeout is (%r)", name, error)
            raise error
        # end of processing retry delay