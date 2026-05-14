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

"""Synchronized request in the Azure Cosmos database service.
"""
import copy
import json
import time
from concurrent.futures import CancelledError
from urllib.parse import urlparse

from azure.core.exceptions import DecodeError  # type: ignore

from . import exceptions, http_constants, _retry_utility
from ._availability_strategy_config import CrossRegionHedgingStrategy
from ._availability_strategy_handler import execute_with_hedging
from ._constants import _Constants
from ._diagnostics import _HedgingDetectionState, _attach_state_to_headers
from ._diagnostics_types import RequestedRegionReason
from ._request_object import RequestObject
from .documents import _OperationType

# cspell:ignore ppaf
def _is_readable_stream(obj):
    """Checks whether obj is a file-like readable stream.

    :param Union[str, unicode, file-like stream object, dict, list, None] obj: the object to be checked.
    :returns: whether the object is a file-like readable stream.
    :rtype: boolean
    """
    if hasattr(obj, "read") and callable(getattr(obj, "read")):
        return True
    return False


def _request_body_from_data(data):
    """Gets request body from data.

    When `data` is dict and list into unicode string; otherwise return `data`
    without making any change.

    :param Union[str, unicode, file-like stream object, dict, list, None] data:
    :returns: the json dump data.
    :rtype: Union[str, unicode, file-like stream object, None]

    """
    if data is None or isinstance(data, str) or _is_readable_stream(data):
        return data
    if isinstance(data, (dict, list, tuple)):
        json_dumped = json.dumps(data, separators=(",", ":"))

        return json_dumped
    return None


def _Request(global_endpoint_manager, request_params, connection_policy, pipeline_client, request, **kwargs): # pylint: disable=too-many-statements
    """Makes one http request using the requests module.

    :param _GlobalEndpointManager global_endpoint_manager:
    :param ~azure.cosmos._request_object.RequestObject request_params:
        contains information for the request, like the resource_type, operation_type, and endpoint_override
    :param documents.ConnectionPolicy connection_policy:
    :param azure.core.PipelineClient pipeline_client:
        Pipeline client to process the request
    :param azure.core.pipeline.transport.HttpRequest request:
        The request object to send through the pipeline
    :return: tuple of (result, headers)
    :rtype: tuple of (dict, dict)

    """
    # pylint: disable=protected-access, too-many-branches
    kwargs.pop(_Constants.OperationStartTime, None)
    # Pop internal flags that should not be passed to the HTTP layer
    kwargs.pop("_internal_pk_range_fetch", None)
    # Hedging-detection state is consumed by the orchestrator + retry layer
    # only; never forward to the HTTP pipeline.
    kwargs.pop("_hedging_state", None)
    connection_timeout = connection_policy.RequestTimeout
    connection_timeout = kwargs.pop("connection_timeout", connection_timeout)
    read_timeout = connection_policy.ReadTimeout
    read_timeout = kwargs.pop("read_timeout", read_timeout)

    # Every request tries to perform a refresh
    client_timeout = kwargs.get('timeout')
    start_time = time.time()
    if request_params.healthy_tentative_location:
        read_timeout = connection_policy.RecoveryReadTimeout
    if request_params.resource_type != http_constants.ResourceType.DatabaseAccount:
        global_endpoint_manager.refresh_endpoint_list(None, **kwargs)
    else:
        # always override database account call timeouts
        read_timeout = connection_policy.DBAReadTimeout
        connection_timeout = connection_policy.DBAConnectionTimeout

    if request_params.read_timeout_override:
        read_timeout = request_params.read_timeout_override

    if client_timeout is not None:
        kwargs['timeout'] = client_timeout - (time.time() - start_time)
        if kwargs['timeout'] <= 0:
            raise exceptions.CosmosClientTimeoutError()

    if request_params.endpoint_override:
        base_url = request_params.endpoint_override
    else:
        pk_range_wrapper = None
        if (global_endpoint_manager.is_circuit_breaker_applicable(request_params) or
                global_endpoint_manager.is_per_partition_automatic_failover_applicable(request_params)):
            # Circuit breaker or per-partition failover are applicable, so we need to use the endpoint from the request
            pk_range_wrapper = global_endpoint_manager.create_pk_range_wrapper(request_params)
        base_url = global_endpoint_manager.resolve_service_endpoint_for_partition(request_params, pk_range_wrapper)

    # For each retry, check if request should be cancelled due to sibling requests already completed
    # - used for when hedging enabled
    if request_params.should_cancel_request():
        raise CancelledError("The request has been cancelled")

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

    if connection_policy.SSLConfiguration or "connection_cert" in kwargs:
        ca_certs = connection_policy.SSLConfiguration.SSLCaCerts
        cert_files = (connection_policy.SSLConfiguration.SSLCertFile, connection_policy.SSLConfiguration.SSLKeyFile)
        response = _PipelineRunFunction(
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
        response = _PipelineRunFunction(
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


def _is_availability_strategy_applicable(request_params: RequestObject) -> bool:
    """Determine if availability strategy should be applied to the request.
    
    :param request_params: Request parameters containing operation details
    :type request_params: ~azure.cosmos._request_object.RequestObject
    :returns: True if availability strategy should be applied, False otherwise
    :rtype: bool
    """
    return (request_params.availability_strategy is not None and
            not request_params.is_hedging_request and
            request_params.resource_type == http_constants.ResourceType.Document and
            (not _OperationType.IsWriteOperation(request_params.operation_type) or
             request_params.retry_write > 0))


def _replace_url_prefix(original_url, new_prefix):
    parts = original_url.split('/', 3)

    if not new_prefix.endswith('/'):
        new_prefix += '/'

    new_url = new_prefix + parts[3] if len(parts) > 3 else new_prefix

    return new_url


def _PipelineRunFunction(pipeline_client, request, **kwargs):
    # pylint: disable=protected-access

    return pipeline_client._pipeline.run(request, **kwargs)

def SynchronizedRequest(
        client,
        request_params,
        global_endpoint_manager,
        connection_policy,
        pipeline_client,
        request,
        request_data,
        **kwargs
):
    """Performs one synchronized http request according to the parameters.

    :param object client: Document client instance
    :param request_params: Request parameters containing operation details
    :type request_params: ~azure.cosmos._request_object.RequestObject
    :param _GlobalEndpointManager global_endpoint_manager:
    :param documents.ConnectionPolicy connection_policy:
    :param azure.core.PipelineClient pipeline_client: PipelineClient to process the request.
    :param HttpRequest request: the HTTP request to be sent
    :param (str, unicode, file-like stream object, dict, list or None) request_data: the data to be sent in the request
    :return: tuple of (result, headers)
    :rtype: tuple of (dict dict)
    """
    request.data = _request_body_from_data(request_data)
    if request.data and isinstance(request.data, str):
        request.headers[http_constants.HttpHeaders.ContentLength] = len(request.data)
    elif request.data is None:
        request.headers[http_constants.HttpHeaders.ContentLength] = 0

    if request_params.availability_strategy is None:
        # if ppaf is enabled, then hedging is enabled by default
        if global_endpoint_manager.is_per_partition_automatic_failover_enabled():
            request_params.availability_strategy = CrossRegionHedgingStrategy()

    # ----- Hedging-detection: per-operation state -------------------------- #
    # Construct a state holder for this operation. Threaded through:
    #   * the hedging handler via the ``hedging_state`` closure argument
    #     (NOT on ``request_params`` — SE-002 / public-spec §5.4 / AC8).
    #   * ``_retry_utility.Execute`` via the ``_hedging_state`` kwarg.
    #   * back up to the wrapper-construction site (``CosmosDict``/``CosmosList``
    #     in ``_cosmos_client_connection``) by stashing on the response-headers
    #     dict under a private sentinel key (popped in each wrapper's
    #     ``__init__``).
    # Hedge-arm subtasks recursively re-enter ``SynchronizedRequest`` with
    # ``is_hedging_request=True``; they should reuse the parent state via the
    # kwarg rather than create a new one. We thus only create state for the
    # top-level dispatch.
    hedging_state: "Optional[_HedgingDetectionState]" = kwargs.get("_hedging_state")
    is_top_level = hedging_state is None and not request_params.is_hedging_request
    if is_top_level:
        hedging_state = _HedgingDetectionState()
        kwargs["_hedging_state"] = hedging_state

    # Handle hedging if availability strategy is applicable
    if _is_availability_strategy_applicable(request_params):
        result, headers = execute_with_hedging(
            request_params,
            global_endpoint_manager,
            request,
            lambda req_param, r: _retry_utility.Execute(
                client,
                global_endpoint_manager,
                _Request,
                req_param,
                connection_policy,
                pipeline_client,
                r,
                **kwargs
            ),
            hedging_state=hedging_state,
        )
        if is_top_level:
            _attach_state_to_headers(headers, hedging_state)
        return result, headers

    # Non-hedged path: record INITIAL once at orchestrator entry.
    if is_top_level and hedging_state is not None:
        # Best-effort region name from the resolved endpoint; falls back to
        # empty string when the endpoint cannot be resolved to a friendly name.
        region_name = _resolve_region_name(global_endpoint_manager, request_params)
        hedging_state._record_request(  # pylint: disable=protected-access
            region_name, RequestedRegionReason.INITIAL
        )

    # Pass _Request function with its parameters to retry_utility's Execute method that wraps the call with retries
    result, headers = _retry_utility.Execute(
        client,
        global_endpoint_manager,
        _Request,
        request_params,
        connection_policy,
        pipeline_client,
        request,
        **kwargs
    )
    if is_top_level and hedging_state is not None:
        # Best-effort: the responding region is the resolved endpoint for the
        # final attempt (post-retry). Same resolver as INITIAL above.
        region_name = _resolve_region_name(global_endpoint_manager, request_params)
        hedging_state._record_response(region_name)  # pylint: disable=protected-access
        _attach_state_to_headers(headers, hedging_state)
    return result, headers


def _resolve_region_name(global_endpoint_manager, request_params) -> str:
    """Best-effort resolution of the human-readable region name for the
    endpoint currently selected on ``request_params``. Returns an empty string
    if the name cannot be resolved (e.g., emulator, missing routing context).
    Never raises — the hot path must not break for diagnostics.

    :param global_endpoint_manager: The client's global endpoint manager.
        Used to map the resolved endpoint URL to a friendly region name.
    :type global_endpoint_manager: object
    :param request_params: The per-request :class:`RequestObject` whose
        currently selected endpoint should be resolved.
    :type request_params: ~azure.cosmos._request_object.RequestObject
    :returns: The friendly region name (e.g., ``"East US"``) for the endpoint
        currently routed to, or an empty string when no mapping is available.
    :rtype: str
    """
    try:
        endpoint = getattr(request_params, "location_endpoint_to_route", None)
        if endpoint and hasattr(global_endpoint_manager, "get_region_name"):
            is_write = _OperationType.IsWriteOperation(request_params.operation_type)
            name = global_endpoint_manager.get_region_name(endpoint, is_write)
            if name:
                return name
        # Fall back to the global endpoint manager's preferred read/write region.
        if hasattr(global_endpoint_manager, "get_write_endpoint_region"):
            try:
                name = global_endpoint_manager.get_write_endpoint_region()
                if name:
                    return name
            except Exception:  # pylint: disable=broad-except
                pass
    except Exception:  # pylint: disable=broad-except
        return ""
    return ""
