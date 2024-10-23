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
from typing import Optional, Union, Dict, Any, TYPE_CHECKING, Callable
import os
import platform


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
        diagnostics_handler: Optional[Union[Callable, dict]] = None,
        **kwargs
    ):
        self._enable_diagnostics_logging = enable_diagnostics_logging
        self.diagnostics_handler = diagnostics_handler
        if callable(self.diagnostics_handler):
            self.should_log = self.diagnostics_handler
        self.__global_endpoint_manager = global_endpoint_manager
        self.__client_settings = self.__get_client_settings()
        if database_account:
            self.__database_account_settings = database_account
        else:
            self.__database_account_settings = self.__get_database_account_settings()
        super().__init__(logger, **kwargs)
        if self._enable_diagnostics_logging:
            cosmos_disallow_list = ["Authorization", "ProxyAuthorization"]
            cosmos_allow_list = [
                v for k, v in HttpHeaders.__dict__.items() if not k.startswith("_") and k not in cosmos_disallow_list
            ]
            self.allowed_header_names = set(cosmos_allow_list)

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        verb = request.http_request.method
        if self.should_log(verb=verb, isRequest=True):
            if self._enable_diagnostics_logging:
                request.context["start_time"] = time.time()
                # We will only log settings once upon initializing.
                self._log_client_settings()
                self._log_database_account_settings()
                super().on_request(request)

    def on_response(
        self,
        request: PipelineRequest[HTTPRequestType],
        response: PipelineResponse[HTTPRequestType, HTTPResponseType],  # type: ignore[override]
    ) -> None:
        duration = time.time() - request.context["start_time"] if "start_time" in request.context else None
        status_code = response.http_response.status_code
        sub_status_code = None
        verb = request.http_request.method
        resource_type = None
        if self.should_log(duration, status_code, sub_status_code, verb, resource_type, isRequest=False):
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
                    logger.warning("Failed to log request: %s", repr(err))


    def should_log(
            self,
            duration: Optional[int] = None,
            status_code: Optional[int] = None,
            sub_status_code: Optional[int] = None,
            verb: Optional[str] = None,
            resource_type: Optional[str] = None,
            is_request: bool = False
    ) -> bool:
        return True

    def dict_should_log(self, duration: Optional[int] = None,
            status_code: Optional[int] = None,
            sub_status_code: Optional[int] = None,
            verb: Optional[str] = None,
            resource_type: Optional[str] = None,
            is_request: bool = False) -> bool:
        params = {
            'duration': duration,
            'status code': status_code,
            'sub status code': sub_status_code,
            'verb': verb,
            'resource type': resource_type
        }
        for key, param in params.items():
            if param is not None and self.diagnostics_handler[key] is not None:
                if self.diagnostics_handler[key](param):
                    return True
        return False

    def __get_client_settings(self) -> Optional[Dict[str, Any]]:
        # Place any client settings we want to log here
        return {"Client Preferred Regions": self.__global_endpoint_manager.PreferredLocations}

    def __get_database_account_settings(self) -> Optional[DatabaseAccount]:
        # if self.__global_endpoint_manager._database_account_cache:
        return self.__global_endpoint_manager._database_account_cache
        # return self.__global_endpoint_manager._GetDatabaseAccount()

    def _log_client_settings(self)-> None:
        self.logger.info("Client Settings:", exc_info=False)
        self.logger.info("\tClient Preferred Regions: {}".format(self.__client_settings["Client Preferred Regions"])
                         , exc_info=False) # connection retry policy stuff values that configure timeouts etc

    def _log_database_account_settings(self)-> None:
        self.logger.info("Database Account Settings:", exc_info=False)
        self.__database_account_settings = self.__get_database_account_settings()
        if self.__database_account_settings:
            self.logger.info("\tConsistency Level: {}".format(self.__database_account_settings.
                                                              ConsistencyPolicy.get("defaultConsistencyLevel"))
                             , exc_info=False)
            self.logger.info("\tWritable Locations: {}".format(self.__database_account_settings.WritableLocations)
                             , exc_info=False)
            self.logger.info("\tReadable Locations: {}".format(self.__database_account_settings.ReadableLocations)
                             , exc_info=False)
            self.logger.info("\tMulti-Region Writes: {}".format(self.__database_account_settings.
                                                                _EnableMultipleWritableLocations), exc_info=False)


    def __get_system_info(self):
        try:
            system = platform.system()

            if system == "Windows":
                # Get CPU info

                cpu_info = os.popen("wmic cpu get loadpercentage").read().strip().split("\n")[2]

                # Get memory info
                memory_info = os.popen(
                    "wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Value").read().strip().split("\n")
                free_memory = int(memory_info[0].split("=")[1])
                total_memory = int(memory_info[2].split("=")[1])
                used_memory = total_memory - free_memory

                return {
                    "CPU Load (%)": cpu_info,
                    "Total Memory (KB)": total_memory,
                    "Used Memory (KB)": used_memory,
                    "Free Memory (KB)": free_memory
                }

            elif system == "Linux":
                # Get CPU info
                cpu_info = os.popen("top -bn1 | grep 'Cpu(s)'").read().strip().split()[1]

                # Get memory info
                memory_info = os.popen("free -k").read().strip().split("\n")[1].split()
                total_memory = int(memory_info[1])
                used_memory = int(memory_info[2])
                free_memory = int(memory_info[3])

                return {
                    "CPU Load (%)": cpu_info,
                    "Total Memory (KB)": total_memory,
                    "Used Memory (KB)": used_memory,
                    "Free Memory (KB)": free_memory
                }

            elif system == "Darwin":  # macOS
                # Get CPU info
                cpu_info = os.popen("ps -A -o %cpu | awk '{s+=$1} END {print s}'").read().strip()

                # Get memory info
                memory_info = os.popen("vm_stat | grep 'Pages free'").read().strip().split(":")[1].strip().split()[0]
                page_size = int(os.popen("vm_stat | grep 'page size of'").read().strip().split()[3])
                free_memory = int(memory_info) * page_size // 1024
                total_memory = int(os.popen("sysctl -n hw.memsize").read().strip()) // 1024
                used_memory = total_memory - free_memory

                return {
                    "CPU Load (%)": cpu_info,
                    "Total Memory (KB)": total_memory,
                    "Used Memory (KB)": used_memory,
                    "Free Memory (KB)": free_memory
                }

            else:
                return {}

        except Exception as e:
            return {}
