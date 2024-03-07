# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Any, Union, Optional

from azure.core.exceptions import AzureError

class ServiceBusError(AzureError):
    """Base exception for all Service Bus errors which can be used for default error handling.

    :param str or bytes message: The message object stringified as 'message' attribute
    :keyword error: The original exception if any
    :paramtype error: Exception
    :ivar exc_type: The exc_type from sys.exc_info()
    :ivar exc_value: The exc_value from sys.exc_info()
    :ivar exc_traceback: The exc_traceback from sys.exc_info()
    :ivar exc_msg: A string formatting of message parameter, exc_type and exc_value
    :ivar str message: A stringified version of the message parameter
    """

    def __init__(
        self,
        message: Optional[Union[str, bytes]],
        *args: Any,
        **kwargs: Any
    ) -> None:
        self._retryable = kwargs.pop("retryable", False)
        self._shutdown_handler = kwargs.pop("shutdown_handler", True)
        self._condition = kwargs.pop("condition", None)
        self._status_code = kwargs.pop("status_code", None)
        if isinstance(message, bytes):
            message = message.decode("UTF-8")

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

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        message = kwargs.pop("message", "An error occurred in the connection.")
        super(ServiceBusConnectionError, self).__init__(
            message, retryable=True, shutdown_handler=True, **kwargs
        )


class ServiceBusAuthenticationError(ServiceBusError):
    """An error occurred when authenticate the connection."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        message = kwargs.pop(
            "message", "An error occurred when authenticating the connection."
        )
        super(ServiceBusAuthenticationError, self).__init__(
            message, retryable=True, shutdown_handler=True, **kwargs
        )


class ServiceBusAuthorizationError(ServiceBusError):
    """An error occurred when authorizing the connection."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        message = kwargs.pop(
            "message", "An error occurred when authorizing the connection."
        )
        super(ServiceBusAuthorizationError, self).__init__(
            message, retryable=True, shutdown_handler=True, **kwargs
        )


class OperationTimeoutError(ServiceBusError):
    """Operation timed out."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        message = kwargs.pop("message", "Operation timed out.")
        super(OperationTimeoutError, self).__init__(
            message, retryable=True, shutdown_handler=False, **kwargs
        )


class MessageSizeExceededError(ServiceBusError, ValueError):
    """Message content is larger than the service bus frame size."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
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

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        super(MessageAlreadySettled, self).__init__(
            "Unable to {} message; The message has either been deleted"
            " or already settled.".format(kwargs.get("action", "operate"))
        )
        self._retryable = False
        self._shutdown_handler = False


class MessageLockLostError(ServiceBusError):
    """The lock on the message is lost. Callers should call attempt to receive and process the message again."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
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

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
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

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        message = kwargs.pop("message", "The requested message was not found.")
        super(MessageNotFoundError, self).__init__(
            message, retryable=False, shutdown_handler=False, **kwargs
        )


class MessagingEntityNotFoundError(ServiceBusError):
    """A Service Bus resource cannot be found by the Service Bus service.

    Entity associated with the operation doesn't exist or it has been deleted.
    Please make sure the entity exists.
    """

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        message = kwargs.pop(
            "message",
            "A Service Bus resource cannot be found by the Service Bus service.",
        )
        super(MessagingEntityNotFoundError, self).__init__(
            message, retryable=False, shutdown_handler=True, **kwargs
        )


class MessagingEntityDisabledError(ServiceBusError):
    """The Messaging Entity is disabled. Enable the entity again using Portal."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        message = kwargs.pop(
            "message",
            "The Messaging Entity is disabled. Enable the entity again using Portal.",
        )

        super(MessagingEntityDisabledError, self).__init__(
            message, retryable=True, shutdown_handler=True, **kwargs
        )


class MessagingEntityAlreadyExistsError(ServiceBusError):
    """An entity with the same name exists under the same namespace."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
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

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
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

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
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

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
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

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        message = kwargs.pop("message", "The requested session cannot be locked.")
        super(SessionCannotBeLockedError, self).__init__(
            message, retryable=True, shutdown_handler=True, **kwargs
        )


class AutoLockRenewFailed(ServiceBusError):
    """An attempt to renew a lock on a message or session in the background has failed."""


class AutoLockRenewTimeout(ServiceBusError):
    """The time allocated to renew the message or session lock has elapsed."""
