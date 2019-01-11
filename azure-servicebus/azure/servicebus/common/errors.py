#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from uamqp import errors, constants


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
    """
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


class ServiceBusErrorPolicy(errors.ErrorPolicy):

    def __init__(self, max_retries=3, is_session=False):
        self._is_session = is_session
        super(ServiceBusErrorPolicy, self).__init__(max_retries=max_retries, on_error=_error_handler)

    def on_unrecognized_error(self, error):
        if self._is_session:
            return errors.ErrorAction(retry=False)
        return super(ServiceBusErrorPolicy, self).on_unrecognized_error(error)

    def on_link_error(self, error):
        if self._is_session:
            return errors.ErrorAction(retry=False)
        return super(ServiceBusErrorPolicy, self).on_link_error(error)

    def on_connection_error(self, error):
        if self._is_session:
            return errors.ErrorAction(retry=False)
        return super(ServiceBusErrorPolicy, self).on_connection_error(error)


class ServiceBusError(Exception):

    def __init__(self, message, inner_exception=None):
        self.inner_exception = inner_exception
        super(ServiceBusError, self).__init__(message)


class ServiceBusResourceNotFound(ServiceBusError):
    pass


class ServiceBusConnectionError(ServiceBusError):
    pass


class ServiceBusAuthorizationError(ServiceBusError):
    pass


class InvalidHandlerState(ServiceBusError):
    """
    An attempt to run a handler operation that the handler is not
    in the right state to perform.
    """


class NoActiveSession(ServiceBusError):
    """
    No active Sessions are available to receive from.
    """


class MessageAlreadySettled(ServiceBusError):

    def __init__(self, action):
        message = "Unable to {} message as it has already been settled".format(action)
        super(MessageAlreadySettled, self).__init__(message)


class MessageSettleFailed(ServiceBusError):

    def __init__(self, action, inner_exception):
        message = "Failed to {} message. Error: {}".format(action, inner_exception)
        self.inner_exception = inner_exception
        super(MessageSettleFailed, self).__init__(message, inner_exception)


class MessageSendFailed(ServiceBusError):

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

    def __init__(self, message=None, inner_exception=None):
        message = message or "Message lock expired"
        super(MessageLockExpired, self).__init__(message, inner_exception=inner_exception)


class SessionLockExpired(ServiceBusError):

    def __init__(self, message=None, inner_exception=None):
        message = message or "Session lock expired"
        super(SessionLockExpired, self).__init__(message, inner_exception=inner_exception)


class AutoLockRenewFailed(ServiceBusError):
    pass


class AutoLockRenewTimeout(ServiceBusError):
    pass
