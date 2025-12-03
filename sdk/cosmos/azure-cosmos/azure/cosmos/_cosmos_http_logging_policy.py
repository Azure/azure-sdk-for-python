# -*- coding: utf-8 -*-
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


"""Http Logging Policy for Azure SDK"""

import sys
import json
import logging
import time
import os
import urllib.parse
from logging import Logger
from typing import Optional, Union, TYPE_CHECKING, Set, Tuple, Type, Any
import types

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import HttpLoggingPolicy
from azure.core.exceptions import ServiceRequestError, ServiceResponseError

from .http_constants import HttpHeaders, _cosmos_allow_list
from ._global_endpoint_manager import _GlobalEndpointManager
from .exceptions import CosmosHttpResponseError

if TYPE_CHECKING:
    from azure.core.rest import HttpRequest, HttpResponse, AsyncHttpResponse
    from azure.core.pipeline.transport import (  # pylint: disable=no-legacy-azure-core-http-response-import
        HttpRequest as LegacyHttpRequest,
        HttpResponse as LegacyHttpResponse,
        AsyncHttpResponse as LegacyAsyncHttpResponse,
    )
    from azure.core.pipeline.transport._base import _HttpResponseBase as LegacySansIOHttpResponse
    from azure.core.rest._rest_py3 import _HttpResponseBase as SansIOHttpResponse
    from ._location_cache import LocationCache
    from .documents import DatabaseAccount, ConnectionPolicy

HTTPRequestType = Union["LegacyHttpRequest", "HttpRequest"]
HTTPResponseType = Union["LegacyHttpResponse", "HttpResponse", "LegacyAsyncHttpResponse",
"AsyncHttpResponse", "SansIOHttpResponse", "LegacySansIOHttpResponse"]


# These Helper functions are used to Log Diagnostics for the SDK outside on_request and on_response
def _populate_logger_attributes(  # type: ignore[attr-defined, union-attr]
                            logger_attributes: Optional[dict[str, Any]] = None,
                            request: Optional[Union[PipelineRequest[HTTPRequestType], Any]] = None,
                            exception: Optional[Union[CosmosHttpResponseError,
                            ServiceRequestError, ServiceResponseError]] = None) -> dict[str, Any]:
    """Populates the logger attributes with the request and response details.

    :param logger_attributes: Optional[dict[str, Any]], The logger attributes to populate.
    :type logger_attributes: Optional[dict[str, Any]]
    :param request: Optional[Union[PipelineRequest[HTTPRequestType], Any]], The request object containing HTTP details.
    :type request: Optional[Union[PipelineRequest[HTTPRequestType], Any]]
    :param exception: Optional[Union[CosmosHttpResponseError, ServiceRequestError, ServiceResponseError]],
        The exception object, if any.
    :type exception: Optional[Union[CosmosHttpResponseError, ServiceRequestError, ServiceResponseError]]
    :return: The logger attributes populated with the request and response details.
    :rtype: dict[str, Any]
    """

    if not logger_attributes:
        logger_attributes = {}

    http_request = request.http_request if isinstance(request, PipelineRequest) else None

    if http_request:
        logger_attributes["activity_id"] = http_request.headers.get(HttpHeaders.ActivityId, "")
        logger_attributes["verb"] = http_request.method
        logger_attributes["url"] = http_request.url
        logger_attributes["operation_type"] = http_request.headers.get(
            'x-ms-thinclient-proxy-operation-type')
        logger_attributes["resource_type"] = http_request.headers.get(
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


def _log_diagnostics_error(  # type: ignore[attr-defined, union-attr]
                            diagnostics_enabled: bool = False,
                            request: Optional[PipelineRequest[HTTPRequestType]] = None,
                            response_headers: Optional[dict] = None, error: Optional[Union[CosmosHttpResponseError,
                            ServiceRequestError, ServiceResponseError]] = None,
                            logger_attributes: Optional[dict] = None,
                            global_endpoint_manager: Optional[_GlobalEndpointManager] = None,
                            logger: Optional[Logger] = None):
    """Logs the request and response error details to the logger.

    :param diagnostics_enabled: Whether diagnostics logging is enabled.
    :type diagnostics_enabled: bool
    :param request: The request object containing HTTP details.
    :type request: Optional[PipelineRequest[HTTPRequestType]]
    :param response_headers: The response headers from the HTTP response.
    :type response_headers: Optional[dict[str, Any]]
    :param error: The error object, if any.
    :type error: Optional[Union[CosmosHttpResponseError, ServiceRequestError, ServiceResponseError]]
    :param logger_attributes: The logger attributes to populate.
    :type logger_attributes: Optional[dict[str, Any]]
    :param global_endpoint_manager: The global endpoint manager instance.
    :type global_endpoint_manager: Optional[_GlobalEndpointManager]
    :param logger: The logger instance to use.
    :type logger: Optional[logging.Logger]
    """
    if diagnostics_enabled:
        logger = logger or logging.getLogger("azure.cosmos._cosmos_http_logging_policy")
        logger_attributes = _populate_logger_attributes(logger_attributes,
                                                        request, error)
        log_string: str = _get_client_settings(global_endpoint_manager)
        log_string += _get_database_account_settings(global_endpoint_manager)
        http_request = request.http_request if request else None
        if http_request:
            log_string += f"\nRequest URL: {http_request.url}"
            log_string += f"\nRequest method: {http_request.method}"
            log_string += "\nRequest Activity ID: {}".format(http_request.headers.get(HttpHeaders.ActivityId))
            log_string += "\nRequest headers:"
            for header, value in http_request.headers.items():
                value = _redact_header(header, value)
                if value and value != "REDACTED":
                    log_string += "\n    '{}': '{}'".format(header, value)
        log_string += "\nResponse status: {}".format(logger_attributes.get("status_code", ""))
        if response_headers:
            log_string += "\nResponse Activity ID: {}".format(
                response_headers.get(HttpHeaders.ActivityId, logger_attributes.get("activity_id", "")))
            log_string += "\nResponse headers: "
            for res_header, value in response_headers.items():
                value = _redact_header(res_header, value)
                if value and value != "REDACTED":
                    log_string += "\n    '{}': '{}'".format(res_header, value)
        if "duration" in logger_attributes:
            seconds = logger_attributes["duration"] / 1000  # type: ignore[operator]
            log_string += f"\nElapsed time in seconds: {seconds:.6f}".rstrip('0').rstrip('.')
        log_string += "\nResponse error message: {}".format(_format_error(getattr(error, 'message', str(error))))
        logger.info(log_string, extra=logger_attributes)


def _get_client_settings(global_endpoint_manager: Optional[_GlobalEndpointManager]) -> str:
    # Place any client settings we want to log here
    client_preferred_regions = []
    client_excluded_regions: Optional[list[str]] = []
    client_account_read_regions = []
    client_account_write_regions = []

    if global_endpoint_manager:
        if hasattr(global_endpoint_manager, 'client'):
            gem_client = global_endpoint_manager.client
            if gem_client and gem_client.connection_policy:
                connection_policy: ConnectionPolicy = gem_client.connection_policy
                client_preferred_regions = global_endpoint_manager.location_cache.effective_preferred_locations
                client_excluded_regions = connection_policy.ExcludedLocations

        if global_endpoint_manager.location_cache:
            location_cache: LocationCache = global_endpoint_manager.location_cache
            client_account_read_regions = location_cache.account_read_locations
            client_account_write_regions = location_cache.account_write_locations
    logger_str = "Client Settings: \n"
    client_settings = {"Preferred Regions": client_preferred_regions,
                       "Excluded Regions": client_excluded_regions,
                       "Account Read Regions": client_account_read_regions,
                       "Account Write Regions": client_account_write_regions}
    if client_settings and isinstance(client_settings, dict):
        logger_str += ''.join([f"\t{k}: {v}\n" for k, v in client_settings.items()])
    return logger_str


def _get_database_account_settings(global_endpoint_manager: Optional[_GlobalEndpointManager]) \
        -> str:
    database_account: Optional["DatabaseAccount"] = None
    if global_endpoint_manager and hasattr(global_endpoint_manager, '_database_account_cache'):
        database_account = global_endpoint_manager._database_account_cache  # pylint: disable=protected-access, line-too-long

    logger_str = "\nDatabase Account Settings: \n"
    if database_account and database_account.ConsistencyPolicy:
        logger_str += f"\tConsistency Level: {database_account.ConsistencyPolicy.get('defaultConsistencyLevel')}\n"
        logger_str += f"\tWritable Locations: {database_account.WritableLocations}\n"
        logger_str += f"\tReadable Locations: {database_account.ReadableLocations}\n"
        logger_str += f"\tMulti-Region Writes: {database_account._EnableMultipleWritableLocations}\n"  # pylint: disable=protected-access, line-too-long

    return logger_str


def _redact_header(key: str, value: str) -> str:
    if key.lower() in _cosmos_allow_list:
        return value
    return HttpLoggingPolicy.REDACTED_PLACEHOLDER


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


def _iter_loggers(logger):
    while logger:
        yield logger
        logger = logger.parent if logger.parent else None


class CosmosHttpLoggingPolicy(HttpLoggingPolicy):

    def __init__(
            self,
            logger: Optional[logging.Logger] = None,
            global_endpoint_manager: Optional[_GlobalEndpointManager] = None,
            *,
            enable_diagnostics_logging: bool = False,
            **kwargs
    ):
        super().__init__(logger, **kwargs)
        self.logger: logging.Logger = logger or logging.getLogger("azure.cosmos._cosmos_http_logging_policy")
        self._enable_diagnostics_logging = enable_diagnostics_logging
        self.__global_endpoint_manager = global_endpoint_manager
        # The list of headers we do not want to log, it needs to be updated if any new headers should not be logged
        cosmos_allow_list = _cosmos_allow_list
        self.allowed_header_names = set(cosmos_allow_list)
        # For optimizing header redaction. We create the set with lower case allowed headers
        self.lower_case_allowed_header_names: Set[str] = {header.lower() for header in self.allowed_header_names}
        self.lower_case_allowed_query_params: Set[str] = {param.lower() for param in self.allowed_query_params}

    def _redact_query_param(self, key: str, value: str) -> str:
        return value if key.lower() in self.lower_case_allowed_query_params else HttpLoggingPolicy.REDACTED_PLACEHOLDER

    def _redact_header(self, key: str, value: str) -> str:
        return _redact_header(key, value)

    def on_request(
            # pylint: disable=too-many-return-statements, too-many-statements, too-many-nested-blocks, too-many-branches
            # pylint: disable=too-many-locals
            self, request: PipelineRequest[HTTPRequestType]
    ) -> None:
        """Logs HTTP method, url and headers.
        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        if self._enable_diagnostics_logging:

            http_request = request.http_request
            if "start_time" not in request.context:
                request.context["start_time"] = time.time()
            options = request.context.options
            # Get logger in my context first (request has been retried)
            # then read from kwargs (pop if that's the case)
            # then use my instance logger
            logger = request.context.setdefault("logger", options.pop("logger", self.logger))
            # If filtered is applied, and we are not calling on request from on response, just return to avoid logging
            # the request again
            filter_applied = any(
                bool(current_logger.filters) or any(bool(h.filters) for h in current_logger.handlers)
                for current_logger in _iter_loggers(logger))
            if filter_applied and 'logger_attributes' not in request.context:
                return
            operation_type = http_request.headers.get('x-ms-thinclient-proxy-operation-type', "")
            try:
                url = request.http_request.url
            except AttributeError:
                url = None
            database_name = None
            collection_name = None
            resource_type = http_request.headers.get('x-ms-thinclient-proxy-resource-type', "")
            if url:
                url_parts = url.split('/')
                if 'dbs' in url_parts:
                    dbs_index = url_parts.index('dbs')
                    if dbs_index + 1 < len(url_parts):
                        database_name = url_parts[url_parts.index('dbs') + 1]
                if 'colls' in url_parts:
                    colls_index = url_parts.index('colls')
                    if colls_index + 1 < len(url_parts):
                        collection_name = url_parts[url_parts.index('colls') + 1]

            if not logger.isEnabledFor(logging.INFO):
                return
            try:
                parsed_url = list(urllib.parse.urlparse(http_request.url))
                parsed_qp = urllib.parse.parse_qsl(parsed_url[4], keep_blank_values=True)
                filtered_qp = [(key, self._redact_query_param(key, value)) for key, value in parsed_qp]
                # 4 is query
                parsed_url[4] = "&".join(["=".join(part) for part in filtered_qp])
                redacted_url = urllib.parse.urlunparse(parsed_url)

                multi_record = os.environ.get(HttpLoggingPolicy.MULTI_RECORD_LOG, False)

                if filter_applied and 'logger_attributes' in request.context:
                    cosmos_logger_attributes = request.context['logger_attributes']
                    cosmos_logger_attributes['activity_id'] = http_request.headers.get(HttpHeaders.ActivityId, "")
                    cosmos_logger_attributes['is_request'] = True
                else:
                    cosmos_logger_attributes = {
                        'activity_id': http_request.headers.get(HttpHeaders.ActivityId, ""),
                        'duration': None,
                        'status_code': None,
                        'sub_status_code': None,
                        'verb': http_request.method,
                        'url': redacted_url,
                        'database_name': database_name,
                        'collection_name': collection_name,
                        'resource_type': resource_type,
                        'operation_type': operation_type,
                        'exception_type': "",
                        'is_request': True}

                client_settings = self._log_client_settings()
                db_settings = self._log_database_account_settings()
                if multi_record:
                    logger.info(client_settings, extra=cosmos_logger_attributes)
                    logger.info(db_settings, extra=cosmos_logger_attributes)
                    logger.info("Request URL: %r", redacted_url, extra=cosmos_logger_attributes)
                    logger.info("Request method: %r", http_request.method, extra=cosmos_logger_attributes)
                    logger.info("Request Activity ID: %r", http_request.headers.get(HttpHeaders.ActivityId, ""),
                                extra=cosmos_logger_attributes)
                    logger.info("Request headers:", extra=cosmos_logger_attributes)
                    for header, value in http_request.headers.items():
                        value = self._redact_header(header, value)
                        if value and value != HttpLoggingPolicy.REDACTED_PLACEHOLDER:
                            logger.info("    %r: %r", header, value, extra=cosmos_logger_attributes)
                    if isinstance(http_request.body, types.GeneratorType):
                        logger.info("File upload", extra=cosmos_logger_attributes)
                        return
                    try:
                        if isinstance(http_request.body, types.AsyncGeneratorType):
                            logger.info("File upload", extra=cosmos_logger_attributes)
                            return
                    except AttributeError:
                        pass
                    if http_request.body:
                        logger.info("A body is sent with the request", extra=cosmos_logger_attributes)
                        return
                    logger.info("No body was attached to the request", extra=cosmos_logger_attributes)
                    return
                log_string = client_settings
                log_string += db_settings
                log_string += "\nRequest URL: '{}'".format(redacted_url)
                log_string += "\nRequest method: '{}'".format(http_request.method)
                log_string += "\nRequest Activity ID: '{}'".format(http_request.headers.get(HttpHeaders.ActivityId, ""))
                log_string += "\nRequest headers:"
                for header, value in http_request.headers.items():
                    value = self._redact_header(header, value)
                    if value and value != HttpLoggingPolicy.REDACTED_PLACEHOLDER:
                        log_string += "\n    '{}': '{}'".format(header, value)
                if isinstance(http_request.body, types.GeneratorType):
                    log_string += "\nFile upload"
                    logger.info(log_string, extra=cosmos_logger_attributes)
                    return
                try:
                    if isinstance(http_request.body, types.AsyncGeneratorType):
                        log_string += "\nFile upload"
                        logger.info(log_string, extra=cosmos_logger_attributes)
                        return
                except AttributeError:
                    pass
                if http_request.body:
                    log_string += "\nA body is sent with the request"
                    logger.info(log_string, extra=cosmos_logger_attributes)
                    return
                log_string += "\nNo body was attached to the request"
                logger.info(log_string, extra=cosmos_logger_attributes)
                request.context.pop("logger_attributes", None)

            except Exception as err:  # pylint: disable=broad-except
                logger.warning("Failed to log request: %s",
                               repr(err))  # pylint: disable=do-not-log-exceptions-if-not-debug
            return
        super().on_request(request)

    def on_response(  # pylint: disable=too-many-statements, too-many-branches, too-many-locals
            self,
            request: PipelineRequest[HTTPRequestType],
            response: PipelineResponse[HTTPRequestType, HTTPResponseType],
    ) -> None:

        if self._enable_diagnostics_logging:
            context = request.context
            http_response = response.http_response
            headers = request.http_request.headers
            sub_status_str = http_response.headers.get("x-ms-substatus")
            sub_status_code: Optional[int] = int(sub_status_str) if sub_status_str else 0
            url_obj = request.http_request.url  # type: ignore[attr-defined, union-attr]
            duration = (time.time() - context["start_time"]) * 1000 \
                    if "start_time" in context else ""  # type: ignore[union-attr, arg-type]

            log_data = {"activity_id": headers.get(HttpHeaders.ActivityId, ""),
                        "duration": duration,
                        "status_code": http_response.status_code, "sub_status_code": sub_status_code,
                        "verb": request.http_request.method,
                        "operation_type": headers.get('x-ms-thinclient-proxy-operation-type', ""),
                        "url": str(url_obj), "database_name": "", "collection_name": "",
                        "resource_type": headers.get('x-ms-thinclient-proxy-resource-type', ""),
                        "exception_type": "",
                        "is_request": False}  # type: ignore[assignment]
            log_data["exception_type"] = CosmosHttpResponseError.__name__ if log_data["status_code"] and \
                                                                             isinstance(log_data["status_code"],
                                                                                        int) and log_data[
                                                                                 "status_code"] >= 400 else ""
            if log_data["url"]:
                url_parts: list[str] = log_data["url"].split('/')  # type: ignore[union-attr]
                if 'dbs' in url_parts:
                    dbs_index = url_parts.index('dbs')
                    if dbs_index + 1 < len(url_parts):
                        log_data["database_name"] = url_parts[dbs_index + 1]
                if 'colls' in url_parts:
                    colls_index = url_parts.index('colls')
                    if colls_index + 1 < len(url_parts):
                        log_data["collection_name"] = url_parts[colls_index + 1]

            options = context.options
            logger = context.setdefault("logger", options.pop("logger", self.logger))
            filter_applied = any(
                bool(current_logger.filters) or any(bool(h.filters) for h in current_logger.handlers)
                for current_logger in _iter_loggers(logger))
            if filter_applied:
                context["logger_attributes"] = log_data.copy()
                self.on_request(request)

            try:
                if not logger.isEnabledFor(logging.INFO):
                    return

                multi_record = os.environ.get(HttpLoggingPolicy.MULTI_RECORD_LOG, False)
                if multi_record:
                    logger.info("Response status: %r", log_data["status_code"], extra=log_data)
                    logger.info(
                        "\nResponse Activity ID: {}".format(http_response.headers.get(HttpHeaders.ActivityId,
                                                                                      log_data["activity_id"])),
                        extra=log_data)
                    logger.info("Response headers:", extra=log_data)
                    for res_header, value in http_response.headers.items():
                        value = self._redact_header(res_header, value)
                        if value and value != HttpLoggingPolicy.REDACTED_PLACEHOLDER:
                            logger.info("    %r: %r", res_header, value, extra=log_data)
                    if "start_time" in context and duration:
                        seconds = duration / 1000  # type: ignore[operator]
                        logger.info(f"Elapsed time in seconds: {seconds:.6f}".rstrip('0').rstrip('.'),
                                    extra=log_data)
                    else:
                        logger.info("Elapsed time in seconds: unknown", extra=log_data)
                    if isinstance(log_data["status_code"], int) and log_data["status_code"] >= 400:
                        logger.info("\nResponse error message: %r", _format_error(http_response.text()),
                                    extra=log_data)
                    return
                log_string = "\nResponse status: {}".format(log_data["status_code"])
                log_string += "\nResponse Activity ID: {}".format(http_response.headers.get(HttpHeaders.ActivityId, ""))
                log_string += "\nResponse headers:"
                for res_header, value in http_response.headers.items():
                    value = self._redact_header(res_header, value)
                    if value and value != HttpLoggingPolicy.REDACTED_PLACEHOLDER:
                        log_string += "\n    '{}': '{}'".format(res_header, value)
                if "start_time" in context and duration:
                    seconds = duration / 1000  # type: ignore[operator]
                    log_string += f"\nElapsed time in seconds: {seconds:.6f}".rstrip('0').rstrip('.')
                else:
                    log_string += "\nElapsed time in seconds: unknown"
                if isinstance(log_data["status_code"], int) and log_data["status_code"] >= 400:
                    log_string += "\nResponse error message: {}".format(_format_error(http_response.text()))
                logger.info(log_string, extra=log_data)
            except Exception as err:  # pylint: disable=broad-except
                logger.warning("Failed to log response: %s", repr(err),
                               extra=log_data)  # pylint: disable=do-not-log-exceptions-if-not-debug
            return
        super().on_response(request, response)

    def on_exception( # pylint: disable=too-many-statements
            self,
            request: PipelineRequest[HTTPRequestType],
    ) -> None:

        """Handles exceptions raised during the pipeline request.

               Logs the exception details if diagnostics logging is enabled.
        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        """

        exc_info: Tuple[
            Optional[Type[BaseException]], Optional[BaseException],
            Optional[types.TracebackType]] = sys.exc_info()

        if self._enable_diagnostics_logging and exc_info[0] in (CosmosHttpResponseError, ServiceRequestError,
                                                             ServiceResponseError):
            exc_type: Optional[Type[Union[CosmosHttpResponseError, ServiceRequestError,
            ServiceResponseError]]] = exc_info[0]  # type: ignore[assignment]
            exc_value: Optional[Union[CosmosHttpResponseError,
            ServiceRequestError, ServiceResponseError]] = exc_info[1]  # type: ignore[assignment]
            logger: Logger = self.logger
            filter_applied: bool = any(
                bool(current_logger.filters) or any(bool(h.filters) for h in current_logger.handlers)
                for current_logger in _iter_loggers(logger)
            )
            logger_attributes: dict = {}
            duration: Union[float, int, str] = ""
            context: dict = {}
            if request:
                logger = request.context.setdefault("logger", request.context.options.pop("logger", self.logger))
                filter_applied = any(
                    bool(current_logger.filters) or any(bool(h.filters) for h in current_logger.handlers)
                    for current_logger in _iter_loggers(logger))
                context = request.context
                duration = (time.time() - context["start_time"]) * 1000 \
                    if "start_time" in context else ""  # type: ignore[union-attr, arg-type]
                logger_attributes["duration"] = duration
                logger_attributes["activity_id"] = request.http_request.headers.get(HttpHeaders.ActivityId, "")
                logger_attributes["verb"] = request.http_request.method
                logger_attributes["url"] = request.http_request.url
                logger_attributes["operation_type"] = request.http_request.headers.get(
                    'x-ms-thinclient-proxy-operation-type')
                logger_attributes["resource_type"] = request.http_request.headers.get(
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
            if exc_value:
                if hasattr(exc_value, 'status_code'):
                    logger_attributes["status_code"] = exc_value.status_code
                if hasattr(exc_value, 'sub_status'):
                    logger_attributes["sub_status_code"] = exc_value.sub_status
            logger_attributes["exception_type"] = exc_type.__name__ if exc_type else "UnknownException"
            if filter_applied:
                context["logger_attributes"] = logger_attributes.copy()
                self.on_request(request)
            log_string = "\nException without response occurred during the request processing."

            log_string += "\nActivity ID: {}".format(logger_attributes["activity_id"])

            if "start_time" in context and duration:
                seconds = duration / 1000  # type: ignore[operator]
                log_string += f"\nElapsed time in seconds from initial request: {seconds:.6f}".rstrip('0').rstrip('.')
            else:
                log_string += "\nElapsed time in seconds from initial request: unknown"
            log_string += "\nResponse status: {}".format(logger_attributes.get("status_code", ""))
            message = exc_value.message if hasattr(exc_value, 'message') else str(exc_value)  # type: ignore[union-attr]
            log_string += "\nResponse error message: {}".format(_format_error(message))
            logger.info(log_string, extra=logger_attributes)
        else:
            super().on_exception(request)

    def _log_client_settings(self) -> str:
        return _get_client_settings(self.__global_endpoint_manager)

    # pylint: disable=protected-access
    def _log_database_account_settings(self) -> str:
        return _get_database_account_settings(self.__global_endpoint_manager)
