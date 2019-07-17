from uamqp import errors, compat
from ..error import EventHubError, EventDataSendError, \
    EventDataError, ConnectError, ConnectionLostError, AuthenticationError


async def _handle_exception(exception, retry_count, max_retries, closable, log):
    type_name = type(closable).__name__
    if isinstance(exception, KeyboardInterrupt):
        log.info("{} stops due to keyboard interrupt".format(type_name))
        await closable.close()
        raise

    elif isinstance(exception, (
            errors.MessageAccepted,
            errors.MessageAlreadySettled,
            errors.MessageModified,
            errors.MessageRejected,
            errors.MessageReleased,
            errors.MessageContentTooLarge)
            ):
        log.error("Event data error (%r)", exception)
        error = EventDataError(str(exception), exception)
        await closable.close(exception)
        raise error
    elif isinstance(exception, errors.MessageException):
        log.error("Event data send error (%r)", exception)
        error = EventDataSendError(str(exception), exception)
        await closable.close(exception)
        raise error
    elif retry_count >= max_retries:
        log.info("{} has an error and has exhausted retrying. (%r)".format(type_name), exception)
        if isinstance(exception, errors.AuthenticationException):
            log.info("{} authentication failed. Shutting down.".format(type_name))
            error = AuthenticationError(str(exception), exception)
        elif isinstance(exception, errors.VendorLinkDetach):
            log.info("{} link detached. Shutting down.".format(type_name))
            error = ConnectError(str(exception), exception)
        elif isinstance(exception, errors.LinkDetach):
            log.info("{} link detached. Shutting down.".format(type_name))
            error = ConnectionLostError(str(exception), exception)
        elif isinstance(exception, errors.ConnectionClose):
            log.info("{} connection closed. Shutting down.".format(type_name))
            error = ConnectionLostError(str(exception), exception)
        elif isinstance(exception, errors.MessageHandlerError):
            log.info("{} detached. Shutting down.".format(type_name))
            error = ConnectionLostError(str(exception), exception)
        elif isinstance(exception, errors.AMQPConnectionError):
            log.info("{} connection lost. Shutting down.".format(type_name))
            error_type = AuthenticationError if str(exception).startswith("Unable to open authentication session") \
                else ConnectError
            error = error_type(str(exception), exception)
        elif isinstance(exception, compat.TimeoutException):
            log.info("{} timed out. Shutting down.".format(type_name))
            error = ConnectionLostError(str(exception), exception)
        else:
            log.error("Unexpected error occurred (%r). Shutting down.", exception)
            error = EventHubError("Receive failed: {}".format(exception), exception)
        await closable.close()
        raise error
    else:
        log.info("{} has an exception (%r). Retrying...".format(type_name), exception)
        if isinstance(exception, errors.AuthenticationException):
            if hasattr(closable, "_close_connection"):
                await closable._close_connection()
        elif isinstance(exception, errors.LinkRedirect):
            log.info("{} link redirected. Redirecting...".format(type_name))
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
