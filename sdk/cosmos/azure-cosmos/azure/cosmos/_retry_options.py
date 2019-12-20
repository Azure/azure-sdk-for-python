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

"""Class for retry options in the Azure Cosmos database service.
"""


class RetryOptions(object):
    """The retry options to be applied to all requests when retrying.

    :ivar int MaxRetryAttemptCount:
        Max number of retries to be performed for a request. Default value 9.
    :ivar int FixedRetryIntervalInMilliseconds:
        Fixed retry interval in milliseconds to wait between each retry ignoring
        the retryAfter returned as part of the response.
    :ivar int MaxWaitTimeInSeconds:
        Max wait time in seconds to wait for a request while the retries are happening.
        Default value 30 seconds.
    """

    def __init__(
        self, max_retry_attempt_count=9, fixed_retry_interval_in_milliseconds=None, max_wait_time_in_seconds=30
    ):
        self._max_retry_attempt_count = max_retry_attempt_count
        self._fixed_retry_interval_in_milliseconds = fixed_retry_interval_in_milliseconds
        self._max_wait_time_in_seconds = max_wait_time_in_seconds

    @property
    def MaxRetryAttemptCount(self):
        return self._max_retry_attempt_count

    @property
    def FixedRetryIntervalInMilliseconds(self):
        return self._fixed_retry_interval_in_milliseconds

    @property
    def MaxWaitTimeInSeconds(self):
        return self._max_wait_time_in_seconds
