# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import six

from uamqp import errors, compat

_LOGGER = logging.getLogger(__name__)

class EventHubError(Exception):
    """Represents an error occurred in the client.

    :ivar message: The error message.
    :vartype message: str
    :ivar error: The error condition, if available.
    :vartype error: str
    :ivar details: The error details, if included in the
     service response.
    :vartype details: Dict[str, str]
    """

    def __init__(self, message, details=None):
        self.error = None
        self.message = message
        self.details = details
        if details and isinstance(details, Exception):
            try:
                condition = details.condition.value.decode("UTF-8")
            except AttributeError:
                try:
                    condition = details.condition.decode("UTF-8")
                except AttributeError:
                    condition = None
            if condition:
                _, _, self.error = condition.partition(":")
                self.message += "\nError: {}".format(self.error)
            try:
                self._parse_error(details.description)
                for detail in self.details:
                    self.message += "\n{}".format(detail)
            except:  # pylint: disable=bare-except
                self.message += "\n{}".format(details)
        super(EventHubError, self).__init__(self.message)

    def _parse_error(self, error_list):
        details = []
        self.message = (
            error_list
            if isinstance(error_list, six.text_type)
            else error_list.decode("UTF-8")
        )
        details_index = self.message.find(" Reference:")
        if details_index >= 0:
            details_msg = self.message[details_index + 1 :]
            self.message = self.message[0:details_index]

            tracking_index = details_msg.index(", TrackingId:")
            system_index = details_msg.index(", SystemTracker:")
            timestamp_index = details_msg.index(", Timestamp:")
            details.append(details_msg[:tracking_index])
            details.append(details_msg[tracking_index + 2 : system_index])
            details.append(details_msg[system_index + 2 : timestamp_index])
            details.append(details_msg[timestamp_index + 2 :])
            self.details = details


class ClientClosedError(EventHubError):
    """The Client has been closed and is unable to process further events."""


class ConnectionLostError(EventHubError):
    """Connection to the Event Hub is lost.

    In most cases the client will automatically retry on this error."""


class ConnectError(EventHubError):
    """Failed to connect to the Event Hubs service."""


class AuthenticationError(ConnectError):
    """Failed to connect to the Event Hubs service because of an authentication issue."""


class EventDataError(EventHubError):
    """Client prevented problematic event data from being sent."""


class EventDataSendError(EventHubError):
    """Service returned an error while an event data is being sent."""


class OperationTimeoutError(EventHubError):
    """Operation timed out."""


class OwnershipLostError(Exception):
    """Raised when `update_checkpoint` detects the ownership to a partition has been lost."""


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
        error_type = (
            AuthenticationError
            if str(exception).startswith("Unable to open authentication session")
            else ConnectError
        )
        error = error_type(str(exception), exception)
    elif isinstance(exception, compat.TimeoutException):
        error = ConnectionLostError(str(exception), exception)
    else:
        error = EventHubError(str(exception), exception)
    return error


def _handle_exception(
    exception, closable
):  # pylint:disable=too-many-branches, too-many-statements
    try:  # closable is a producer/consumer object
        name = closable._name  # pylint: disable=protected-access
    except AttributeError:  # closable is an client object
        name = closable._container_id  # pylint: disable=protected-access
    if isinstance(exception, KeyboardInterrupt):  # pylint:disable=no-else-raise
        _LOGGER.info("%r stops due to keyboard interrupt", name)
        closable._close_connection()  # pylint:disable=protected-access
        raise exception
    elif isinstance(exception, EventHubError):
        closable._close_handler()  # pylint:disable=protected-access
        raise exception
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
        if isinstance(exception, errors.AuthenticationException):
            if hasattr(closable, "_close_connection"):
                closable._close_connection()  # pylint:disable=protected-access
        elif isinstance(exception, errors.LinkDetach):
            if hasattr(closable, "_close_handler"):
                closable._close_handler()  # pylint:disable=protected-access
        elif isinstance(exception, errors.ConnectionClose):
            if hasattr(closable, "_close_connection"):
                closable._close_connection()  # pylint:disable=protected-access
        elif isinstance(exception, errors.MessageHandlerError):
            if hasattr(closable, "_close_handler"):
                closable._close_handler()  # pylint:disable=protected-access
        else:  # errors.AMQPConnectionError, compat.TimeoutException
            if hasattr(closable, "_close_connection"):
                closable._close_connection()  # pylint:disable=protected-access
        return _create_eventhub_exception(exception)
