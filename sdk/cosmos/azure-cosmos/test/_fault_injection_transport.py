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
from collections.abc import MutableMapping
from typing import Callable, Optional

import aiohttp
from azure.core.pipeline.transport import AioHttpTransport, AioHttpTransportResponse
from azure.core.rest import HttpRequest, AsyncHttpResponse

import test_config
from azure.cosmos.exceptions import CosmosHttpResponseError


class FaultInjectionTransport(AioHttpTransport):
    logger = logging.getLogger('azure.cosmos.fault_injection_transport')
    logger.setLevel(logging.DEBUG)

    def __init__(self, *, session: aiohttp.ClientSession | None = None, loop=None, session_owner: bool = True, **config):
        self.faults = []
        self.requestTransformations = []
        self.responseTransformations = []
        super().__init__(session=session, loop=loop, session_owner=session_owner, **config)

    def add_fault(self, predicate: Callable[[HttpRequest], bool], fault_factory: Callable[[HttpRequest], asyncio.Task[Exception]]):
        self.faults.append({"predicate": predicate, "apply": fault_factory})

    def add_response_transformation(self, predicate: Callable[[HttpRequest], bool], response_transformation: Callable[[HttpRequest, Callable[[HttpRequest], asyncio.Task[AsyncHttpResponse]]], asyncio.Task[AsyncHttpResponse]]):
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

    async def send(self, request: HttpRequest, *, stream: bool = False, proxies: MutableMapping[str, str] | None = None, **config) -> AsyncHttpResponse:
        FaultInjectionTransport.logger.info("--> FaultInjectionTransport.Send {} {}".format(request.method, request.url))
        # find the first fault Factory with matching predicate if any
        first_fault_factory = FaultInjectionTransport.__first_item(iter(self.faults), lambda f: f["predicate"](request))
        if first_fault_factory:
            FaultInjectionTransport.logger.info("--> FaultInjectionTransport.ApplyFaultInjection")
            injected_error = await first_fault_factory["apply"](request)
            FaultInjectionTransport.logger.info("Found to-be-injected error {}".format(injected_error))
            raise injected_error

        # apply the chain of request transformations with matching predicates if any
        matching_request_transformations = filter(lambda f: f["predicate"](f["predicate"]), iter(self.requestTransformations))
        for currentTransformation in matching_request_transformations:
            FaultInjectionTransport.logger.info("--> FaultInjectionTransport.ApplyRequestTransformation")
            request = await currentTransformation["apply"](request)

        first_response_transformation = FaultInjectionTransport.__first_item(iter(self.responseTransformations), lambda f: f["predicate"](request))

        FaultInjectionTransport.logger.info("--> FaultInjectionTransport.BeforeGetResponseTask")
        get_response_task =  asyncio.create_task(super().send(request, stream=stream, proxies=proxies, **config))
        FaultInjectionTransport.logger.info("<-- FaultInjectionTransport.AfterGetResponseTask")

        if first_response_transformation:
            FaultInjectionTransport.logger.info(f"Invoking response transformation")
            response = await first_response_transformation["apply"](request, lambda: get_response_task)
            response.headers["_request"] = request
            FaultInjectionTransport.logger.info(f"Received response transformation result with status code {response.status_code}")
            return response
        else:
            FaultInjectionTransport.logger.info(f"Sending request to {request.url}")
            response = await get_response_task
            response.headers["_request"] = request
            FaultInjectionTransport.logger.info(f"Received response with status code {response.status_code}")
            return response

    @staticmethod
    def predicate_url_contains_id(r: HttpRequest, id_value: str) -> bool:
        return id_value in r.url

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
        return (FaultInjectionTransport.predicate_url_contains_id(r, id_value)
                or FaultInjectionTransport.predicate_req_payload_contains_id(r, id_value))

    @staticmethod
    def predicate_is_database_account_call(r: HttpRequest) -> bool:
        is_db_account_read = (r.headers.get('x-ms-thinclient-proxy-resource-type') == 'databaseaccount'
                and r.headers.get('x-ms-thinclient-proxy-operation-type') == 'Read')

        return is_db_account_read

    @staticmethod
    def predicate_is_write_operation(r: HttpRequest, uri_prefix: str) -> bool:
        is_write_document_operation = (r.headers.get('x-ms-thinclient-proxy-resource-type') == 'docs'
                and r.headers.get('x-ms-thinclient-proxy-operation-type') != 'Read'
                and r.headers.get('x-ms-thinclient-proxy-operation-type') != 'ReadFeed'
                and r.headers.get('x-ms-thinclient-proxy-operation-type') != 'Query')

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
    async def transform_topology_swr_mrr(
            write_region_name: str,
            read_region_name: str,
            r: HttpRequest,
            inner: Callable[[],asyncio.Task[AsyncHttpResponse]]) -> asyncio.Task[AsyncHttpResponse]:

        response = await inner()
        if not FaultInjectionTransport.predicate_is_database_account_call(response.request):
            return response

        await response.load_body()
        data = response.body()
        if response.status_code == 200 and data:
            data = data.decode("utf-8")
            result = json.loads(data)
            readable_locations = result["readableLocations"]
            writable_locations = result["writableLocations"]
            readable_locations[0]["name"] = write_region_name
            writable_locations[0]["name"] = write_region_name
            readable_locations.append({"name": read_region_name, "databaseAccountEndpoint" : test_config.TestConfig.local_host})
            FaultInjectionTransport.logger.info("Transformed Account Topology: {}".format(result))
            request: HttpRequest = response.request
            return FaultInjectionTransport.MockHttpResponse(request, 200, result)

        return response

    @staticmethod
    async def transform_topology_mwr(
            first_region_name: str,
            second_region_name: str,
            r: HttpRequest,
            inner: Callable[[], asyncio.Task[AsyncHttpResponse]]) -> asyncio.Task[AsyncHttpResponse]:

        response = await inner()
        if not FaultInjectionTransport.predicate_is_database_account_call(response.request):
            return response

        await response.load_body()
        data = response.body()
        if response.status_code == 200 and data:
            data = data.decode("utf-8")
            result = json.loads(data)
            readable_locations = result["readableLocations"]
            writable_locations = result["writableLocations"]
            readable_locations[0]["name"] = first_region_name
            writable_locations[0]["name"] = first_region_name
            readable_locations.append(
                {"name": second_region_name, "databaseAccountEndpoint": test_config.TestConfig.local_host})
            writable_locations.append(
                {"name": second_region_name, "databaseAccountEndpoint": test_config.TestConfig.local_host})
            result["enableMultipleWriteLocations"] = True
            FaultInjectionTransport.logger.info("Transformed Account Topology: {}".format(result))
            request: HttpRequest = response.request
            return FaultInjectionTransport.MockHttpResponse(request, 200, result)

        return response

    class MockHttpResponse(AioHttpTransportResponse):
        def __init__(self, request: HttpRequest, status_code: int, content:Optional[dict[str, any]]):
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
            self.content: Optional[dict[str, any]] = None
            self.json_text: Optional[str] = None
            self.bytes: Optional[bytes] = None
            if content:
                self.content:Optional[dict[str, any]] = content
                self.json_text:Optional[str] = json.dumps(content)
                self.bytes:bytes = self.json_text.encode("utf-8")


        def body(self) -> bytes:
            return self.bytes

        def text(self, encoding: Optional[str] = None) -> str:
            return self.json_text

        async def load_body(self) -> None:
            return