# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Internal class for connection reset retry policy implementation in the Azure
Cosmos database service.
"""
from . import http_constants

# pylint: disable=protected-access


class DefaultRetryPolicy(object):

    error_codes = http_constants._ErrorCodes
    CONNECTION_ERROR_CODES = [
        error_codes.WindowsInterruptedFunctionCall,
        error_codes.WindowsFileHandleNotValid,
        error_codes.WindowsPermissionDenied,
        error_codes.WindowsBadAddress,
        error_codes.WindowsInvalidArgumnet,
        error_codes.WindowsResourceTemporarilyUnavailable,
        error_codes.WindowsOperationNowInProgress,
        error_codes.WindowsAddressAlreadyInUse,
        error_codes.WindowsConnectionResetByPeer,
        error_codes.WindowsCannotSendAfterSocketShutdown,
        error_codes.WindowsConnectionTimedOut,
        error_codes.WindowsConnectionRefused,
        error_codes.WindowsNameTooLong,
        error_codes.WindowsHostIsDown,
        error_codes.WindowsNoRouteTohost,
        error_codes.LinuxConnectionReset,
    ]

    def __init__(self, *args):
        self._max_retry_attempt_count = 10
        self.current_retry_attempt_count = 0
        self.retry_after_in_milliseconds = 1000
        self.args = args

    def needsRetry(self, error_code):
        if error_code in DefaultRetryPolicy.CONNECTION_ERROR_CODES:
            if self.args:
                if (self.args[3].method == "GET") or (http_constants.HttpHeaders.IsQuery in self.args[3].headers) \
                        or (http_constants.HttpHeaders.IsQueryPlanRequest in self.args[3].headers):
                    return True
                return False
            return True
        return False

    def ShouldRetry(self, exception):
        """Returns true if the request should retry based on the passed-in exception.

        :param exceptions.CosmosHttpResponseError exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        if (self.current_retry_attempt_count < self._max_retry_attempt_count) and self.needsRetry(
            exception.status_code
        ):
            self.current_retry_attempt_count += 1
            return True
        return False
