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
import aiohttp
import logging
import sys

from azure.core.pipeline.transport import AioHttpTransport
from azure.core.rest import HttpRequest, AsyncHttpResponse
from collections.abc import MutableMapping
from typing import Any, Callable

class FaulInjectionTransport(AioHttpTransport):
    def __init__(self, logger: logging.Logger, *, session: aiohttp.ClientSession | None = None, loop=None, session_owner: bool = True, **config):
        self.logger = logger
        self.faults = []
        self.requestTransformations = []
        self.responseTransformations = []
        super().__init__(session=session, loop=loop, session_owner=session_owner, **config)

    def addFault(self, predicate: Callable[[HttpRequest], bool], faultFactory: Callable[[HttpRequest], asyncio.Task[Exception]]):
        self.faults.append({"predicate": predicate, "apply": faultFactory})

    def addRequestTransformation(self, predicate: Callable[[HttpRequest], bool], requestTransformation: Callable[[HttpRequest], asyncio.Task[HttpRequest]]):
        self.requestTransformations.append({"predicate": predicate, "apply": requestTransformation})

    def addResponseTransformation(self, predicate: Callable[[HttpRequest], bool], responseTransformation: Callable[[HttpRequest, Callable[[HttpRequest], asyncio.Task[AsyncHttpResponse]]], AsyncHttpResponse]):
        self.responseTransformations.append({
            "predicate": predicate, 
            "apply": responseTransformation})    

    def firstItem(self, iterable, condition=lambda x: True):
        """
        Returns the first item in the `iterable` that satisfies the `condition`.
        
        If no item satisfies the condition, it returns None.
        """
        return next((x for x in iterable if condition(x)), None)

    async def send(self, request: HttpRequest, *, stream: bool = False, proxies: MutableMapping[str, str] | None = None, **config):
        # find the first fault Factory with matching predicate if any
        firstFaultFactory = self.firstItem(iter(self.faults), lambda f: f["predicate"](request))
        if (firstFaultFactory != None):
            injectedError = await firstFaultFactory["apply"]()
            self.logger.info("Found to-be-injected error {}".format(injectedError))
            raise injectedError

        # apply the chain of request transformations with matching predicates if any
        matchingRequestTransformations = filter(lambda f: f["predicate"](f["predicate"]), iter(self.requestTransformations))
        for currentTransformation in matchingRequestTransformations:
            request = await currentTransformation["apply"](request)

        firstResonseTransformation = self.firstItem(iter(self.responseTransformations), lambda f: f["predicate"](request))
        
        getResponseTask = super().send(request, stream=stream, proxies=proxies, **config)
        
        if (firstResonseTransformation != None):
            self.logger.info(f"Invoking response transformation")
            response = await firstResonseTransformation["apply"](request, lambda: getResponseTask)        
            self.logger.info(f"Received response transformation result with status code {response.status_code}")
            return response
        else:
            self.logger.info(f"Sending request to {request.url}")
            response = await getResponseTask
            self.logger.info(f"Received response with status code {response.status_code}")
            return response
    