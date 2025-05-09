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

import json
import logging
import time
import os
import urllib.parse
from typing import Optional, Union, Dict, Any, TYPE_CHECKING, Set, List
import types

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import HttpLoggingPolicy

from ._location_cache import LocationCache
from .http_constants import HttpHeaders
from ._global_endpoint_manager import _GlobalEndpointManager
from .documents import DatabaseAccount

if TYPE_CHECKING:
    from azure.core.rest import HttpRequest, HttpResponse, AsyncHttpResponse
    from azure.core.pipeline.transport import (  # pylint: disable=no-legacy-azure-core-http-response-import
        HttpRequest as LegacyHttpRequest,
        HttpResponse as LegacyHttpResponse,
        AsyncHttpResponse as LegacyAsyncHttpResponse,
    )
    from azure.core.pipeline.transport._base import _HttpResponseBase as LegacySansIOHttpResponse
    from azure.core.rest._rest_py3 import _HttpResponseBase as SansIOHttpResponse

HTTPRequestType = Union["LegacyHttpRequest", "HttpRequest"]
HTTPResponseType = Union["LegacyHttpResponse", "HttpResponse", "LegacyAsyncHttpResponse",
"AsyncHttpResponse", "SansIOHttpResponse", "LegacySansIOHttpResponse"]


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


class CosmosHttpLoggingPolicy(HttpLoggingPolicy):

    def __init__(
            self,
            logger: Optional[logging.Logger] = None,
            global_endpoint_manager: Optional[_GlobalEndpointManager] = None,
            database_account: Optional[DatabaseAccount] = None,
            *,
            enable_diagnostics_logging: bool = False,
            **kwargs
    ):
        super().__init__(logger, **kwargs)
        self.logger: logging.Logger = logger or logging.getLogger("azure.cosmos._cosmos_http_logging_policy")
        self._enable_diagnostics_logging = enable_diagnostics_logging
        self.__global_endpoint_manager = global_endpoint_manager
        self.__database_account_settings: Optional[DatabaseAccount] = (database_account or
                                                                       self.__get_database_account_settings())
        # The list of headers we do not want to log, it needs to be updated if any new headers should not be logged
        cosmos_disallow_list = ["Authorization", "ProxyAuthorization", "TransferEncoding"]
        cosmos_allow_list = [
            v for k, v in HttpHeaders.__dict__.items() if not k.startswith("_") and k not in cosmos_disallow_list
        ]
        self.allowed_header_names = set(cosmos_allow_list)
        # For optimizing header redaction. We create the set with lower case allowed headers
        self.lower_case_allowed_header_names: Set[str] = {header.lower() for header in self.allowed_header_names}
        self.lower_case_allowed_query_params: Set[str] = {param.lower() for param in self.allowed_query_params}

    def _redact_query_param(self, key: str, value: str) -> str:
        return value if key.lower() in self.lower_case_allowed_query_params else HttpLoggingPolicy.REDACTED_PLACEHOLDER

    def _redact_header(self, key: str, value: str) -> str:
        if key.lower() in self.lower_case_allowed_header_names:
            return value
        return HttpLoggingPolicy.REDACTED_PLACEHOLDER

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
            filter_applied = bool(logger.filters) or any(bool(h.filters) for h in logger.handlers)
            if filter_applied and 'logger_attributes' not in request.context:
                return
            operation_type = http_request.headers.get('x-ms-thinclient-proxy-operation-type')
            try:
                url = request.http_request.url
            except AttributeError:
                url = None
            database_name = None
            collection_name = None
            resource_type = http_request.headers.get('x-ms-thinclient-proxy-resource-type')
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
                    cosmos_logger_attributes['is_request'] = True
                else:
                    cosmos_logger_attributes = {
                        'duration': None,
                        'status_code': None,
                        'sub_status_code': None,
                        'verb': http_request.method,
                        'url': redacted_url,
                        'database_name': database_name,
                        'collection_name': collection_name,
                        'resource_type': resource_type,
                        'operation_type': operation_type,
                        'is_request': True}

                client_settings = self._log_client_settings()
                db_settings = self._log_database_account_settings()
                if multi_record:
                    logger.info(client_settings, extra=cosmos_logger_attributes)
                    logger.info(db_settings, extra=cosmos_logger_attributes)
                    logger.info("Request URL: %r", redacted_url, extra=cosmos_logger_attributes)
                    logger.info("Request method: %r", http_request.method, extra=cosmos_logger_attributes)
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

            except Exception as err:  # pylint: disable=broad-except
                logger.warning("Failed to log request: %s", repr(err)) #pylint: disable=do-not-log-exceptions-if-not-debug
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
            try:
                duration: Optional[float] = float(http_response.headers.get("x-ms-request-duration-ms"))  # type: ignore[union-attr, arg-type]  # pylint: disable=line-too-long
            except (ValueError, TypeError):
                duration = (time.time() - context["start_time"]) * 1000 \
                    if "start_time" in context else None  # type: ignore[union-attr, arg-type]

            log_data = {"duration": duration,
                        "status_code": http_response.status_code, "sub_status_code": sub_status_code,
                        "verb": request.http_request.method,
                        "operation_type": headers.get('x-ms-thinclient-proxy-operation-type'),
                        "url": str(url_obj), "database_name": "", "collection_name": "",
                        "resource_type": headers.get('x-ms-thinclient-proxy-resource-type'), "is_request": False}  # type: ignore[assignment]  # pylint: disable=line-too-long

            if log_data["url"]:
                url_parts: List[str] = log_data["url"].split('/')  # type: ignore[union-attr]
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
            filter_applied = bool(logger.filters) or any(bool(h.filters) for h in logger.handlers)
            if filter_applied:
                context["logger_attributes"] = log_data.copy()
                self.on_request(request)

            try:
                if not logger.isEnabledFor(logging.INFO):
                    return

                multi_record = os.environ.get(HttpLoggingPolicy.MULTI_RECORD_LOG, False)
                if multi_record:
                    logger.info("Response status: %r", log_data["status_code"], extra=log_data)
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
                logger.warning("Failed to log response: %s", repr(err), extra=log_data) #pylint: disable=do-not-log-exceptions-if-not-debug
            return
        super().on_response(request, response)

    def __get_client_settings(self) -> Optional[Dict[str, Any]]:
        # Place any client settings we want to log here
        client_preferred_regions = []
        client_excluded_regions = []
        client_account_read_regions = []
        client_account_write_regions = []
        if self.__global_endpoint_manager and hasattr(self.__global_endpoint_manager, 'client'):
            gem_client = self.__global_endpoint_manager.client
            if gem_client and gem_client.connection_policy:
                connection_policy = gem_client.connection_policy
                client_preferred_regions = connection_policy.PreferredLocations
                client_excluded_regions = connection_policy.ExcludedLocations

            if self.__global_endpoint_manager.location_cache:
                location_cache: LocationCache = self.__global_endpoint_manager.location_cache
                client_account_read_regions = location_cache.account_read_locations
                client_account_write_regions = location_cache.account_write_locations

        return {"Preferred Regions": client_preferred_regions,
                "Excluded Regions": client_excluded_regions,
                "Account Read Regions": client_account_read_regions,
                "Account Write Regions": client_account_write_regions}

    def __get_database_account_settings(self) -> Optional[DatabaseAccount]:
        if self.__global_endpoint_manager and hasattr(self.__global_endpoint_manager, '_database_account_cache'):
            return self.__global_endpoint_manager._database_account_cache  # pylint: disable=protected-access
        return None

    def _log_client_settings(self) -> str:
        logger_str = "\nClient Settings: \n"
        client_settings = self.__get_client_settings()
        if client_settings and isinstance(client_settings, dict):
            logger_str += ''.join([f"\t{k}: {v}\n" for k, v in client_settings.items()])
        return logger_str

    # pylint: disable=protected-access
    def _log_database_account_settings(self) -> str:
        logger_str = "\nDatabase Account Settings: \n"
        self.__database_account_settings = self.__get_database_account_settings()
        if self.__database_account_settings and self.__database_account_settings.ConsistencyPolicy:
            logger_str += f"\tConsistency Level: {self.__database_account_settings.ConsistencyPolicy.get('defaultConsistencyLevel')}\n"  # pylint: disable=line-too-long
            logger_str += f"\tWritable Locations: {self.__database_account_settings.WritableLocations}\n"
            logger_str += f"\tReadable Locations: {self.__database_account_settings.ReadableLocations}\n"
            logger_str += f"\tMulti-Region Writes: {self.__database_account_settings._EnableMultipleWritableLocations}\n"  # pylint: disable=protected-access, line-too-long

        return logger_str
