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

"""Internal class for database account retry policy implementation in the
Azure Cosmos database service.
"""
import os
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.cosmos import _constants


class DatabaseAccountRetryPolicy(object):
    """Implements retry logic for database account reads in Azure Cosmos DB."""

    # List of HTTP status codes considered transient errors for retry logic.
    transient_status_codes = [502, 503, 504]

    # Tuple of exception types considered transient errors for retry logic.
    transient_exceptions = (ServiceRequestError, ServiceResponseError)

    def __init__(self, connection_policy):
        self.retry_count = 0
        self.retry_after_in_milliseconds = int(os.getenv(
            _constants._Constants.DB_ACCOUNT_RETRY_AFTER_MS_CONFIG,
            str(_constants._Constants.DB_ACCOUNT_RETRY_AFTER_MS_CONFIG_DEFAULT)
        ))
        self.max_retry_attempt_count = int(os.getenv(
            _constants._Constants.DB_ACCOUNT_RETRY_ATTEMPTS_CONFIG,
            str(_constants._Constants.DB_ACCOUNT_RETRY_ATTEMPTS_CONFIG_DEFAULT)
        ))
        self.connection_policy = connection_policy

    def ShouldRetry(self, exception):
        """
        Determines if the given exception is transient and if a retry should be attempted.

        :param exception: The exception instance to evaluate.
        :type exception: Exception
        :return: True if the exception is transient and retry attempts to remain, False otherwise.
        :rtype: bool
        """

        is_transient = False

        # Check for transient HTTP status codes
        status_code = getattr(exception, "status_code", None)
        if status_code in self.transient_status_codes:
            is_transient = True

        # Check for transient exception types
        if isinstance(exception, self.transient_exceptions):
            is_transient = True

        if is_transient and self.retry_count < self.max_retry_attempt_count:
            self.retry_count += 1
            return True

        return False
