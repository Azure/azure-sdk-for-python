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

"""Internal class for metadata request throttle retry policy implementation in the Azure
Cosmos database service.

Unlike the document throttle retry policy (ResourceThrottleRetryPolicy) which has
configurable max retry count and wait time, this policy retries indefinitely on
429 (Too Many Requests) errors. Metadata requests such as partition key range cache
fetches must succeed for the SDK to route documents correctly, so they should never
permanently give up on throttles.
"""

import random

from . import http_constants

# Random jitter upper bound (milliseconds) added to each retry-after delay
# to spread retries across concurrent clients.
_RANDOM_SALT_IN_MS = 100


class MetadataRequestRetryPolicy(object):
    """Throttle retry policy for metadata requests that retries indefinitely on 429 errors.

    Currently scoped to partition key range cache related calls only.
    """

    def __init__(self):
        self.current_retry_attempt_count = 0
        self.cumulative_wait_time_in_milliseconds = 0
        self.retry_after_in_milliseconds = 0

    def ShouldRetry(self, exception):
        """Returns true if the request should retry based on the passed-in exception.

        Always returns True since metadata requests should retry indefinitely
        until successful, honoring the server-returned Retry-After header with
        additional random jitter.

        :param exceptions.CosmosHttpResponseError exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        self.current_retry_attempt_count += 1
        self.retry_after_in_milliseconds = 0

        if http_constants.HttpHeaders.RetryAfterInMilliseconds in exception.headers:
            self.retry_after_in_milliseconds = int(
                exception.headers[http_constants.HttpHeaders.RetryAfterInMilliseconds]
            )

        # Add random jitter to spread retries across concurrent clients
        self.retry_after_in_milliseconds += random.randint(0, _RANDOM_SALT_IN_MS)
        self.cumulative_wait_time_in_milliseconds += self.retry_after_in_milliseconds
        return True
