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
from typing import Optional, Union, Dict, Any, TYPE_CHECKING, Callable, Mapping
import types

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import HttpLoggingPolicy

from .http_constants import HttpHeaders
from ._global_endpoint_manager import _GlobalEndpointManager
from .documents import DatabaseAccount

if TYPE_CHECKING:
    from azure.core.rest import HttpRequest, HttpResponse, AsyncHttpResponse
    from azure.core.pipeline.transport import (  # pylint: disable=no-legacy-azure-core-http-response-import
        HttpRequest as LegacyHttpRequest,
        HttpResponse as LegacyHttpResponse,
        AsyncHttpResponse as LegacyAsyncHttpResponse
    )


HTTPRequestType = Union["LegacyHttpRequest", "HttpRequest"]
HTTPResponseType = Union["LegacyHttpResponse", "HttpResponse", "LegacyAsyncHttpResponse", "AsyncHttpResponse"]


def _format_error(payload: str) -> str:
    output = json.loads(payload)
    return output['message'].replace("\r", " ")


class CosmosHttpLoggingPolicy(HttpLoggingPolicy):

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        global_endpoint_manager: Optional[_GlobalEndpointManager] = None,
        database_account: Optional[DatabaseAccount] = None,
        *,
        enable_diagnostics_logging: bool = False,
        diagnostics_handler: Optional[Union[Callable, Mapping]] = None,
        **kwargs
    ):
        self._enable_diagnostics_logging = enable_diagnostics_logging
        self.diagnostics_handler = diagnostics_handler
        self.__request_already_logged = False
        if self.diagnostics_handler and callable(self.diagnostics_handler):
            if hasattr(self.diagnostics_handler, '__get__'):
                self._should_log = types.MethodType(diagnostics_handler, self)  # type: ignore
            else:
                self._should_log = self.diagnostics_handler  # type: ignore
        elif isinstance(self.diagnostics_handler, Mapping):
            self._should_log = self._dict_should_log  # type: ignore
        else:
            self._should_log = self._default_should_log  # type: ignore
        self.__global_endpoint_manager = global_endpoint_manager
        self.__client_settings = self.__get_client_settings()
        self.__database_account_settings: Optional[DatabaseAccount] = (database_account or
                                                                       self.__get_database_account_settings())
        self._resource_map = {
            'docs': 'document',
            'colls': 'container',
            'dbs': 'database'
        }
        super().__init__(logger, **kwargs)
        if self._enable_diagnostics_logging:
            cosmos_disallow_list = ["Authorization", "ProxyAuthorization"]
            cosmos_allow_list = [
                v for k, v in HttpHeaders.__dict__.items() if not k.startswith("_") and k not in cosmos_disallow_list
            ]
            self.allowed_header_names = set(cosmos_allow_list)

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        verb = request.http_request.method
        if self._enable_diagnostics_logging:
            request.context["start_time"] = time.time()
            url = None
            if self.diagnostics_handler:
                url = request.http_request.url
            database_name = None
            collection_name = None
            resource_type = None
            if url:
                url_parts = url.split('/')
                if 'dbs' in url_parts:
                    dbs_index = url_parts.index('dbs')
                    if dbs_index + 1 < len(url_parts):
                        database_name = url_parts[url_parts.index('dbs') + 1]
                    resource_type = self._resource_map['dbs']
                if 'colls' in url_parts:
                    colls_index = url_parts.index('colls')
                    if colls_index + 1 < len(url_parts):
                        collection_name = url_parts[url_parts.index('colls') + 1]
                    resource_type = self._resource_map['colls']
                if 'docs' in url_parts:
                    resource_type = self._resource_map['docs']
            if self._should_log(verb=verb,database_name=database_name,collection_name=collection_name,
                                resource_type=resource_type, is_request=True):
                self._log_client_settings()
                self._log_database_account_settings()
                super().on_request(request)
                self.__request_already_logged = True

    # pylint: disable=too-many-statements
    def on_response(
        self,
        request: PipelineRequest[HTTPRequestType],
        response: PipelineResponse[HTTPRequestType, HTTPResponseType],  # type: ignore[override]
    ) -> None:
        duration = time.time() - request.context["start_time"] if "start_time" in request.context else None
        status_code = response.http_response.status_code
        sub_status_str = response.http_response.headers.get("x-ms-substatus")
        sub_status_code = int(sub_status_str) if sub_status_str else None
        verb = request.http_request.method
        http_version_obj = None
        url = None
        if self.diagnostics_handler:
            try:
                major = response.http_response.internal_response.version.major  # type: ignore[attr-defined, union-attr]
                minor = response.http_response.internal_response.version.minor  # type: ignore[attr-defined, union-attr]
                http_version_obj = f"{major}."
                http_version_obj += f"{minor}"
            except (AttributeError, TypeError):
                http_version_obj = None
            try:
                url = response.http_response.internal_response.url.geturl()  # type: ignore[attr-defined, union-attr]
            except AttributeError:
                url = str(response.http_response.internal_response.url)  # type: ignore[attr-defined, union-attr]
        database_name = None
        collection_name = None
        resource_type = None
        if url:
            url_parts = url.split('/')
            if 'dbs' in url_parts:
                dbs_index = url_parts.index('dbs')
                if dbs_index + 1 < len(url_parts):
                    database_name = url_parts[url_parts.index('dbs') + 1]
                resource_type = self._resource_map['dbs']
            if 'colls' in url_parts:
                colls_index = url_parts.index('colls')
                if colls_index + 1 < len(url_parts):
                    collection_name = url_parts[url_parts.index('colls') + 1]
                resource_type = self._resource_map['colls']
            if 'docs' in url_parts:
                resource_type = self._resource_map['docs']


        if self._should_log(duration=duration, status_code=status_code, sub_status_code=sub_status_code,
                            verb=verb, http_version=http_version_obj, database_name=database_name,
                            collection_name=collection_name, resource_type=resource_type, is_request=False):
            if not self.__request_already_logged:
                self._log_client_settings()
                self._log_database_account_settings()
                super().on_request(request)
            else:
                self.__request_already_logged = False
            super().on_response(request, response)
            if self._enable_diagnostics_logging:
                http_response = response.http_response
                options = response.context.options
                logger = request.context.setdefault("logger", options.pop("logger", self.logger))
                try:
                    if "start_time" in request.context:
                        logger.info("Elapsed time in seconds: {}".format(duration))
                    else:
                        logger.info("Elapsed time in seconds: unknown")
                    if http_response.status_code >= 400:
                        logger.info("Response error message: %r", _format_error(http_response.text()))
                except Exception as err:  # pylint: disable=broad-except
                    logger.warning("Failed to log request: %s", repr(err)) # pylint: disable=do-not-log-exceptions

    # pylint: disable=unused-argument
    def _default_should_log(
            self,
            **kwargs
    ) -> bool:
        return True

    def _dict_should_log(self, **kwargs) -> bool:
        params = {
            'duration': kwargs.get('duration', None),
            'status code': kwargs.get('status_code', None),
            'verb': kwargs.get('verb', None),
            'http version': kwargs.get('http_version', None),
            'database name': kwargs.get('database_name', None),
            'collection name': kwargs.get('collection_name', None),
            'resource type': kwargs.get('resource_type', None)
        }
        for key, param in params.items():
            if (param and isinstance(self.diagnostics_handler, Mapping) and key in self.diagnostics_handler
                    and self.diagnostics_handler[key] is not None):
                if self.diagnostics_handler[key](param):
                    return True
        return False

    def __get_client_settings(self) -> Optional[Dict[str, Any]]:
        # Place any client settings we want to log here
        if self.__global_endpoint_manager:
            if hasattr(self.__global_endpoint_manager, 'PreferredLocations'):
                return {"Client Preferred Regions": self.__global_endpoint_manager.PreferredLocations}
            return {"Client Preferred Regions": []}
        return None

    def __get_database_account_settings(self) -> Optional[DatabaseAccount]:
        if self.__global_endpoint_manager and hasattr(self.__global_endpoint_manager, '_database_account_cache'):
            return self.__global_endpoint_manager._database_account_cache  # pylint: disable=protected-access
        return None

    def _log_client_settings(self) -> None:
        self.logger.info("Client Settings:", exc_info=False)
        if self.__client_settings and isinstance(self.__client_settings, dict):
            self.logger.info("\tClient Preferred Regions: %s", self.__client_settings["Client Preferred Regions"],
                             exc_info=False)

    # pylint: disable=protected-access
    def _log_database_account_settings(self) -> None:
        self.logger.info("Database Account Settings:", exc_info=False)
        self.__database_account_settings = self.__get_database_account_settings()
        if self.__database_account_settings and self.__database_account_settings.ConsistencyPolicy:
            self.logger.info("\tConsistency Level: %s",
                             self.__database_account_settings.ConsistencyPolicy.get("defaultConsistencyLevel"),
                             exc_info=False)
            self.logger.info("\tWritable Locations: %s", self.__database_account_settings.WritableLocations,
                             exc_info=False)
            self.logger.info("\tReadable Locations: %s", self.__database_account_settings.ReadableLocations,
                             exc_info=False)
            self.logger.info("\tMulti-Region Writes: %s",
                             self.__database_account_settings._EnableMultipleWritableLocations, exc_info=False)
