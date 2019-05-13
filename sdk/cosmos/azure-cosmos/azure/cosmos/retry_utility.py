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

"""Internal methods for executing functions in the Azure Cosmos database service.
"""

import time

import azure.cosmos.errors as errors
import azure.cosmos.endpoint_discovery_retry_policy as endpoint_discovery_retry_policy
import azure.cosmos.resource_throttle_retry_policy as resource_throttle_retry_policy
import azure.cosmos.default_retry_policy as default_retry_policy
import azure.cosmos.session_retry_policy as session_retry_policy
from azure.cosmos.http_constants import HttpHeaders, StatusCodes, SubStatusCodes

def _Execute(client, global_endpoint_manager, function, *args, **kwargs):
    """Exectutes the function with passed parameters applying all retry policies

    :param object client:
        Document client instance
    :param object global_endpoint_manager:
        Instance of _GlobalEndpointManager class
    :param function function:
        Function to be called wrapped with retries
    :param (non-keyworded, variable number of arguments list) *args:
    :param (keyworded, variable number of arguments list) **kwargs:

    """
    # instantiate all retry policies here to be applied for each request execution
    endpointDiscovery_retry_policy = endpoint_discovery_retry_policy._EndpointDiscoveryRetryPolicy(client.connection_policy, global_endpoint_manager, *args)

    resourceThrottle_retry_policy = resource_throttle_retry_policy._ResourceThrottleRetryPolicy(client.connection_policy.RetryOptions.MaxRetryAttemptCount, 
                                                                                                client.connection_policy.RetryOptions.FixedRetryIntervalInMilliseconds, 
                                                                                                client.connection_policy.RetryOptions.MaxWaitTimeInSeconds)
    defaultRetry_policy = default_retry_policy._DefaultRetryPolicy(*args)

    sessionRetry_policy = session_retry_policy._SessionRetryPolicy(client.connection_policy.EnableEndpointDiscovery, global_endpoint_manager, *args)
    while True:
        try:
            if args:
                result = _ExecuteFunction(function, global_endpoint_manager, *args, **kwargs)
            else:
                result = _ExecuteFunction(function, *args, **kwargs)
            if not client.last_response_headers:
                client.last_response_headers = {}
            
            # setting the throttle related response headers before returning the result
            client.last_response_headers[HttpHeaders.ThrottleRetryCount] = resourceThrottle_retry_policy.current_retry_attempt_count
            client.last_response_headers[HttpHeaders.ThrottleRetryWaitTimeInMs] = resourceThrottle_retry_policy.cummulative_wait_time_in_milliseconds

            return result
        except errors.HTTPFailure as e:
            retry_policy = None
            if (e.status_code == StatusCodes.FORBIDDEN
                    and e.sub_status == SubStatusCodes.WRITE_FORBIDDEN):
                retry_policy = endpointDiscovery_retry_policy
            elif e.status_code == StatusCodes.TOO_MANY_REQUESTS:
                retry_policy = resourceThrottle_retry_policy
            elif e.status_code == StatusCodes.NOT_FOUND and e.sub_status and e.sub_status == SubStatusCodes.READ_SESSION_NOTAVAILABLE:
                retry_policy = sessionRetry_policy
            else:
                retry_policy = defaultRetry_policy

            # If none of the retry policies applies or there is no retry needed, set the throttle related response hedaers and 
            # re-throw the exception back
            # arg[0] is the request. It needs to be modified for write forbidden exception
            if not (retry_policy.ShouldRetry(e)):
                if not client.last_response_headers:
                    client.last_response_headers = {}
                client.last_response_headers[HttpHeaders.ThrottleRetryCount] = resourceThrottle_retry_policy.current_retry_attempt_count
                client.last_response_headers[HttpHeaders.ThrottleRetryWaitTimeInMs] = resourceThrottle_retry_policy.cummulative_wait_time_in_milliseconds
                if len(args) > 0 and args[0].should_clear_session_token_on_session_read_failure:
                    client.session.clear_session_token(client.last_response_headers)
                raise
            else:
                # Wait for retry_after_in_milliseconds time before the next retry
                time.sleep(retry_policy.retry_after_in_milliseconds / 1000.0)

def _ExecuteFunction(function, *args, **kwargs):
    """ Stub method so that it can be used for mocking purposes as well.
    """
    return function(*args, **kwargs)