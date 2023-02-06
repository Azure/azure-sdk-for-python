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

import os
import urllib
import logging
import types
import ast

from azure.core.pipeline.policies import HttpLoggingPolicy

from .http_constants import HttpHeaders


class CosmosHttpLoggingPolicy(HttpLoggingPolicy):

    def __init__(self, logger: Optional[logging.Logger] = None, **kwargs) -> None: # pylint: disable=unused-argument
        self._enable_diagnostics_logging = kwargs.pop("enable_diagnostics_logging", False)
        super().__init__(logger, **kwargs)
        if self._enable_diagnostics_logging:
            cosmos_disallow_list = ["Authorization", "ProxyAuthorization"]
            cosmos_allow_list = [
                v for k, v in HttpHeaders.__dict__.items() if not k.startswith("_") and k not in cosmos_disallow_list
            ]
            self.allowed_header_names.update(set(cosmos_allow_list))

    def _format_error(self, payload: str) -> str:
        payload = payload.replace("true", "True")
        payload = payload.replace("false", "False")
        output = ast.literal_eval(payload)
        return output['message'].replace("\r", " ")

    def on_response(
        self,
        request: PipelineRequest[HTTPRequestType],
        response: PipelineResponse[HTTPRequestType, HTTPResponseType],
    ) -> None:
        logger = request.context.setdefault(
            "logger", options.pop("logger", self.logger)
        )
        try:
            if not logger.isEnabledFor(logging.INFO):
                return
            super().on_response(request, response)

            if self._enable_diagnostics_logging:
                ir = response.http_response.internal_response
                multi_record = os.environ.get(HttpLoggingPolicy.MULTI_RECORD_LOG, False)
                if multi_record:
                    logger.info("Response status reason: %r", ir.reason)
                    try:
                        logger.info("Elapsed Time: %r", ir.elapsed)
                    except AttributeError:
                        logger.info("Elapsed Time: %r", None)
                    if http_response.status_code >= 400:
                        logger.into("Response status error message: %r", self._format_error(ir.text))
                    return
                log_string = "Cosmos diagnostics:"
                log_string += "\nResponse status reason: {}".format(ir.reason)
                try:
                    log_string += "\nElapsed Time: {}".format(ir.elapsed)
                except AttributeError:
                    log_string += "\nElapsed Time: {}".format(None)
                if http_response.status_code >= 400:
                    log_string += "\nResponse status error message: {}".format(self._format_error(ir.text))
                logger.info(log_string)
        except Exception as err:  # pylint: disable=broad-except
            logger.warning("Failed to log response: %s", repr(err))
