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
import logging
import time
from typing import Optional

from azure.core.exceptions import AzureError, ClientAuthenticationError, ServiceRequestError, ServiceResponseError
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import RetryPolicy

from . import _container_recreate_retry_policy, _database_account_retry_policy
from . import _default_retry_policy
from . import _endpoint_discovery_retry_policy
from . import _gone_retry_policy
from . import _resource_throttle_retry_policy
from . import _service_request_retry_policy, _service_response_retry_policy
from . import _session_retry_policy
from . import _timeout_failover_retry_policy
from . import exceptions
from .documents import _OperationType
from .exceptions import CosmosHttpResponseError
from .http_constants import HttpHeaders, StatusCodes, SubStatusCodes, ResourceType


# pylint: disable=protected-access, disable=too-many-lines, disable=too-many-statements, disable=too-many-branches

# The list of headers we do not want to log, it needs to be updated if any new headers should not be logged
__disallow_list = ["Authorization", "ProxyAuthorization", "TransferEncoding"]
__cosmos_allow_list = set([
            v.lower() for k, v in HttpHeaders.__dict__.items() if not k.startswith("_") and k not in __disallow_list
        ])

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
    database_account_retry_policy = _database_account_retry_policy.DatabaseAccountRetryPolicy(
        client.connection_policy
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
    service_response_retry_policy = _service_response_retry_policy.ServiceResponseRetryPolicy(
        client.connection_policy, global_endpoint_manager, *args,
    )
    service_request_retry_policy = _service_request_retry_policy.ServiceRequestRetryPolicy(
        client.connection_policy, global_endpoint_manager, *args,
    )
    # set logger
    logger: logging.Logger = kwargs.pop("logger", logging.getLogger("azure.cosmos._retry_utility"))
    # HttpRequest we would need to modify for Container Recreate Retry Policy
    request = None
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
                e_offer = exceptions.CosmosResourceNotFoundError(
                    status_code=StatusCodes.NOT_FOUND,
                    message="Could not find ThroughputProperties for container " + link,
                    sub_status_code=SubStatusCodes.THROUGHPUT_OFFER_NOT_FOUND)
                if client._enable_diagnostics_logging:
                    _log_diagnostics_error(request, result[1], e_offer,
                                           {}, global_endpoint_manager)
                raise e_offer
            return result
        except exceptions.CosmosHttpResponseError as e:
            if client._enable_diagnostics_logging:
                logger_attributes = {
                    "duration": float(time.time() - start_time)
                }
                _log_diagnostics_error(request, None, e,
                                       logger_attributes, global_endpoint_manager)
            if request and _has_database_account_header(request.headers):
                retry_policy = database_account_retry_policy
            # Re-assign retry policy based on error code
            elif e.status_code == StatusCodes.FORBIDDEN and e.sub_status in\
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
            elif e.status_code == StatusCodes.REQUEST_TIMEOUT:
                retry_policy = timeout_failover_retry_policy
            elif e.status_code >= StatusCodes.INTERNAL_SERVER_ERROR:
                retry_policy = timeout_failover_retry_policy
            else:
                retry_policy = defaultRetry_policy

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

        except ServiceRequestError as e:
            if request and _has_database_account_header(request.headers):
                if not database_account_retry_policy.ShouldRetry(e):
                    if client._enable_diagnostics_logging:
                        # TODO : We need to get status code information from the exception.
                        logger_attributes = {
                            "duration": float(time.time() - start_time)
                        }
                        _log_diagnostics_error(request, None, e,
                                                         logger_attributes, global_endpoint_manager)
                    raise e
            else:
                _handle_service_request_retries(request, client, service_request_retry_policy, e, *args)

        except ServiceResponseError as e:
            if request and _has_database_account_header(request.headers):
                if not database_account_retry_policy.ShouldRetry(e):
                    if client._enable_diagnostics_logging:
                        # TODO : We need to get status code information from the exception.
                        logger_attributes = {
                            "duration": float(time.time() - start_time)
                        }
                        _log_diagnostics_error(request, None, e,
                                                         logger_attributes, global_endpoint_manager)
                    raise e
            else:
                _handle_service_response_retries(request, client, service_response_retry_policy, e, *args)

def ExecuteFunction(function, *args, **kwargs):
    """Stub method so that it can be used for mocking purposes as well.
    :param Callable function: the function to execute.
    :param list args: the explicit arguments for the function.
    :returns: the result of executing the function with the passed in arguments
    :rtype: tuple(dict, dict)
    """
    return function(*args, **kwargs)

def _has_read_retryable_headers(request_headers):
    if _OperationType.IsReadOnlyOperation(request_headers.get(HttpHeaders.ThinClientProxyOperationType)):
        return True
    return False

def _has_database_account_header(request_headers):
    if request_headers.get(HttpHeaders.ThinClientProxyResourceType) == ResourceType.DatabaseAccount:
        return True
    return False

def _handle_service_request_retries(request, client, request_retry_policy, exception, *args):
    # we resolve the request endpoint to the next preferred region
    # once we are out of preferred regions we stop retrying
    retry_policy = request_retry_policy
    if not retry_policy.ShouldRetry():
        if args and args[0].should_clear_session_token_on_session_read_failure and client.session:
            client.session.clear_session_token(client.last_response_headers)
        if client._enable_diagnostics_logging:
            _log_diagnostics_error(request, {}, exception,
                                   {}, client._global_endpoint_manager)
        raise exception

def _handle_service_response_retries(request, client, response_retry_policy, exception, *args):
    if client._enable_diagnostics_logging:
        _log_diagnostics_error(request, {}, exception,
                                         {}, client._global_endpoint_manager)
    if request and _has_read_retryable_headers(request.headers):
        # we resolve the request endpoint to the next preferred region
        # once we are out of preferred regions we stop retrying
        retry_policy = response_retry_policy
        if not retry_policy.ShouldRetry():
            if args and args[0].should_clear_session_token_on_session_read_failure and client.session:
                client.session.clear_session_token(client.last_response_headers)
            if client._enable_diagnostics_logging:
                _log_diagnostics_error(request, {}, exception,
                                       {}, client._global_endpoint_manager)
            raise exception
    else:
        if client._enable_diagnostics_logging:
            _log_diagnostics_error(request, {}, exception,
                                   {}, client._global_endpoint_manager)
        raise exception

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

def __populate_logger_attributes(logger_attributes={}, request=None, response_headers=None, exception=None):
    """Populates the logger attributes with the request and response details.

    :param request: The request object.
    :param response: The response object.
    :param logger_attributes: The logger attributes.
    """
    if response_headers:
        logger_attributes["duration"] = float(response_headers.get(HttpHeaders.RequestDurationMs))
    if request:
        logger_attributes["verb"] = request.method
        logger_attributes["url"] = request.url
        logger_attributes["operation_type"] = request.headers.get(
            'x-ms-thinclient-proxy-operation-type')
        logger_attributes["resource_type"] = request.headers.get(
            'x-ms-thinclient-proxy-resource-type')
        if logger_attributes["url"]:
            url_parts = logger_attributes["url"].split('/')
            if 'dbs' in url_parts:
                dbs_index = url_parts.index('dbs')
                if dbs_index + 1 < len(url_parts):
                    logger_attributes["database_name"] = url_parts[dbs_index + 1]
            if 'colls' in url_parts:
                colls_index = url_parts.index('colls')
                if colls_index + 1 < len(url_parts):
                    logger_attributes["collection_name"] = url_parts[colls_index + 1]

    if exception:
        if hasattr(exception, 'status_code'):
            logger_attributes["status_code"] = exception.status_code
        if hasattr(exception, 'sub_status'):
            logger_attributes["sub_status_code"] = exception.sub_status

    logger_attributes["is_request"] = False
    return logger_attributes

def _log_diagnostics_error(request, response_headers, error, logger_attributes, global_endpoint_manager):
    """Logs the request and response error details to the logger.

    :param request: The request object.
    :param response: The response object.
    :param error: The error object.
    :param logger_attributes: The logger attributes.
    """
    logger: logging.Logger = logging.getLogger("azure.cosmos._retry_utility")
    logger_attributes = __populate_logger_attributes(logger_attributes, request, response_headers, error)
    log_string = __get_client_settings(global_endpoint_manager)
    log_string += __get_database_account_settings(global_endpoint_manager)
    if request:
        log_string += f"\nReqeust URL: {request.url}"
        log_string += f"\nRequest Method: {request.method}"
        log_string += "\nRequest Activity ID: {}".format(request.headers.get(HttpHeaders.ActivityId))
        log_string += "\nRequest headers:"
        for header, value in request.headers.items():
            value = __redact_header(header, value)
            if value and value != "REDACTED":
                log_string += "\n    '{}': '{}'".format(header, value)
    log_string += "\nResponse Status: {}".format(logger_attributes.get("status_code", ""))
    log_string += "\nResponse Headers: "
    if response_headers:
        for res_header, value in response_headers.items():
            value = __redact_header(res_header, value)
            if value and value != "REDACTED":
                log_string += "\n    '{}': '{}'".format(res_header, value)
    if "duration" in logger_attributes:
        seconds = logger_attributes["duration"] / 1000  # type: ignore[operator]
        log_string += f"\nElapsed time in seconds: {seconds:.6f}".rstrip('0').rstrip('.')
    log_string += "\nResponse error message: {}".format(_format_error(error.message))
    logger.info(log_string, extra=logger_attributes)


def __redact_header( key: str, value: str) -> str:
        if key.lower() in __cosmos_allow_list:
            return value
        return "REDACTED"

def __get_client_settings(global_endpoint_manager):
        # Place any client settings we want to log here
        client_preferred_regions = []
        client_excluded_regions = []
        client_account_read_regions = []
        client_account_write_regions = []

        if global_endpoint_manager:
            if hasattr(global_endpoint_manager, 'client'):
                gem_client = global_endpoint_manager.client
            else:
                gem_client = global_endpoint_manager.Client
            if gem_client and gem_client.connection_policy:
                connection_policy = gem_client.connection_policy
                client_preferred_regions = connection_policy.PreferredLocations
                client_excluded_regions = connection_policy.ExcludedLocations

            if global_endpoint_manager.location_cache:
                location_cache = global_endpoint_manager.location_cache
                client_account_read_regions = location_cache.account_read_locations
                client_account_write_regions = location_cache.account_write_locations
        logger_str = "\nClient Settings: \n"
        client_settings = {"Client Preferred Regions": client_preferred_regions,
                "Client Excluded Regions": client_excluded_regions,
                "Client Account Read Regions": client_account_read_regions,
                "Client Account Write Regions": client_account_write_regions}
        if client_settings and isinstance(client_settings, dict):
            logger_str += ''.join([f"\t{k}: {v}\n" for k, v in client_settings.items()])
        return logger_str

def __get_database_account_settings(global_endpoint_manager):
        if global_endpoint_manager and hasattr(global_endpoint_manager, '_database_account_cache'):
            database_account = global_endpoint_manager._database_account_cache  # pylint: disable=protected-access
        else:
            database_account = None
        logger_str = "\nDatabase Account Settings: \n"
        if database_account and database_account.ConsistencyPolicy:
            logger_str += f"\tConsistency Level: {database_account.ConsistencyPolicy.get('defaultConsistencyLevel')}\n"  # pylint: disable=line-too-long
            logger_str += f"\tWritable Locations: {database_account.WritableLocations}\n"
            logger_str += f"\tReadable Locations: {database_account.ReadableLocations}\n"
            logger_str += f"\tMulti-Region Writes: {database_account._EnableMultipleWritableLocations}\n"  # pylint: disable=protected-access, line-too-long

        return logger_str

def _format_error(payload: str) -> str:
    try:
        output = json.loads(payload)
        ret_str = "\n\t" + "Code: " + output['code'] + "\n"
        message = output["message"].replace("\r\n", "\n\t\t").replace(",", ",\n\t\t")
        ret_str += "\t" + message + "\n"
    except (json.JSONDecodeError, KeyError):
        try:
            ret_str = "\t" + payload.replace("\r\n", "\n\t\t").replace(",", ",\n\t\t") + "\n"
        except AttributeError:
            ret_str = str(payload)
    return ret_str


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
                retry_error = err
                # the request ran into a socket timeout or failed to establish a new connection
                # since request wasn't sent, raise exception immediately to be dealt with in client retry policies
                # This logic is based on the _retry.py file from azure-core
                if not _has_database_account_header(request.http_request.headers):
                    if retry_settings['connect'] > 0:
                        retry_active = self.increment(retry_settings, response=request, error=err)
                        if retry_active:
                            self.sleep(retry_settings, request.context.transport)
                            continue
                raise err
            except ServiceResponseError as err:
                retry_error = err
                # Only read operations can be safely retried with ServiceResponseError
                if (not _has_read_retryable_headers(request.http_request.headers) or
                        _has_database_account_header(request.http_request.headers)):
                    raise err

                # This logic is based on the _retry.py file from azure-core
                if retry_settings['read'] > 0:
                    retry_active = self.increment(retry_settings, response=request, error=err)
                    if retry_active:
                        self.sleep(retry_settings, request.context.transport)
                        continue
                raise err
            except CosmosHttpResponseError as err:
                raise err
            except AzureError as err:
                retry_error = err
                if _has_database_account_header(request.http_request.headers):
                    raise err
                if _has_read_retryable_headers(request.http_request.headers) and retry_settings['read'] > 0:
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
