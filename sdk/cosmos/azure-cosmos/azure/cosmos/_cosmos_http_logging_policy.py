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
from typing import Optional, Union, TYPE_CHECKING

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import HttpLoggingPolicy

from .http_constants import HttpHeaders

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
        *,
        enable_diagnostics_logging: bool = False,
        **kwargs
    ):
        self._enable_diagnostics_logging = enable_diagnostics_logging
        super().__init__(logger, **kwargs)
        if self._enable_diagnostics_logging:
            cosmos_disallow_list = ["Authorization", "ProxyAuthorization"]
            cosmos_allow_list = [
                v for k, v in HttpHeaders.__dict__.items() if not k.startswith("_") and k not in cosmos_disallow_list
            ]
            self.allowed_header_names = set(cosmos_allow_list)

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        super().on_request(request)
        if self._enable_diagnostics_logging:
            request.context["start_time"] = time.time()

    def on_response(
        self,
        request: PipelineRequest[HTTPRequestType],
        response: PipelineResponse[HTTPRequestType, HTTPResponseType],  # type: ignore[override]
    ) -> None:
        super().on_response(request, response)
        if self._enable_diagnostics_logging:
            http_response = response.http_response
            options = response.context.options
            logger = request.context.setdefault("logger", options.pop("logger", self.logger))
            try:
                if "start_time" in request.context:
                    logger.info("Elapsed time in seconds: {}".format(time.time() - request.context["start_time"]))
                else:
                    logger.info("Elapsed time in seconds: unknown")
                if http_response.status_code >= 400:
                    logger.info("Response error message: %r", _format_error(http_response.text()))
            except Exception as err:  # pylint: disable=broad-except
                logger.warning("Failed to log request: %s", repr(err))
