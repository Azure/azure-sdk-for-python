# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from uamqp import errors, constants

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


def _create_servicebus_exception(logger, exception, handler):
    error_need_close_handler = True
    error_need_raise = False

    if isinstance(exception, MessageSendFailed):
        logger.info("Message send error (%r)", exception)
        error = exception
    elif isinstance(exception, errors.LinkDetach) and exception.condition == SESSION_LOCK_LOST:
        try:
            session_id = handler._session_id  # pylint: disable=protected-access
        except AttributeError:
            session_id = None
        error = SessionLockExpired("Connection detached - lock on Session {} lost.".format(session_id))
        error_need_raise = True
    elif isinstance(exception, errors.LinkDetach) and exception.condition == SESSION_LOCK_TIMEOUT:
        error = NoActiveSession("Queue has no active session to receive from.")
        error_need_raise = True
    elif isinstance(exception, errors.AuthenticationException):
        logger.info("Authentication failed due to exception: (%r).", exception)
        error = ServiceBusAuthorizationError(str(exception), exception)
    elif isinstance(exception, (errors.LinkDetach, errors.ConnectionClose)):
        logger.info("Handler detached due to exception: (%r).", exception)
        if exception.condition == constants.ErrorCodes.UnauthorizedAccess:
            error = ServiceBusAuthorizationError(str(exception), exception)
        else:
            error = ServiceBusConnectionError(str(exception), exception)
    elif isinstance(exception, errors.MessageHandlerError):
        logger.info("Handler error: (%r).", exception)
        error = ServiceBusConnectionError(str(exception), exception)
    elif isinstance(exception, errors.AMQPConnectionError):
        logger.info("Failed to open handler: (%r).", exception)
        message = "Failed to open handler: {}.".format(exception)
        error = ServiceBusConnectionError(message, exception)
        error_need_raise, error_need_close_handler = True, False
    else:
        logger.info("Unexpected error occurred (%r). Shutting down.", exception)
        error = exception
        if not isinstance(exception, ServiceBusError):
            error = ServiceBusError("Handler failed: {}.".format(exception))

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


class ServiceBusError(Exception):
    """An error occured.

    This is the parent of all Service Bus errors and can
    be used for default error handling.

    """

    def __init__(self, message, inner_exception=None):
        self.inner_exception = inner_exception
        super(ServiceBusError, self).__init__(message)


class ServiceBusResourceNotFound(ServiceBusError):
    """The Service Bus entity could not be reached."""


class ServiceBusConnectionError(ServiceBusError):
    """An error occured in the connection."""


class ServiceBusAuthorizationError(ServiceBusError):
    """An error occured when authorizing the connection."""


class InvalidHandlerState(ServiceBusError):
    """An attempt to run a handler operation that the handler is not in the right state to perform."""


class NoActiveSession(ServiceBusError):
    """No active Sessions are available to receive from."""


class OperationTimeoutError(ServiceBusError):
    """Operation timed out."""


class MessageAlreadySettled(ServiceBusError):
    """Failed to settle the message.

    An attempt was made to complete an operation on a message that has already
    been settled (completed, abandoned, dead-lettered or deferred).
    This error will also be raised if an attempt is made to settle a message
    received via ReceiveAndDelete mode.

    """

    def __init__(self, action):
        message = "Unable to {} message as it has already been settled".format(action)
        super(MessageAlreadySettled, self).__init__(message)


class MessageSettleFailed(ServiceBusError):
    """Attempt to settle a message failed."""

    def __init__(self, action, inner_exception):
        message = "Failed to {} message. Error: {}".format(action, inner_exception)
        self.inner_exception = inner_exception
        super(MessageSettleFailed, self).__init__(message, inner_exception)


class MessageSendFailed(ServiceBusError):
    """A message failed to send to the Service Bus entity."""

    def __init__(self, inner_exception):
        message = "Message failed to send. Error: {}".format(inner_exception)
        self.condition = None
        self.description = None
        if hasattr(inner_exception, 'condition'):
            self.condition = inner_exception.condition
            self.description = inner_exception.description
        self.inner_exception = inner_exception
        super(MessageSendFailed, self).__init__(message, inner_exception)


class MessageLockExpired(ServiceBusError):
    """The lock on the message has expired and it has been released back to the queue.

    It will need to be received again in order to settle it.

    """

    def __init__(self, message=None, inner_exception=None):
        message = message or "Message lock expired"
        super(MessageLockExpired, self).__init__(message, inner_exception=inner_exception)


class SessionLockExpired(ServiceBusError):
    """The lock on the session has expired.

    All unsettled messages that have been received can no longer be settled.

    """

    def __init__(self, message=None, inner_exception=None):
        message = message or "Session lock expired"
        super(SessionLockExpired, self).__init__(message, inner_exception=inner_exception)


class AutoLockRenewFailed(ServiceBusError):
    """An attempt to renew a lock on a message or session in the background has failed."""


class AutoLockRenewTimeout(ServiceBusError):
    """The time allocated to renew the message or session lock has elapsed."""
