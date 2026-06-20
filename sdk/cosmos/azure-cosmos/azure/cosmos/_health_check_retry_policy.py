# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Internal class for health check retry policy implementation in the
Azure Cosmos database service.
"""
import os
from azure.cosmos import _constants


class HealthCheckRetryPolicy(object):
    """Implements retry logic for health checks in Azure Cosmos DB."""

    def __init__(self, connection_policy, *args):
        self.retry_count = 0
        self.retry_after_in_milliseconds = int(os.getenv(
            _constants._Constants.AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS,
            str(_constants._Constants.AZURE_COSMOS_HEALTH_CHECK_RETRY_AFTER_MS_DEFAULT)
        ))
        self.max_retry_attempt_count = int(os.getenv(
            _constants._Constants.AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES,
            str(_constants._Constants.AZURE_COSMOS_HEALTH_CHECK_MAX_RETRIES_DEFAULT)
        ))
        self.connection_policy = connection_policy
        self.retry_factor = 2
        self.max_retry_after_in_milliseconds = 1000 * 60 * 3  # 3 minutes
        self.initial_connection_timeout = 5
        self.request = args[0] if args else None

    def ShouldRetry(self, exception):# pylint: disable=unused-argument
        """
        Determines if the given exception is transient and if a retry should be attempted.

        :param exception: The exception instance to evaluate.
        :type exception: Exception
        :return: True if the exception is transient and retry attempts to remain, False otherwise.
        :rtype: bool
        """
        if self.retry_count > 0:
            self.retry_after_in_milliseconds = min(self.retry_after_in_milliseconds +
                                                   self.retry_factor ** self.retry_count,
                                                   self.max_retry_after_in_milliseconds)
        if self.request:
            # increase read timeout for each retry
            if self.request.read_timeout_override:
                self.request.read_timeout_override = min(self.request.read_timeout_override ** 2,
                                                         self.connection_policy.ReadTimeout)
            else:
                self.request.read_timeout_override = self.initial_connection_timeout


        if self.retry_count < self.max_retry_attempt_count:
            self.retry_count += 1
            return True

        return False
