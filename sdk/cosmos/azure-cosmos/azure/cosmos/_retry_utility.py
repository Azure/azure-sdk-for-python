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

"""Internal methods for executing functions in the Azure Cosmos database service.
"""
import json
import time
from typing import Optional

from azure.core.exceptions import AzureError, ClientAuthenticationError, ServiceRequestError
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import RetryPolicy
from azure.core.pipeline.transport._base import HttpRequest

from . import exceptions
from . import _endpoint_discovery_retry_policy
from . import _resource_throttle_retry_policy
from . import _default_retry_policy
from . import _session_retry_policy
from . import _gone_retry_policy
from . import _timeout_failover_retry_policy
from . import _container_recreate_retry_policy
from .http_constants import HttpHeaders, StatusCodes, SubStatusCodes


# pylint: disable=protected-access, disable=too-many-lines, disable=too-many-statements, disable=too-many-branches


def Execute(client, global_endpoint_manager, function, *args, **kwargs):
    """Executes the function with passed parameters applying all retry policies

    :param object client:
        Document client instance
    :param object global_endpoint_manager:
        Instance of _GlobalEndpointManager class
    :param function function:
        Function to be called wrapped with retries
    :param list args:
    :returns: the result of running the passed in function as a (result, headers) tuple
    :rtype: tuple of (dict, dict)
    """
    # instantiate all retry policies here to be applied for each request execution
    endpointDiscovery_retry_policy = _endpoint_discovery_retry_policy.EndpointDiscoveryRetryPolicy(
        client.connection_policy, global_endpoint_manager, *args
    )

    resourceThrottle_retry_policy = _resource_throttle_retry_policy.ResourceThrottleRetryPolicy(
        client.connection_policy.RetryOptions.MaxRetryAttemptCount,
        client.connection_policy.RetryOptions.FixedRetryIntervalInMilliseconds,
        client.connection_policy.RetryOptions.MaxWaitTimeInSeconds,
    )
    defaultRetry_policy = _default_retry_policy.DefaultRetryPolicy(*args)

    sessionRetry_policy = _session_retry_policy._SessionRetryPolicy(
        client.connection_policy.EnableEndpointDiscovery, global_endpoint_manager, *args
    )

    partition_key_range_gone_retry_policy = _gone_retry_policy.PartitionKeyRangeGoneRetryPolicy(client, *args)

    timeout_failover_retry_policy = _timeout_failover_retry_policy._TimeoutFailoverRetryPolicy(
        client.connection_policy, global_endpoint_manager, *args
    )
    # HttpRequest we would need to modify for Container Recreate Retry Policy
    request: Optional[HttpRequest] = None
    if args and len(args) > 3:
        # Reference HttpRequest instance in args
        request = args[3]
        container_recreate_retry_policy = _container_recreate_retry_policy.ContainerRecreateRetryPolicy(
            client, client._container_properties_cache, request, *args)
    else:
        container_recreate_retry_policy = _container_recreate_retry_policy.ContainerRecreateRetryPolicy(
            client, client._container_properties_cache, None, *args)

    while True:
        client_timeout = kwargs.get('timeout')
        start_time = time.time()
        try:
            if args:
                result = ExecuteFunction(function, global_endpoint_manager, *args, **kwargs)
            else:
                result = ExecuteFunction(function, *args, **kwargs)
            if not client.last_response_headers:
                client.last_response_headers = {}

            # setting the throttle related response headers before returning the result
            client.last_response_headers[
                HttpHeaders.ThrottleRetryCount
            ] = resourceThrottle_retry_policy.current_retry_attempt_count
            client.last_response_headers[
                HttpHeaders.ThrottleRetryWaitTimeInMs
            ] = resourceThrottle_retry_policy.cumulative_wait_time_in_milliseconds
            # TODO: It is better to raise Exceptions manually in the method related to the request,
            #  a rework of retry would be needed to be able to retry exceptions raised that way.
            #  for now raising a manual exception here should allow it to be retried.
            # If container does not have throughput, results will return empty list.
            # We manually raise a 404. We raise it here, so we can handle it in retry utilities.
            if result and isinstance(result[0], dict) and 'Offers' in result[0] and \
                    not result[0]['Offers'] and request.method == 'POST':
                # Grab the link used for getting throughput properties to add to message.
                link = json.loads(request.body)["parameters"][0]["value"]
                raise exceptions.CosmosResourceNotFoundError(
                    status_code=StatusCodes.NOT_FOUND,
                    message="Could not find ThroughputProperties for container " + link,
                    sub_status_code=SubStatusCodes.THROUGHPUT_OFFER_NOT_FOUND)
            return result
        except exceptions.CosmosHttpResponseError as e:
            retry_policy = defaultRetry_policy
            # Re-assign retry policy based on error code
            if e.status_code == StatusCodes.FORBIDDEN and e.sub_status in\
                    [SubStatusCodes.DATABASE_ACCOUNT_NOT_FOUND, SubStatusCodes.WRITE_FORBIDDEN]:
                retry_policy = endpointDiscovery_retry_policy
            elif e.status_code == StatusCodes.TOO_MANY_REQUESTS:
                retry_policy = resourceThrottle_retry_policy
            elif (
                e.status_code == StatusCodes.NOT_FOUND
                and e.sub_status
                and e.sub_status == SubStatusCodes.READ_SESSION_NOTAVAILABLE
            ):
                retry_policy = sessionRetry_policy
            elif exceptions._partition_range_is_gone(e):
                retry_policy = partition_key_range_gone_retry_policy
            elif exceptions._container_recreate_exception(e):
                retry_policy = container_recreate_retry_policy
                # Before we retry if retry policy is container recreate, we need refresh the cache of the
                # container properties and pass in the new RID in the headers.
                client._refresh_container_properties_cache(retry_policy.container_link)
                if e.sub_status != SubStatusCodes.COLLECTION_RID_MISMATCH and retry_policy.check_if_rid_different(
                        retry_policy.container_link, client._container_properties_cache, retry_policy.container_rid):
                    retry_policy.refresh_container_properties_cache = False
                else:
                    cached_container = client._container_properties_cache[retry_policy.container_link]
                    # If partition key value was previously extracted from the document definition
                    # reattempt to extract partition key with updated partition key definition
                    if retry_policy.should_extract_partition_key(cached_container):
                        new_partition_key = retry_policy._extract_partition_key(
                            client, container_cache=cached_container, body=request.body
                        )
                        request.headers[HttpHeaders.PartitionKey] = new_partition_key
                    # If getting throughput, we have to replace the container link received from stale cache
                    # with refreshed cache
                    if retry_policy.should_update_throughput_link(request.body, cached_container):
                        new_body = retry_policy._update_throughput_link(request.body)
                        request.body = new_body

                    retry_policy.container_rid = cached_container["_rid"]
                    request.headers[retry_policy._intended_headers] = retry_policy.container_rid
            elif e.status_code in [StatusCodes.REQUEST_TIMEOUT, StatusCodes.SERVICE_UNAVAILABLE]:
                retry_policy = timeout_failover_retry_policy

            # If none of the retry policies applies or there is no retry needed, set the
            # throttle related response headers and re-throw the exception back arg[0]
            # is the request. It needs to be modified for write forbidden exception
            if not retry_policy.ShouldRetry(e):
                if not client.last_response_headers:
                    client.last_response_headers = {}
                client.last_response_headers[
                    HttpHeaders.ThrottleRetryCount
                ] = resourceThrottle_retry_policy.current_retry_attempt_count
                client.last_response_headers[
                    HttpHeaders.ThrottleRetryWaitTimeInMs
                ] = resourceThrottle_retry_policy.cumulative_wait_time_in_milliseconds
                if args and args[0].should_clear_session_token_on_session_read_failure:
                    client.session.clear_session_token(client.last_response_headers)
                raise

            # Wait for retry_after_in_milliseconds time before the next retry
            time.sleep(retry_policy.retry_after_in_milliseconds / 1000.0)
            if client_timeout:
                kwargs['timeout'] = client_timeout - (time.time() - start_time)
                if kwargs['timeout'] <= 0:
                    raise exceptions.CosmosClientTimeoutError()


def ExecuteFunction(function, *args, **kwargs):
    """Stub method so that it can be used for mocking purposes as well.
    :param Callable function: the function to execute.
    :param list args: the explicit arguments for the function.
    :returns: the result of executing the function with the passed in arguments
    :rtype: tuple(dict, dict)
    """
    return function(*args, **kwargs)


def _configure_timeout(request: PipelineRequest, absolute: Optional[int], per_request: int) -> None:
    if absolute is not None:
        if absolute <= 0:
            raise exceptions.CosmosClientTimeoutError()
        if per_request:
            # Both socket timeout and client timeout have been provided - use the shortest value.
            request.context.options['connection_timeout'] = min(per_request, absolute)
        else:
            # Only client timeout provided.
            request.context.options['connection_timeout'] = absolute
    elif per_request:
        # Only socket timeout provided.
        request.context.options['connection_timeout'] = per_request


class ConnectionRetryPolicy(RetryPolicy):

    def __init__(self, **kwargs):
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super(ConnectionRetryPolicy, self).__init__(**clean_kwargs)

    def send(self, request):
        """Sends the PipelineRequest object to the next policy. Uses retry settings if necessary.
        Also enforces an absolute client-side timeout that spans multiple retry attempts.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: Returns the PipelineResponse or raises error if maximum retries exceeded.
        :rtype: ~azure.core.pipeline.PipelineResponse
        :raises ~azure.core.exceptions.AzureError: Maximum retries exceeded.
        :raises ~azure.cosmos.exceptions.CosmosClientTimeoutError: Specified timeout exceeded.
        :raises ~azure.core.exceptions.ClientAuthenticationError: Authentication failed.
        """
        absolute_timeout = request.context.options.pop('timeout', None)
        per_request_timeout = request.context.options.pop('connection_timeout', 0)

        retry_error = None
        retry_active = True
        response = None
        retry_settings = self.configure_retries(request.context.options)
        while retry_active:
            start_time = time.time()
            try:
                _configure_timeout(request, absolute_timeout, per_request_timeout)

                response = self.next.send(request)
                if self.is_retry(retry_settings, response):
                    retry_active = self.increment(retry_settings, response=response)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport, response=response)
                        continue
                break
            except ClientAuthenticationError:  # pylint:disable=try-except-raise
                # the authentication policy failed such that the client's request can't
                # succeed--we'll never have a response to it, so propagate the exception
                raise
            except exceptions.CosmosClientTimeoutError as timeout_error:
                timeout_error.inner_exception = retry_error
                timeout_error.response = response
                timeout_error.history = retry_settings['history']
                raise
            except ServiceRequestError as err:
                # the request ran into a socket timeout or failed to establish a new connection
                # since request wasn't sent, we retry up to however many connection retries are configured (default 3)
                if retry_settings['connect'] > 0:
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport)
                        continue
                raise err
            except AzureError as err:
                retry_error = err
                if self._is_method_retryable(retry_settings, request.http_request):
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport)
                        continue
                raise err
            finally:
                end_time = time.time()
                if absolute_timeout:
                    absolute_timeout -= (end_time - start_time)

        self.update_context(response.context, retry_settings)
        return response
