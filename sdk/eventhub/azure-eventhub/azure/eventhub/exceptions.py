# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Union, List, Optional, cast, TYPE_CHECKING
from ._pyamqp.error import AMQPException

if TYPE_CHECKING:
    from ._pyamqp.error import ErrorCondition


class EventHubError(Exception):
    """Represents an error occurred in the client.

    :ivar message: The error message.
    :vartype message: str
    :ivar error: The error condition, if available.
    :vartype error: str
    :ivar details: The error details, if included in the
     service response.
    :vartype details: list[str] or AMQPException
    """

    def __init__(self, message: str, details: Optional[Union[List[str], "AMQPException"]] = None) -> None:
        self.error: Optional[str] = None
        self.message: str = message
        self.details: Union[List[str], "AMQPException"]
        if details and isinstance(details, Exception):
            self.details = details
            if isinstance(self.details, AMQPException):
                try:
                    details.condition = cast("ErrorCondition", details.condition)
                    condition = details.condition.value.decode("UTF-8")
                except AttributeError:
                    try:
                        details.condition = cast(bytes, details.condition)
                        condition = details.condition.decode("UTF-8")
                    except AttributeError:
                        condition = None
                if condition:
                    _, _, self.error = condition.partition(":")
                    self.message += "\nError: {}".format(self.error)
            elif isinstance(self.details, list):
                try:
                    details.description = cast(str, details.description)
                    self._parse_error(details.description)
                    for detail in self.details:
                        self.message += "\n{}".format(detail)
                except:  # pylint: disable=bare-except
                    self.message += "\n{}".format(details)
        super(EventHubError, self).__init__(self.message)

    def _parse_error(self, error_list: Union[str, bytes]) -> None:
        details = []
        self.message = (
            error_list
            if isinstance(error_list, str)
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
