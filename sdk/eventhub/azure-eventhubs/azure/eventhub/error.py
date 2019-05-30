# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from uamqp import types, constants, errors
import six
from azure.core import AzureError

_NO_RETRY_ERRORS = (
    b"com.microsoft:argument-out-of-range",
    b"com.microsoft:entity-disabled",
    b"com.microsoft:auth-failed",
    b"com.microsoft:precondition-failed",
    b"com.microsoft:argument-error"
)

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


class EventHubError(AzureError):
    """
    Represents an error happened in the client.

    :ivar message: The error message.
    :vartype message: str
    :ivar error: The error condition, if available.
    :vartype error: str
    :ivar details: The error details, if included in the
     service response.
    :vartype details: dict[str, str]
    """

    def __init__(self, message, details=None):
        self.error = None
        self.message = message
        self.details = details
        if isinstance(message, constants.MessageSendResult):
            self.message = "Message send failed with result: {}".format(message)
        if details and isinstance(details, Exception):
            try:
                condition = details.condition.value.decode('UTF-8')
            except AttributeError:
                condition = details.condition.decode('UTF-8')
            _, _, self.error = condition.partition(':')
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
        self.message = error_list if isinstance(error_list, six.text_type) else error_list.decode('UTF-8')
        details_index = self.message.find(" Reference:")
        if details_index >= 0:
            details_msg = self.message[details_index + 1:]
            self.message = self.message[0:details_index]

            tracking_index = details_msg.index(", TrackingId:")
            system_index = details_msg.index(", SystemTracker:")
            timestamp_index = details_msg.index(", Timestamp:")
            details.append(details_msg[:tracking_index])
            details.append(details_msg[tracking_index + 2: system_index])
            details.append(details_msg[system_index + 2: timestamp_index])
            details.append(details_msg[timestamp_index + 2:])
            self.details = details


class EventHubAuthenticationError(EventHubError):
    pass


class EventHubConnectionError(EventHubError):
    pass


class EventHubMessageError(EventHubError):
    pass

