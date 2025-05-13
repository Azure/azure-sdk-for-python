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

"""AioHttpTransport allowing injection of faults between SDK and Cosmos Gateway
"""

import asyncio
import json
import logging
import sys
from typing import Callable, Optional, Any, Dict, List, Awaitable, MutableMapping
import aiohttp
from azure.core.pipeline.transport import AioHttpTransport, AioHttpTransportResponse
from azure.core.rest import HttpRequest, AsyncHttpResponse
from azure.cosmos import documents

import test_config
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.core.exceptions import ServiceRequestError, ServiceResponseError

from azure.cosmos.http_constants import ResourceType, HttpHeaders

class FaultInjectionTransportAsync(AioHttpTransport):
    logger = logging.getLogger('azure.cosmos.fault_injection_transport_async')
    logger.setLevel(logging.DEBUG)

    def __init__(self, *, session: Optional[aiohttp.ClientSession] = None, loop=None, session_owner: bool = True, **config):
        self.faults: List[Dict[str, Any]] = []
        self.requestTransformations: List[Dict[str, Any]]  = []
        self.responseTransformations: List[Dict[str, Any]] = []
        super().__init__(session=session, loop=loop, session_owner=session_owner, **config)

    def add_fault(self, predicate: Callable[[HttpRequest], bool], fault_factory: Callable[[HttpRequest], Awaitable[Exception]]):
        self.faults.append({"predicate": predicate, "apply": fault_factory})

    def add_response_transformation(self, predicate: Callable[[HttpRequest], bool], response_transformation: Callable[[HttpRequest, Callable[[HttpRequest], AioHttpTransportResponse]], AioHttpTransportResponse]):
        self.responseTransformations.append({
            "predicate": predicate, 
            "apply": response_transformation})

    @staticmethod
    def __first_item(iterable, condition=lambda x: True):
        """
        Returns the first item in the `iterable` that satisfies the `condition`.
        
        If no item satisfies the condition, it returns None.
        """
        return next((x for x in iterable if condition(x)), None)

    async def send(self, request: HttpRequest, *, stream: bool = False, proxies: Optional[MutableMapping[str, str]] = None, **config) -> AsyncHttpResponse:
        FaultInjectionTransportAsync.logger.info("--> FaultInjectionTransportAsync.Send {} {}".format(request.method, request.url))
        # find the first fault Factory with matching predicate if any
        first_fault_factory = FaultInjectionTransportAsync.__first_item(iter(self.faults), lambda f: f["predicate"](request))
        if first_fault_factory:
            FaultInjectionTransportAsync.logger.info("--> FaultInjectionTransportAsync.ApplyFaultInjection")
            injected_error = await first_fault_factory["apply"](request)
            FaultInjectionTransportAsync.logger.info("Found to-be-injected error {}".format(injected_error))
            raise injected_error

        # apply the chain of request transformations with matching predicates if any
        matching_request_transformations = filter(lambda f: f["predicate"](f["predicate"]), iter(self.requestTransformations))
        for currentTransformation in matching_request_transformations:
            FaultInjectionTransportAsync.logger.info("--> FaultInjectionTransportAsync.ApplyRequestTransformation")
            request = await currentTransformation["apply"](request)

        first_response_transformation = FaultInjectionTransportAsync.__first_item(iter(self.responseTransformations), lambda f: f["predicate"](request))

        FaultInjectionTransportAsync.logger.info("--> FaultInjectionTransportAsync.BeforeGetResponseTask")
        get_response_task =  asyncio.create_task(super().send(request, stream=stream, proxies=proxies, **config))
        FaultInjectionTransportAsync.logger.info("<-- FaultInjectionTransportAsync.AfterGetResponseTask")

        if first_response_transformation:
            FaultInjectionTransportAsync.logger.info(f"Invoking response transformation")
            response = await first_response_transformation["apply"](request, lambda: get_response_task)
            response.headers["_request"] = request
            FaultInjectionTransportAsync.logger.info(f"Received response transformation result with status code {response.status_code}")
            return response
        else:
            FaultInjectionTransportAsync.logger.info(f"Sending request to {request.url}")
            response = await get_response_task
            response.headers["_request"] = request
            FaultInjectionTransportAsync.logger.info(f"Received response with status code {response.status_code}")
            return response

    @staticmethod
    def predicate_url_contains_id(r: HttpRequest, id_value: str) -> bool:
        return id_value in r.url

    @staticmethod
    def predicate_targets_region(r: HttpRequest, region_endpoint: str) -> bool:
        return r.url.startswith(region_endpoint)

    @staticmethod
    def print_call_stack():
        print("Call stack:")
        frame = sys._getframe()
        while frame:
            print(f"File: {frame.f_code.co_filename}, Line: {frame.f_lineno}, Function: {frame.f_code.co_name}")
            frame = frame.f_back

    @staticmethod
    def predicate_req_payload_contains_id(r: HttpRequest, id_value: str):
        if r.body is None:
            return False

        return '"id":"{}"'.format(id_value) in r.body

    @staticmethod
    def predicate_req_for_document_with_id(r: HttpRequest, id_value: str) -> bool:
        return (FaultInjectionTransportAsync.predicate_url_contains_id(r, id_value)
                or FaultInjectionTransportAsync.predicate_req_payload_contains_id(r, id_value))

    @staticmethod
    def predicate_is_database_account_call(r: HttpRequest) -> bool:
        is_db_account_read = (r.headers.get(HttpHeaders.ThinClientProxyResourceType) == ResourceType.DatabaseAccount
                and r.headers.get(HttpHeaders.ThinClientProxyOperationType) == documents._OperationType.Read)

        return is_db_account_read

    @staticmethod
    def predicate_is_document_operation(r: HttpRequest) -> bool:
        is_document_operation = (r.headers.get(HttpHeaders.ThinClientProxyResourceType) ==
                                 ResourceType.Document)

        return is_document_operation

    @staticmethod
    def predicate_is_operation_type(r: HttpRequest, operation_type: str) -> bool:
        is_operation_type = r.headers.get(HttpHeaders.ThinClientProxyOperationType) == operation_type
        return is_operation_type

    @staticmethod
    def predicate_is_write_operation(r: HttpRequest, uri_prefix: str) -> bool:
        is_write_document_operation = documents._OperationType.IsWriteOperation(
            str(r.headers.get('x-ms-thinclient-proxy-operation-type')))

        return is_write_document_operation and uri_prefix in r.url

    @staticmethod
    async def error_after_delay(delay_in_ms: int, error: Exception) -> Exception:
        await asyncio.sleep(delay_in_ms / 1000.0)
        return error

    @staticmethod
    async def error_write_forbidden() -> Exception:
        return CosmosHttpResponseError(
            status_code=403,
            message="Injected error disallowing writes in this region.",
            response=None,
            sub_status_code=3,
        )

    @staticmethod
    async def error_region_down() -> Exception:
        return ServiceRequestError(
            message="Injected region down.",
        )

    @staticmethod
    async def error_service_response() -> Exception:
        return ServiceResponseError(
            message="Injected Service Response Error.",
        )

    @staticmethod
    async def transform_topology_swr_mrr(
            write_region_name: str,
            read_region_name: str,
            inner: Callable[[], Awaitable[AioHttpTransportResponse]]) -> AioHttpTransportResponse:

        response = await inner()
        if not FaultInjectionTransportAsync.predicate_is_database_account_call(response.request):
            return response

        data = response.body()
        if response.status_code == 200 and data:
            data = data.decode("utf-8")
            result = json.loads(data)
            readable_locations = result["readableLocations"]
            writable_locations = result["writableLocations"]
            readable_locations[0]["name"] = write_region_name
            writable_locations[0]["name"] = write_region_name
            readable_locations.append({"name": read_region_name, "databaseAccountEndpoint" : test_config.TestConfig.local_host})
            FaultInjectionTransportAsync.logger.info("Transformed Account Topology: {}".format(result))
            request: HttpRequest = response.request
            return FaultInjectionTransportAsync.MockHttpResponse(request, 200, result)

        return response

    @staticmethod
    async def transform_topology_mwr(
            first_region_name: str,
            second_region_name: str,
            inner: Callable[[], Awaitable[AioHttpTransportResponse]],
            first_region_url: str = None,
            second_region_url: str = test_config.TestConfig.local_host
    ) -> AioHttpTransportResponse:

        response = await inner()
        if not FaultInjectionTransportAsync.predicate_is_database_account_call(response.request):
            return response

        data = response.body()
        if response.status_code == 200 and data:
            data = data.decode("utf-8")
            result = json.loads(data)
            readable_locations = result["readableLocations"]
            writable_locations = result["writableLocations"]

            if first_region_url is None:
                first_region_url = readable_locations[0]["databaseAccountEndpoint"]
            readable_locations[0] = \
                {"name": first_region_name, "databaseAccountEndpoint": first_region_url}
            writable_locations[0] = \
                {"name": first_region_name, "databaseAccountEndpoint": first_region_url}
            readable_locations.append(
                {"name": second_region_name, "databaseAccountEndpoint": second_region_url})
            writable_locations.append(
                {"name": second_region_name, "databaseAccountEndpoint": second_region_url})
            result["enableMultipleWriteLocations"] = True
            FaultInjectionTransportAsync.logger.info("Transformed Account Topology: {}".format(result))
            request: HttpRequest = response.request
            return FaultInjectionTransportAsync.MockHttpResponse(request, 200, result)

        return response

    class MockHttpResponse(AioHttpTransportResponse):
        def __init__(self, request: HttpRequest, status_code: int, content:Optional[Dict[str, Any]]):
            self.request: HttpRequest = request
            # This is actually never None, and set by all implementations after the call to
            # __init__ of this class. This class is also a legacy impl, so it's risky to change it
            # for low benefits The new "rest" implementation does define correctly status_code
            # as non-optional.
            self.status_code: int = status_code
            self.headers: MutableMapping[str, str] = {}
            self.reason: Optional[str] = None
            self.content_type: Optional[str] = None
            self.block_size: int = 4096  # Default to same as R
            self.content: Optional[Dict[str, Any]] = None
            self.json_text: Optional[str] = None
            self.bytes: Optional[bytes] = None
            if content:
                self.content = content
                self.json_text = json.dumps(content)
                self.bytes = self.json_text.encode("utf-8")


        def body(self) -> Optional[bytes]:
            return self.bytes

        def text(self) -> Optional[str]:
            return self.json_text

        async def load_body(self) -> None:
            return
