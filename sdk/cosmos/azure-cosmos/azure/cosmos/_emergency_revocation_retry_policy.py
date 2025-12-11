# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Internal class for emergency revocation retry policy implementation in the Azure
Cosmos database service.
"""

# pylint: disable=protected-access


class EmergencyRevocationRetryPolicy(object):

    def __init__(self, *args):
        self._max_retry_attempt_count = 1
        self.current_retry_attempt_count = 0
        self.retry_after_in_milliseconds = 1000
        self.args = args
        self.request = args[0] if args else None

    def ShouldRetry(self, exception):
        """Returns true if the request should retry based on the passed-in exception.

        :param exceptions.CosmosHttpResponseError exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        if self.current_retry_attempt_count < self._max_retry_attempt_count:
            self.current_retry_attempt_count += 1
            return True
        return False
