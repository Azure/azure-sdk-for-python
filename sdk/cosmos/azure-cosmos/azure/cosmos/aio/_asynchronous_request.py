# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

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

"""Asynchronous request in the Azure Cosmos database service.
"""
import copy
import json
import time
from datetime import datetime, timezone
import logging

from urllib.parse import urlparse
from azure.core.exceptions import DecodeError  # type: ignore

from .. import exceptions
from .. import http_constants
from . import _retry_utility_async
from .._request_object import RequestObject
from .._synchronized_request import _request_body_from_data, _replace_url_prefix
from .._utils import get_user_agent_features
from ..documents import _OperationType
from ..http_constants import ResourceType


async def _Request(global_endpoint_manager, request_params, connection_policy, pipeline_client, request, **kwargs): # pylint: disable=too-many-statements
    """Makes one http request using the requests module.

    :param _GlobalEndpointManager global_endpoint_manager:
    :param ~azure.cosmos._request_object.RequestObject request_params:
        contains information for the request, like the resource_type, operation_type, and endpoint_override
    :param documents.ConnectionPolicy connection_policy:
    :param azure.core.PipelineClient pipeline_client:
        Pipeline client to process the request
    :param azure.core.HttpRequest request:
        The request object to send through the pipeline
    :return: tuple of (result, headers)
    :rtype: tuple of (dict, dict)

    """
    # pylint: disable=protected-access

    connection_timeout = connection_policy.RequestTimeout
    read_timeout = connection_policy.ReadTimeout
    connection_timeout = kwargs.pop("connection_timeout", connection_timeout)
    read_timeout = kwargs.pop("read_timeout", read_timeout)

    # Every request tries to perform a refresh
    client_timeout = kwargs.get('timeout')
    start_time = time.time()
    if request_params.healthy_tentative_location:
        read_timeout = connection_policy.RecoveryReadTimeout
    if request_params.resource_type != http_constants.ResourceType.DatabaseAccount:
        await global_endpoint_manager.refresh_endpoint_list(None, **kwargs)
    else:
        # always override database account call timeouts
        read_timeout = connection_policy.DBAReadTimeout
        connection_timeout = connection_policy.DBAConnectionTimeout
    if client_timeout is not None:
        kwargs['timeout'] = client_timeout - (time.time() - start_time)
        if kwargs['timeout'] <= 0:
            raise exceptions.CosmosClientTimeoutError()

    route_start = time.perf_counter()

    if request_params.endpoint_override:
        base_url = request_params.endpoint_override
    else:
        pk_range_wrapper = None
        if (global_endpoint_manager.is_circuit_breaker_applicable(request_params) or
                global_endpoint_manager.is_per_partition_automatic_failover_applicable(request_params)):
            # Circuit breaker or per-partition failover are applicable, so we need to use the endpoint from the request
            pk_range_wrapper = await global_endpoint_manager.create_pk_range_wrapper(request_params)
        base_url = global_endpoint_manager.resolve_service_endpoint_for_partition(request_params, pk_range_wrapper)
    if not request.url.startswith(base_url):
        request.url = _replace_url_prefix(request.url, base_url)

    parse_result = urlparse(request.url)

    # The requests library now expects header values to be strings only starting 2.11,
    # and will raise an error on validation if they are not, so casting all header values to strings.
    request.headers.update({header: str(value) for header, value in request.headers.items()})

    # We are disabling the SSL verification for local emulator(localhost/127.0.0.1) or if the user
    # has explicitly specified to disable SSL verification.
    is_ssl_enabled = (
        parse_result.hostname != "localhost"
        and parse_result.hostname != "127.0.0.1"
        and not connection_policy.DisableSSLVerification
    )

    if request.headers['x-ms-thinclient-proxy-resource-type'] == "docs":
        user_agent_features = get_user_agent_features(global_endpoint_manager)
        if len(user_agent_features) > 0:
            user_agent = kwargs.pop("user_agent", global_endpoint_manager.client._user_agent)
            user_agent = "{} {}".format(user_agent, user_agent_features)
            kwargs.update({"user_agent": user_agent})
            kwargs.update({"user_agent_overwrite": True})

    route_end = time.perf_counter()
    route_duration = (route_end - route_start) * 1000
    start = time.perf_counter()

    if connection_policy.SSLConfiguration or "connection_cert" in kwargs:
        ca_certs = connection_policy.SSLConfiguration.SSLCaCerts
        cert_files = (connection_policy.SSLConfiguration.SSLCertFile, connection_policy.SSLConfiguration.SSLKeyFile)
        response = await _PipelineRunFunction(
            pipeline_client,
            request,
            connection_timeout=connection_timeout,
            read_timeout=read_timeout,
            connection_verify=kwargs.pop("connection_verify", ca_certs),
            connection_cert=kwargs.pop("connection_cert", cert_files),
            request_params=request_params,
            global_endpoint_manager=global_endpoint_manager,
            **kwargs
        )
    else:
        response = await _PipelineRunFunction(
            pipeline_client,
            request,
            connection_timeout=connection_timeout,
            read_timeout=read_timeout,
            # If SSL is disabled, verify = false
            connection_verify=kwargs.pop("connection_verify", is_ssl_enabled),
            request_params=request_params,
            global_endpoint_manager=global_endpoint_manager,
            **kwargs
        )

    end = time.perf_counter()
    duration = (end - start) * 1000

    logger = logging.getLogger("internal_requests")
    response_time = datetime.now(timezone.utc)
    print_string = f"Response time: {response_time.isoformat()} | "
    print_string += f"Request URL: {request.url} | "
    print_string += f"Resource type: {request.headers['x-ms-thinclient-proxy-resource-type']} | "
    print_string += f"Operation type: {request.headers['x-ms-thinclient-proxy-operation-type']} | "
    print_string += f"Status code: {response.http_response.status_code} | "
    print_string += f"Sub-status code: {response.http_response.headers.get('x-ms-substatus', 'N/A')} | "
    print_string += f"Routing duration: {route_duration} ms | "
    print_string += f"Request/response duration: {duration} ms | "
    print_string += f"Activity Id: {request.headers.get('x-ms-activity-id', 'N/A')} |"
    print_string += f"Partition Id: {response.http_response.headers.get('x-ms-cosmos-internal-partition-id', 'N/A')} |"
    print_string += f"Physical Id: {response.http_response.headers.get('x-ms-cosmos-physical-partition-id', 'N/A')} |"
    logger.info(print_string)
    print(print_string)

    response = response.http_response
    headers = copy.copy(response.headers)

    data = response.body()
    if data:
        data = data.decode("utf-8")

    if response.status_code == 404:
        raise exceptions.CosmosResourceNotFoundError(message=data, response=response)
    if response.status_code == 409:
        raise exceptions.CosmosResourceExistsError(message=data, response=response)
    if response.status_code == 412:
        raise exceptions.CosmosAccessConditionFailedError(message=data, response=response)
    if response.status_code >= 400:
        raise exceptions.CosmosHttpResponseError(message=data, response=response)

    result = None
    if data:
        try:
            result = json.loads(data)
        except Exception as e:
            raise DecodeError(
                message="Failed to decode JSON data: {}".format(e),
                response=response,
                error=e) from e

    return result, headers


async def _PipelineRunFunction(pipeline_client, request, **kwargs):
    # pylint: disable=protected-access

    return await pipeline_client._pipeline.run(request, **kwargs)

def _is_availability_strategy_applicable(request_params: RequestObject) -> bool:
    """Determine if availability strategy should be applied to the request.

    :param request_params: Request parameters containing operation details
    :type request_params: ~azure.cosmos._request_object.RequestObject
    :returns: True if availability strategy should be applied, False otherwise
    :rtype: bool
    """
    return (request_params.availability_strategy_config is not None and
            not request_params.is_hedging_request and
            request_params.resource_type == ResourceType.Document and
            (not _OperationType.IsWriteOperation(request_params.operation_type) or
             request_params.retry_write > 0))

async def AsynchronousRequest(
    client,
    request_params,
    global_endpoint_manager,
    connection_policy,
    pipeline_client,
    request,
    request_data,
    **kwargs
):
    """Performs one asynchronous http request according to the parameters.

    :param object client: Document client instance
    :param dict request_params:
    :param _GlobalEndpointManager global_endpoint_manager:
    :param documents.ConnectionPolicy connection_policy:
    :param azure.core.PipelineClient pipeline_client: PipelineClient to process the request.
    :param HttpRequest request: the HTTP request to be sent
    :param (str, unicode, file-like stream object, dict, list or None) request_data:
    :return: tuple of (result, headers)
    :rtype: tuple of (dict dict)
    """
    request.data = _request_body_from_data(request_data)
    if request.data and isinstance(request.data, str):
        request.headers[http_constants.HttpHeaders.ContentLength] = len(request.data)
    elif request.data is None:
        request.headers[http_constants.HttpHeaders.ContentLength] = 0

    # Pass _Request function with its parameters to retry_utility's Execute method that wraps the call with retries
    return await _retry_utility_async.ExecuteAsync(
        client,
        global_endpoint_manager,
        _Request,
        request_params,
        connection_policy,
        pipeline_client,
        request,
        **kwargs
    )