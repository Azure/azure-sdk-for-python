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

from urllib.parse import urlparse
from azure.core.exceptions import DecodeError  # type: ignore

from .. import exceptions
from .. import http_constants
from . import _retry_utility_async
from .._synchronized_request import _request_body_from_data


async def _Request(global_endpoint_manager, request_params, connection_policy, pipeline_client, request, **kwargs):
    """Makes one http request using the requests module.

    :param _GlobalEndpointManager global_endpoint_manager:
    :param dict request_params:
        contains the resourceType, operationType, endpointOverride,
        useWriteEndpoint, useAlternateWriteEndpoint information
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
    connection_timeout = kwargs.pop("connection_timeout", connection_timeout)

    # Every request tries to perform a refresh
    client_timeout = kwargs.get('timeout')
    start_time = time.time()
    await global_endpoint_manager.refresh_endpoint_list(None, **kwargs)
    if client_timeout is not None:
        kwargs['timeout'] = client_timeout - (time.time() - start_time)
        if kwargs['timeout'] <= 0:
            raise exceptions.CosmosClientTimeoutError()

    if request_params.endpoint_override:
        base_url = request_params.endpoint_override
    else:
        base_url = global_endpoint_manager.resolve_service_endpoint(request_params)
    if base_url != pipeline_client._base_url:
        request.url = request.url.replace(pipeline_client._base_url, base_url)

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

    if connection_policy.SSLConfiguration or "connection_cert" in kwargs:
        ca_certs = connection_policy.SSLConfiguration.SSLCaCerts
        cert_files = (connection_policy.SSLConfiguration.SSLCertFile, connection_policy.SSLConfiguration.SSLKeyFile)
        response = await _PipelineRunFunction(
            pipeline_client,
            request,
            connection_timeout=connection_timeout,
            connection_verify=kwargs.pop("connection_verify", ca_certs),
            connection_cert=kwargs.pop("connection_cert", cert_files),
            **kwargs
        )
    else:
        response = await _PipelineRunFunction(
            pipeline_client,
            request,
            connection_timeout=connection_timeout,
            # If SSL is disabled, verify = false
            connection_verify=kwargs.pop("connection_verify", is_ssl_enabled),
            **kwargs
        )

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
