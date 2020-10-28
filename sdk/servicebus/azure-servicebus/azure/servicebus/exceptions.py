# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Optional, Any

from uamqp import errors, constants
from azure.core.exceptions import AzureError

from ._common.constants import SESSION_LOCK_LOST, SESSION_LOCK_TIMEOUT


_NO_RETRY_ERRORS = (
    constants.ErrorCodes.DecodeError,
    constants.ErrorCodes.LinkMessageSizeExceeded,
    constants.ErrorCodes.NotFound,
    constants.ErrorCodes.NotImplemented,
    constants.ErrorCodes.LinkRedirect,
    constants.ErrorCodes.NotAllowed,
    constants.ErrorCodes.UnauthorizedAccess,
    constants.ErrorCodes.LinkStolen,
    constants.ErrorCodes.ResourceLimitExceeded,
    constants.ErrorCodes.ConnectionRedirect,
    constants.ErrorCodes.PreconditionFailed,
    constants.ErrorCodes.InvalidField,
    constants.ErrorCodes.ResourceDeleted,
    constants.ErrorCodes.IllegalState,
    constants.ErrorCodes.FrameSizeTooSmall,
    constants.ErrorCodes.ConnectionFramingError,
    constants.ErrorCodes.SessionUnattachedHandle,
    constants.ErrorCodes.SessionHandleInUse,
    constants.ErrorCodes.SessionErrantLink,
    constants.ErrorCodes.SessionWindowViolation,
    b"com.microsoft:argument-out-of-range",
    b"com.microsoft:entity-disabled",
    b"com.microsoft:auth-failed",
    b"com.microsoft:precondition-failed",
    b"com.microsoft:argument-error")


_AMQP_SESSION_ERROR_CONDITIONS = (
    SESSION_LOCK_LOST,
    SESSION_LOCK_TIMEOUT
)


_AMQP_CONNECTION_ERRORS = (
    errors.LinkDetach,
    errors.ConnectionClose,
    errors.MessageHandlerError,
    errors.AMQPConnectionError
)


_AMQP_MESSAGE_ERRORS = (
    errors.MessageAlreadySettled,
    errors.MessageContentTooLarge,
    errors.MessageException
)


def _error_handler(error):
    """Handle connection and service errors.

    Called internally when an event has failed to send so we
    can parse the error to determine whether we should attempt
    to retry sending the event again.
    Returns the action to take according to error type.

    :param error: The error received in the send attempt.
    :type error: Exception
    :rtype: ~uamqp.errors.ErrorAction
    """
    if error.condition == b'com.microsoft:server-busy':
        return errors.ErrorAction(retry=True, backoff=4)
    if error.condition == b'com.microsoft:timeout':
        return errors.ErrorAction(retry=True, backoff=2)
    if error.condition == b'com.microsoft:operation-cancelled':
        return errors.ErrorAction(retry=True)
    if error.condition == b"com.microsoft:container-close":
        return errors.ErrorAction(retry=True, backoff=4)
    if error.condition in _NO_RETRY_ERRORS:
        return errors.ErrorAction(retry=False)
    return errors.ErrorAction(retry=True)


def _handle_amqp_connection_error(logger, exception, handler):
    # Handle all exception inherited from uamqp.errors.AMQPConnectionError
    error_need_close_handler = True
    error_need_raise = False
    error = None
    if isinstance(exception, errors.LinkDetach) and exception.condition in _AMQP_SESSION_ERROR_CONDITIONS:
        # In session lock lost or no active session case, we don't retry, close the handler and raise the error
        error_need_raise = True
        if exception.condition == SESSION_LOCK_LOST:
            try:
                session_id = handler._session_id  # pylint: disable=protected-access
            except AttributeError:
                session_id = None
            error = SessionLockExpired("Connection detached - lock on Session {} lost.".format(session_id))
        elif exception.condition == SESSION_LOCK_TIMEOUT:
            error = NoActiveSession("Queue has no active session to receive from.")
    elif isinstance(exception, (errors.LinkDetach, errors.ConnectionClose)):
        # In other link detach and connection case, should retry
        logger.info("Handler detached due to exception: (%r).", exception)
        if exception.condition == constants.ErrorCodes.UnauthorizedAccess:
            error = ServiceBusAuthorizationError(str(exception), exception)
        elif exception.condition == constants.ErrorCodes.NotAllowed and 'requires sessions' in str(exception):
            message = str(exception) + '\n\nsession_id must be set when getting a receiver for sessionful entity.'
            error = ServiceBusConnectionError(message, exception)
        else:
            error = ServiceBusConnectionError(str(exception), exception)
    elif isinstance(exception, errors.MessageHandlerError):
        logger.info("Handler error: (%r).", exception)
        error = ServiceBusConnectionError(str(exception), exception)
    else:
        # handling general uamqp.errors.AMQPConnectionError
        logger.info("Failed to open handler: (%r).", exception)
        message = "Failed to open handler: {}.".format(exception)
        error = ServiceBusConnectionError(message, exception)
        error_need_raise, error_need_close_handler = True, False

    return error, error_need_close_handler, error_need_raise


def _handle_amqp_message_error(logger, exception, **kwargs):
    # Handle amqp message related errors
    error_need_close_handler = True
    error_need_raise = False
    error = None
    if isinstance(exception, errors.MessageAlreadySettled):
        # This one doesn't need retry, should raise the error
        logger.info("Message already settled (%r)", exception)
        error = MessageAlreadySettled(kwargs.get("settle_operation", "Unknown operation"))
        error_need_close_handler = False
        error_need_raise = True
    elif isinstance(exception, errors.MessageContentTooLarge) or \
            (isinstance(exception, errors.MessageException) and
             exception.condition == constants.ErrorCodes.LinkMessageSizeExceeded):
        # This one doesn't need retry, should raise the error
        logger.info("Message content is too large (%r).", exception)
        error = MessageContentTooLarge("Message content is too large.", exception)
        error_need_close_handler = False
        error_need_raise = True
    else:
        # handling general uamqp.errors.MessageException
        logger.info("Message send failed (%r)", exception)
        if exception.condition == constants.ErrorCodes.ClientError and 'timed out' in str(exception):
            error = OperationTimeoutError("Send operation timed out", error=exception)
        else:
            error = MessageSendFailed(error=exception)
        error_need_raise = False

    return error, error_need_close_handler, error_need_raise


def _create_servicebus_exception(logger, exception, handler, **kwargs):  # pylint: disable=too-many-statements
    # transform amqp exceptions into servicebus exceptions
    error_need_close_handler = True
    error_need_raise = False
    if isinstance(exception, _AMQP_CONNECTION_ERRORS):
        error, error_need_close_handler, error_need_raise = \
            _handle_amqp_connection_error(logger, exception, handler)
    elif isinstance(exception, _AMQP_MESSAGE_ERRORS):
        error, error_need_close_handler, error_need_raise = \
            _handle_amqp_message_error(logger, exception, **kwargs)
    elif isinstance(exception, errors.AuthenticationException):
        logger.info("Authentication failed due to exception: (%r).", exception)
        error = ServiceBusAuthenticationError(str(exception), exception)
    else:
        logger.info("Unexpected error occurred (%r). Shutting down.", exception)
        if kwargs.get("settle_operation"):
            error = MessageSettleFailed(kwargs.get("settle_operation"), exception)
        elif not isinstance(exception, ServiceBusError):
            error = ServiceBusError("Handler failed: {}.".format(exception), exception)
        else:
            error = exception

    try:
        err_condition = exception.condition
        if err_condition in _NO_RETRY_ERRORS:
            error_need_raise = True
    except AttributeError:
        pass

    return error, error_need_close_handler, error_need_raise


class _ServiceBusErrorPolicy(errors.ErrorPolicy):

    def __init__(self, max_retries=3, is_session=False):
        self._is_session = is_session
        super(_ServiceBusErrorPolicy, self).__init__(max_retries=max_retries, on_error=_error_handler)

    def on_unrecognized_error(self, error):
        if self._is_session:
            return errors.ErrorAction(retry=False)
        return super(_ServiceBusErrorPolicy, self).on_unrecognized_error(error)

    def on_link_error(self, error):
        if self._is_session:
            return errors.ErrorAction(retry=False)
        return super(_ServiceBusErrorPolicy, self).on_link_error(error)

    def on_connection_error(self, error):
        if self._is_session:
            return errors.ErrorAction(retry=False)
        return super(_ServiceBusErrorPolicy, self).on_connection_error(error)


class ServiceBusError(AzureError):
    """Base exception for all Service Bus errors which can be used for default error handling.

    :param str message: The message object stringified as 'message' attribute
    :keyword error: The original exception if any
    :paramtype error: Exception
    :ivar exc_type: The exc_type from sys.exc_info()
    :ivar exc_value: The exc_value from sys.exc_info()
    :ivar exc_traceback: The exc_traceback from sys.exc_info()
    :ivar exc_msg: A string formatting of message parameter, exc_type and exc_value
    :ivar str message: A stringified version of the message parameter
    """


class ServiceBusConnectionError(ServiceBusError):
    """An error occurred in the connection."""


class ServiceBusAuthorizationError(ServiceBusError):
    """An error occurred when authorizing the connection."""


class ServiceBusAuthenticationError(ServiceBusError):
    """An error occurred when authenticate the connection."""


class NoActiveSession(ServiceBusError):
    """No active Sessions are available to receive from."""


class OperationTimeoutError(ServiceBusError):
    """Operation timed out."""


class ServiceBusMessageError(ServiceBusError):
    """An error occurred when an operation on a message failed because the message is in an incorrect state."""


class MessageContentTooLarge(ServiceBusMessageError, ValueError):
    """Message content is larger than the service bus frame size."""


class MessageAlreadySettled(ServiceBusMessageError):
    """Failed to settle the message.

    An attempt was made to complete an operation on a message that has already
    been settled (completed, abandoned, dead-lettered or deferred).
    This error will also be raised if an attempt is made to settle a message
    received via ReceiveAndDelete mode.

    :param str action: The settlement operation, there are four types of settlement,
     `complete/abandon/defer/dead_letter`.

    """

    def __init__(self, action):
        # type: (str) -> None
        message = "Unable to {} message as it has already been settled".format(action)
        super(MessageAlreadySettled, self).__init__(message)


class MessageSettleFailed(ServiceBusMessageError):
    """Attempt to settle a message failed.

    :param str action: The settlement operation, there are four types of settlement,
     `complete/abandon/defer/dead_letter`.
    :param error: The original exception if any.
    :type error: Exception

    """

    def __init__(self, action, error):
        # type: (str, Exception) -> None
        message = "Failed to {} message. Error: {}".format(action, error)
        super(MessageSettleFailed, self).__init__(message, error=error)


class MessageSendFailed(ServiceBusMessageError):
    """A message failed to send to the Service Bus entity."""

    def __init__(self, error):
        # type: (Exception) -> None
        message = "Message failed to send. Error: {}".format(error)
        self.condition = None
        self.description = None
        if hasattr(error, 'condition'):
            self.condition = error.condition  # type: ignore
            self.description = error.description  # type: ignore
        super(MessageSendFailed, self).__init__(message, error=error)


class MessageLockExpired(ServiceBusMessageError):
    """The lock on the message has expired and it has been released back to the queue.

    It will need to be received again in order to settle it.

    """

    def __init__(self, message=None, error=None):
        # type: (Optional[str], Optional[Exception]) -> None
        message = message or "Message lock expired"
        super(MessageLockExpired, self).__init__(message, error=error)


class SessionLockExpired(ServiceBusError):
    """The lock on the session has expired.

    All unsettled messages that have been received can no longer be settled.

    """

    def __init__(self, message=None, error=None):
        # type: (Optional[str], Optional[Exception]) -> None
        message = message or "Session lock expired"
        super(SessionLockExpired, self).__init__(message, error=error)


class AutoLockRenewFailed(ServiceBusError):
    """An attempt to renew a lock on a message or session in the background has failed."""


class AutoLockRenewTimeout(ServiceBusError):
    """The time allocated to renew the message or session lock has elapsed."""
