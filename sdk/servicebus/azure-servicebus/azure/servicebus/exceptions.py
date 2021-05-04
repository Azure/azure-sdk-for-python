# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Any

from uamqp import errors as AMQPErrors, constants
from uamqp.constants import ErrorCodes as AMQPErrorCodes
from azure.core.exceptions import AzureError

from ._common.constants import (
    ERROR_CODE_SESSION_LOCK_LOST,
    ERROR_CODE_MESSAGE_LOCK_LOST,
    ERROR_CODE_MESSAGE_NOT_FOUND,
    ERROR_CODE_TIMEOUT,
    ERROR_CODE_AUTH_FAILED,
    ERROR_CODE_SESSION_CANNOT_BE_LOCKED,
    ERROR_CODE_SERVER_BUSY,
    ERROR_CODE_ARGUMENT_ERROR,
    ERROR_CODE_OUT_OF_RANGE,
    ERROR_CODE_ENTITY_DISABLED,
    ERROR_CODE_ENTITY_ALREADY_EXISTS,
    ERROR_CODE_PRECONDITION_FAILED,
)


_NO_RETRY_CONDITION_ERROR_CODES = (
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
    ERROR_CODE_SESSION_LOCK_LOST,
    ERROR_CODE_MESSAGE_LOCK_LOST,
    ERROR_CODE_OUT_OF_RANGE,
    ERROR_CODE_ARGUMENT_ERROR,
    ERROR_CODE_PRECONDITION_FAILED,
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
    if error.condition == b"com.microsoft:server-busy":
        return AMQPErrors.ErrorAction(retry=True, backoff=4)
    if error.condition == b"com.microsoft:timeout":
        return AMQPErrors.ErrorAction(retry=True, backoff=2)
    if error.condition == b"com.microsoft:operation-cancelled":
        return AMQPErrors.ErrorAction(retry=True)
    if error.condition == b"com.microsoft:container-close":
        return AMQPErrors.ErrorAction(retry=True, backoff=4)
    if error.condition in _NO_RETRY_CONDITION_ERROR_CODES:
        return AMQPErrors.ErrorAction(retry=False)
    return AMQPErrors.ErrorAction(retry=True)


def _handle_amqp_exception_with_condition(
    logger, condition, description, exception=None, status_code=None
):
    #
    # handling AMQP Errors that have the condition field or the mgmt handler
    logger.info(
        "AMQP error occurred: (%r), condition: (%r), description: (%r).",
        exception,
        condition,
        description,
    )
    if condition == AMQPErrorCodes.NotFound:
        # handle NotFound error code
        error_cls = (
            ServiceBusCommunicationError
            if isinstance(exception, AMQPErrors.AMQPConnectionError)
            else MessagingEntityNotFoundError
        )
    elif condition == AMQPErrorCodes.ClientError and "timed out" in str(exception):
        # handle send timeout
        error_cls = OperationTimeoutError
    elif condition == AMQPErrorCodes.UnknownError and isinstance(exception, AMQPErrors.AMQPConnectionError):
        error_cls = ServiceBusConnectionError
    else:
        # handle other error codes
        error_cls = _ERROR_CODE_TO_ERROR_MAPPING.get(condition, ServiceBusError)

    error = error_cls(
        message=description,
        error=exception,
        condition=condition,
        status_code=status_code,
    )
    if condition in _NO_RETRY_CONDITION_ERROR_CODES:
        error._retryable = False  # pylint: disable=protected-access

    return error


def _handle_amqp_exception_without_condition(logger, exception):
    error_cls = ServiceBusError
    if isinstance(exception, AMQPErrors.AMQPConnectionError):
        logger.info("AMQP Connection error occurred: (%r).", exception)
        error_cls = ServiceBusConnectionError
    elif isinstance(exception, AMQPErrors.AuthenticationException):
        logger.info("AMQP Connection authentication error occurred: (%r).", exception)
        error_cls = ServiceBusAuthenticationError
    elif isinstance(exception, AMQPErrors.MessageException):
        logger.info("AMQP Message error occurred: (%r).", exception)
        if isinstance(exception, AMQPErrors.MessageAlreadySettled):
            error_cls = MessageAlreadySettled
        elif isinstance(exception, AMQPErrors.MessageContentTooLarge):
            error_cls = MessageSizeExceededError
    else:
        logger.info(
            "Unexpected AMQP error occurred (%r). Handler shutting down.", exception
        )

    error = error_cls(message=str(exception), error=exception)
    return error


def _handle_amqp_mgmt_error(
    logger, error_description, condition=None, description=None, status_code=None
):
    if description:
        error_description += " {}.".format(description)

    raise _handle_amqp_exception_with_condition(
        logger,
        condition,
        description=error_description,
        exception=None,
        status_code=status_code,
    )


def _create_servicebus_exception(logger, exception):
    if isinstance(exception, AMQPErrors.AMQPError):
        try:
            # handling AMQP Errors that have the condition field
            condition = exception.condition
            description = exception.description
            exception = _handle_amqp_exception_with_condition(
                logger, condition, description, exception=exception
            )
        except AttributeError:
            # handling AMQP Errors that don't have the condition field
            exception = _handle_amqp_exception_without_condition(logger, exception)
    elif not isinstance(exception, ServiceBusError):
        logger.exception(
            "Unexpected error occurred (%r). Handler shutting down.", exception
        )
        exception = ServiceBusError(
            message="Handler failed: {}.".format(exception), error=exception
        )

    return exception


class _ServiceBusErrorPolicy(AMQPErrors.ErrorPolicy):
    def __init__(self, max_retries=3, is_session=False):
        self._is_session = is_session
        super(_ServiceBusErrorPolicy, self).__init__(
            max_retries=max_retries, on_error=_error_handler
        )

    def on_unrecognized_error(self, error):
        if self._is_session:
            return AMQPErrors.ErrorAction(retry=False)
        return super(_ServiceBusErrorPolicy, self).on_unrecognized_error(error)

    def on_link_error(self, error):
        if self._is_session:
            return AMQPErrors.ErrorAction(retry=False)
        return super(_ServiceBusErrorPolicy, self).on_link_error(error)

    def on_connection_error(self, error):
        if self._is_session:
            return AMQPErrors.ErrorAction(retry=False)
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

    def __init__(self, message, *args, **kwargs):
        self._retryable = kwargs.pop("retryable", False)
        self._shutdown_handler = kwargs.pop("shutdown_handler", True)
        self._condition = kwargs.pop("condition", None)
        self._status_code = kwargs.pop("status_code", None)
        try:
            message = message.decode("UTF-8")
        except AttributeError:
            pass

        message = message or "Service Bus has encountered an error."

        if self._condition:
            try:
                self._condition = self._condition.decode("UTF-8")
            except AttributeError:
                pass
            message = message + " Error condition: {}.".format(str(self._condition))
        if self._status_code is not None:
            message = message + " Status Code: {}.".format(str(self._status_code))
        super(ServiceBusError, self).__init__(message, *args, **kwargs)


class ServiceBusConnectionError(ServiceBusError):
    """An error occurred in the connection."""

    def __init__(self, **kwargs):
        message = kwargs.pop("message", "An error occurred in the connection.")
        super(ServiceBusConnectionError, self).__init__(
            message, retryable=True, shutdown_handler=True, **kwargs
        )


class ServiceBusAuthenticationError(ServiceBusError):
    """An error occurred when authenticate the connection."""

    def __init__(self, **kwargs):
        message = kwargs.pop(
            "message", "An error occurred when authenticating the connection."
        )
        super(ServiceBusAuthenticationError, self).__init__(
            message, retryable=True, shutdown_handler=True, **kwargs
        )


class ServiceBusAuthorizationError(ServiceBusError):
    """An error occurred when authorizing the connection."""

    def __init__(self, **kwargs):
        message = kwargs.pop(
            "message", "An error occurred when authorizing the connection."
        )
        super(ServiceBusAuthorizationError, self).__init__(
            message, retryable=True, shutdown_handler=True, **kwargs
        )


class OperationTimeoutError(ServiceBusError):
    """Operation timed out."""

    def __init__(self, **kwargs):
        message = kwargs.pop("message", "Operation timed out.")
        super(OperationTimeoutError, self).__init__(
            message, retryable=True, shutdown_handler=False, **kwargs
        )


class MessageSizeExceededError(ServiceBusError, ValueError):
    """Message content is larger than the service bus frame size."""

    def __init__(self, **kwargs):
        message = kwargs.pop(
            "message", "Message content is larger than the service bus frame size."
        )
        super(MessageSizeExceededError, self).__init__(
            message=message, retryable=False, shutdown_handler=False, **kwargs
        )


# ValueError was preferred to ServiceBusMessageError/ServiceBusError as a base
# since this arises only from client validation.
class MessageAlreadySettled(ValueError):
    """Failed to settle the message.

    An attempt was made to complete an operation on a message that has already
    been settled (completed, abandoned, dead-lettered or deferred).
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(MessageAlreadySettled, self).__init__(
            "Unable to {} message; The message has either been deleted"
            " or already settled.".format(kwargs.get("action", "operate"))
        )
        self._retryable = False
        self._shutdown_handler = False


class MessageLockLostError(ServiceBusError):
    """The lock on the message is lost. Callers should call attempt to receive and process the message again."""

    def __init__(self, **kwargs):
        # type: (Any) -> None
        message = kwargs.pop(
            "message",
            "The lock on the message lock has expired. Callers should "
            + "call attempt to receive and process the message again.",
        )

        super(MessageLockLostError, self).__init__(
            message=message, retryable=False, shutdown_handler=False, **kwargs
        )


class SessionLockLostError(ServiceBusError):
    """The lock on the session has expired. Callers should request the session again.

    All unsettled messages that have been received can no longer be settled.
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        message = kwargs.pop(
            "message",
            "The lock on the session has expired. Callers should request the session again.",
        )

        super(SessionLockLostError, self).__init__(
            message, retryable=False, shutdown_handler=True, **kwargs
        )


class MessageNotFoundError(ServiceBusError):
    """The requested message was not found.

    Attempt to receive a message with a particular sequence number. This message isn't found.
    Make sure the message hasn't been received already.
    Check the deadletter queue to see if the message has been deadlettered.
    """

    def __init__(self, **kwargs):
        message = kwargs.pop("message", "The requested message was not found.")
        super(MessageNotFoundError, self).__init__(
            message, retryable=False, shutdown_handler=False, **kwargs
        )


class MessagingEntityNotFoundError(ServiceBusError):
    """A Service Bus resource cannot be found by the Service Bus service.

    Entity associated with the operation doesn't exist or it has been deleted.
    Please make sure the entity exists.
    """

    def __init__(self, **kwargs):
        message = kwargs.pop(
            "message",
            "A Service Bus resource cannot be found by the Service Bus service.",
        )
        super(MessagingEntityNotFoundError, self).__init__(
            message, retryable=False, shutdown_handler=True, **kwargs
        )


class MessagingEntityDisabledError(ServiceBusError):
    """The Messaging Entity is disabled. Enable the entity again using Portal."""

    def __init__(self, **kwargs):
        message = kwargs.pop(
            "message",
            "The Messaging Entity is disabled. Enable the entity again using Portal.",
        )

        super(MessagingEntityDisabledError, self).__init__(
            message, retryable=True, shutdown_handler=True, **kwargs
        )


class MessagingEntityAlreadyExistsError(ServiceBusError):
    """An entity with the same name exists under the same namespace."""

    def __init__(self, **kwargs):
        message = kwargs.pop(
            "message", "An entity with the same name exists under the same namespace."
        )
        super(MessagingEntityAlreadyExistsError, self).__init__(
            message, retryable=False, shutdown_handler=False, **kwargs
        )


class ServiceBusQuotaExceededError(ServiceBusError):
    """
    The quota applied to a Service Bus resource has been exceeded while interacting with the Azure Service Bus service.

    The messaging entity has reached its maximum allowable size, or the maximum number of connections to a namespace
    has been exceeded. Create space in the entity by receiving messages from the entity or its subqueues.
    """

    def __init__(self, **kwargs):
        message = kwargs.pop(
            "message",
            "The quota applied to a Service Bus resource has been exceeded while "
            + "interacting with the Azure Service Bus service.",
        )

        super(ServiceBusQuotaExceededError, self).__init__(
            message, retryable=False, shutdown_handler=False, **kwargs
        )


class ServiceBusServerBusyError(ServiceBusError):
    """
    The Azure Service Bus service reports that it is busy in response to a client request to perform an operation.

    Service isn't able to process the request at this time. Client can wait for a period of time,
    then retry the operation.
    """

    def __init__(self, **kwargs):
        message = kwargs.pop(
            "message",
            "The Azure Service Bus service reports that it is busy in response to a "
            + "client request to perform an operation.",
        )
        super(ServiceBusServerBusyError, self).__init__(
            message, retryable=True, shutdown_handler=False, **kwargs
        )


class ServiceBusCommunicationError(ServiceBusError):
    """There was a general communications error encountered when interacting with the Azure Service Bus service.

    Client isn't able to establish a connection to Service Bus.
    Make sure the supplied host name is correct and the host is reachable.
    If your code runs in an environment with a firewall/proxy, ensure that the traffic to
    the Service Bus domain/IP address and ports isn't blocked.
    """

    def __init__(self, **kwargs):
        message = kwargs.pop(
            "message",
            "There was a general communications error encountered when interacting "
            + "with the Azure Service Bus service.",
        )
        super(ServiceBusCommunicationError, self).__init__(
            message, retryable=True, shutdown_handler=True, **kwargs
        )


class SessionCannotBeLockedError(ServiceBusError):
    """The requested session cannot be locked.

    Attempt to connect to a session with a specific session ID, but the session is currently locked by another client.
    Make sure the session is unlocked by other clients.
    """

    def __init__(self, **kwargs):
        message = kwargs.pop("message", "The requested session cannot be locked.")
        super(SessionCannotBeLockedError, self).__init__(
            message, retryable=True, shutdown_handler=True, **kwargs
        )


class AutoLockRenewFailed(ServiceBusError):
    """An attempt to renew a lock on a message or session in the background has failed."""


class AutoLockRenewTimeout(ServiceBusError):
    """The time allocated to renew the message or session lock has elapsed."""


_ERROR_CODE_TO_ERROR_MAPPING = {
    AMQPErrorCodes.LinkMessageSizeExceeded: MessageSizeExceededError,
    AMQPErrorCodes.ResourceLimitExceeded: ServiceBusQuotaExceededError,
    AMQPErrorCodes.UnauthorizedAccess: ServiceBusAuthorizationError,
    AMQPErrorCodes.NotImplemented: ServiceBusError,
    AMQPErrorCodes.NotAllowed: ServiceBusError,
    AMQPErrorCodes.LinkDetachForced: ServiceBusConnectionError,
    ERROR_CODE_MESSAGE_LOCK_LOST: MessageLockLostError,
    ERROR_CODE_MESSAGE_NOT_FOUND: MessageNotFoundError,
    ERROR_CODE_AUTH_FAILED: ServiceBusAuthorizationError,
    ERROR_CODE_ENTITY_DISABLED: MessagingEntityDisabledError,
    ERROR_CODE_ENTITY_ALREADY_EXISTS: MessagingEntityAlreadyExistsError,
    ERROR_CODE_SERVER_BUSY: ServiceBusServerBusyError,
    ERROR_CODE_SESSION_CANNOT_BE_LOCKED: SessionCannotBeLockedError,
    ERROR_CODE_SESSION_LOCK_LOST: SessionLockLostError,
    ERROR_CODE_ARGUMENT_ERROR: ServiceBusError,
    ERROR_CODE_OUT_OF_RANGE: ServiceBusError,
    ERROR_CODE_TIMEOUT: OperationTimeoutError,
}
