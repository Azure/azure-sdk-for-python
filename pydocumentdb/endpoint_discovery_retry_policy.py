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

import logging
import time

import pydocumentdb.errors as errors

def _Execute(endpoint_discovery_retry_policy, function, *args, **kwargs):
    """Exectutes the callback function using the endpoint_discovery_retry_policy.

    :Parameters:
        - `endpoint_discovery_retry_policy`: object, instance of EndpointDiscoveryRetryPolicy class
        - `function`: callback function
        - `*args`: non-keyworded, variable number of arguments list
        - `**kwargs`: keyworded, variable number of arguments list
    """
    while True:
        try:
            return _ExecuteFunction(function, *args, **kwargs)
        except Exception, e:
            should_retry = endpoint_discovery_retry_policy.ShouldRetry(e)
            if not should_retry:
                raise
        
        # Refresh the endpoint list to refresh the new writable and readable locations
        endpoint_discovery_retry_policy.global_endpoint_manager.RefreshEndpointList()

        # Wait for retry_after_in_milliseconds time before the next retry
        time.sleep(endpoint_discovery_retry_policy.retry_after_in_milliseconds / 1000.0)

def _ExecuteFunction(function, *args, **kwargs):
    """ Stub method so that it can be used for mocking purposes as well.
    """
    return function(*args, **kwargs)

class _EndpointDiscoveryRetryPolicy(object):
    """The endpoint discovery retry policy class used for geo-replicated database accounts
       to handle the write forbidden exceptions due to writable/readable location changes
       (say, after a failover).
    """

    Max_retry_attempt_count = 120
    Retry_after_in_milliseconds = 1000

    def __init__(self, global_endpoint_manager):
        self.global_endpoint_manager = global_endpoint_manager
        self._max_retry_attempt_count = _EndpointDiscoveryRetryPolicy.Max_retry_attempt_count
        self._current_retry_attempt_count = 0
        self.retry_after_in_milliseconds = _EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    def ShouldRetry(self, exception):
        """Returns true if should retry on the passed-in exception.

        :Parameters:
            - `exception`: Exception

        :Returns:
            boolean

        """
        if (self._current_retry_attempt_count < self._max_retry_attempt_count and
                self._CheckIfRetryNeeded(exception)):
            self._current_retry_attempt_count += 1
            return True
        else:
            logging.info('Operation will NOT be retried or has maxed out the retry count. Exception: %s' % str(exception))
            return False

    def _CheckIfRetryNeeded(self, exception):
        # Check if it's a write-forbidden exception, which has StatusCode=403 and SubStatus=3 and whether EnableEndpointDiscovery is set to True
        if (isinstance(exception, errors.HTTPFailure) and exception.status_code == 403 and exception.sub_status == 3 and self.global_endpoint_manager.EnableEndpointDiscovery):
            logging.info('Write location was changed, refreshing the locations list from database account and will retry the request.')
            return True

        return False
