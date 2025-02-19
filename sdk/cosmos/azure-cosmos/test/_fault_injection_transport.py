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
from typing import Callable

import aiohttp
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.rest import HttpRequest, AsyncHttpResponse

from azure.cosmos.exceptions import CosmosHttpResponseError


class FaultInjectionTransport(AioHttpTransport):
    logger = logging.getLogger('azure.cosmos.fault_injection_transport')
    logger.setLevel(logging.DEBUG)

    def __init__(self, *, session: aiohttp.ClientSession | None = None, loop=None, session_owner: bool = True, **config):
        self.faults = []
        self.requestTransformations = []
        self.responseTransformations = []
        super().__init__(session=session, loop=loop, session_owner=session_owner, **config)

    def addFault(self, predicate: Callable[[HttpRequest], bool], faultFactory: Callable[[HttpRequest], asyncio.Task[Exception]]):
        self.faults.append({"predicate": predicate, "apply": faultFactory})

    def addRequestTransformation(self, predicate: Callable[[HttpRequest], bool], requestTransformation: Callable[[HttpRequest], asyncio.Task[HttpRequest]]):
        self.requestTransformations.append({"predicate": predicate, "apply": requestTransformation})

    def add_response_transformation(self, predicate: Callable[[HttpRequest], bool], responseTransformation: Callable[[HttpRequest, Callable[[HttpRequest], asyncio.Task[AsyncHttpResponse]]], asyncio.Task[AsyncHttpResponse]]):
        self.responseTransformations.append({
            "predicate": predicate, 
            "apply": responseTransformation})    

    def firstItem(self, iterable, condition=lambda x: True):
        """
        Returns the first item in the `iterable` that satisfies the `condition`.
        
        If no item satisfies the condition, it returns None.
        """
        return next((x for x in iterable if condition(x)), None)

    async def send(self, request: HttpRequest, *, stream: bool = False, proxies: MutableMapping[str, str] | None = None, **config) -> AsyncHttpResponse:
        FaultInjectionTransport.logger.info("--> FaultInjectionTransport.Send {} {}".format(request.method, request.url))
        # find the first fault Factory with matching predicate if any
        firstFaultFactory = self.firstItem(iter(self.faults), lambda f: f["predicate"](request))
        if (firstFaultFactory != None):
            FaultInjectionTransport.logger.info("--> FaultInjectionTransport.ApplyFaultInjection")
            injectedError = await firstFaultFactory["apply"]()
            FaultInjectionTransport.logger.info("Found to-be-injected error {}".format(injectedError))
            raise injectedError

        # apply the chain of request transformations with matching predicates if any
        matchingRequestTransformations = filter(lambda f: f["predicate"](f["predicate"]), iter(self.requestTransformations))
        for currentTransformation in matchingRequestTransformations:
            FaultInjectionTransport.logger.info("--> FaultInjectionTransport.ApplyRequestTransformation")
            request = await currentTransformation["apply"](request)

        firstResponseTransformation = self.firstItem(iter(self.responseTransformations), lambda f: f["predicate"](request))

        FaultInjectionTransport.logger.info("--> FaultInjectionTransport.BeforeGetResponseTask")
        getResponseTask =  asyncio.create_task(super().send(request, stream=stream, proxies=proxies, **config))
        FaultInjectionTransport.logger.info("<-- FaultInjectionTransport.AfterGetResponseTask")

        if (firstResponseTransformation != None):
            FaultInjectionTransport.logger.info(f"Invoking response transformation")
            response = await firstResponseTransformation["apply"](request, lambda: getResponseTask)
            FaultInjectionTransport.logger.info(f"Received response transformation result with status code {response.status_code}")
            return response
        else:
            FaultInjectionTransport.logger.info(f"Sending request to {request.url}")
            response = await getResponseTask
            FaultInjectionTransport.logger.info(f"Received response with status code {response.status_code}")
            return response

    @staticmethod
    def predicate_url_contains_id(r: HttpRequest, id: str) -> bool:
        return id in r.url

    @staticmethod
    def print_call_stack():
        print("Call stack:")
        frame = sys._getframe()
        while frame:
            print(f"File: {frame.f_code.co_filename}, Line: {frame.f_lineno}, Function: {frame.f_code.co_name}")
            frame = frame.f_back

    @staticmethod
    def predicate_req_payload_contains_id(r: HttpRequest, id: str):
        if r.body is None:
            return False

        return '"id":"{}"'.format(id) in r.body

    @staticmethod
    def predicate_req_for_document_with_id(r: HttpRequest, id: str) -> bool:
        return (FaultInjectionTransport.predicate_url_contains_id(r, id)
                or FaultInjectionTransport.predicate_req_payload_contains_id(r, id))

    @staticmethod
    def predicate_is_database_account_call(r: HttpRequest) -> bool:
        isDbAccountRead = (r.headers.get('x-ms-thinclient-proxy-resource-type') == 'databaseaccount'
                and r.headers.get('x-ms-thinclient-proxy-operation-type') == 'Read')

        return isDbAccountRead

    @staticmethod
    def predicate_is_write_operation(r: HttpRequest, uri_prefix: str) -> bool:
        isWriteDocumentOperation = (r.headers.get('x-ms-thinclient-proxy-resource-type') == 'docs'
                and r.headers.get('x-ms-thinclient-proxy-operation-type') != 'Read'
                and r.headers.get('x-ms-thinclient-proxy-operation-type') != 'ReadFeed'
                and r.headers.get('x-ms-thinclient-proxy-operation-type') != 'Query')

        return isWriteDocumentOperation and uri_prefix in r.url


    @staticmethod
    async def throw_after_delay(delay_in_ms: int, error: Exception):
        await asyncio.sleep(delay_in_ms / 1000.0)
        raise error

    @staticmethod
    async def throw_write_forbidden():
        raise CosmosHttpResponseError(
            status_code=403,
            message="Injected error disallowing writes in this region.",
            response=None,
            sub_status_code=3,
        )

    @staticmethod
    async def transform_convert_emulator_to_single_master_read_multi_region_account(r: HttpRequest,
                                     inner: Callable[[],asyncio.Task[AsyncHttpResponse]]) -> asyncio.Task[AsyncHttpResponse]:

        response = await inner()
        if not FaultInjectionTransport.predicate_is_database_account_call(response.request):
            return response

        await response.load_body()
        data = response.body()
        if response.status_code == 200 and data:
            data = data.decode("utf-8")
            result = json.loads(data)
            result["readableLocations"].append({"name": "East US", "databaseAccountEndpoint" : "https://localhost:8888/"})
            FaultInjectionTransport.logger.info("Transformed Account Topology: {}".format(result))
        return response