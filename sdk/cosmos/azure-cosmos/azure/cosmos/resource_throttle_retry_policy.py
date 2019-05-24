#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Internal class for resource throttle retry policy implementation in the Azure Cosmos database service.
"""

import azure.cosmos.http_constants as http_constants

class _ResourceThrottleRetryPolicy(object):

    def __init__(self, max_retry_attempt_count, fixed_retry_interval_in_milliseconds, max_wait_time_in_seconds):
        self._max_retry_attempt_count = max_retry_attempt_count
        self._fixed_retry_interval_in_milliseconds = fixed_retry_interval_in_milliseconds
        self._max_wait_time_in_milliseconds = max_wait_time_in_seconds * 1000
        self.current_retry_attempt_count = 0
        self.cummulative_wait_time_in_milliseconds = 0

    def ShouldRetry(self, exception):
        """Returns true if should retry based on the passed-in exception.

        :param (errors.HTTPFailure instance) exception:

        :rtype:
            boolean

        """
        if self.current_retry_attempt_count < self._max_retry_attempt_count:
            self.current_retry_attempt_count += 1
            self.retry_after_in_milliseconds = 0
                
            if self._fixed_retry_interval_in_milliseconds:
                self.retry_after_in_milliseconds = self._fixed_retry_interval_in_milliseconds
            elif http_constants.HttpHeaders.RetryAfterInMilliseconds in exception.headers:
                self.retry_after_in_milliseconds = int(exception.headers[http_constants.HttpHeaders.RetryAfterInMilliseconds])
                
            if self.cummulative_wait_time_in_milliseconds < self._max_wait_time_in_milliseconds:
                self.cummulative_wait_time_in_milliseconds += self.retry_after_in_milliseconds
                return True
            
        return False
    
