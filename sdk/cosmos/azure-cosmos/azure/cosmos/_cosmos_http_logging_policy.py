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



class CosmosHttpLoggingPolicy(HttpLoggingPolicy):

    def __init__(self, logger=None, **kwargs): # pylint: disable=unused-argument
        self._enable_diagnostics_logging = kwargs.pop("enable_diagnostics_logging", None)
        super().__init__(logger, **kwargs)
        if self._enable_diagnostics_logging:
            self.logger = logger

    def on_request(self, request): # pylint: disable=too-many-return-statements, too-many-statements
        # type: (PipelineRequest) -> None
        http_request = request.http_request
        options = request.context.options
        self._enable_diagnostics_logging = request.context.setdefault(
            "enable_diagnostics_logging",
            options.pop("enable_diagnostics_logging", self._enable_diagnostics_logging))
        if self._enable_diagnostics_logging:
            # Get logger in my context first (request has been retried)
            # then read from kwargs (pop if that's the case)
            # then use my instance logger
            logger = request.context.setdefault("logger", options.pop("logger", self.logger))

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
                if multi_record:
                    logger.info("Request URL: %r", redacted_url)
                    logger.info("Request method: %r", http_request.method)
                    logger.info("Request headers:")
                    for header, value in http_request.headers.items():
                        logger.info("    %r: %r", header, value)
                    if isinstance(http_request.body, types.GeneratorType):
                        logger.info("File upload")
                        return
                    try:
                        if isinstance(http_request.body, types.AsyncGeneratorType):
                            logger.info("File upload")
                            return
                    except AttributeError:
                        pass
                    if http_request.body:
                        logger.info("A body is sent with the request")
                        return
                    logger.info("No body was attached to the request")
                    return
                log_string = "Request URL: '{}'".format(redacted_url)
                log_string += "\nRequest method: '{}'".format(http_request.method)
                log_string += "\nRequest headers:"
                for header, value in http_request.headers.items():
                    log_string += "\n    '{}': '{}'".format(header, value)
                if isinstance(http_request.body, types.GeneratorType):
                    log_string += "\nFile upload"
                    logger.info(log_string)
                    return
                try:
                    if isinstance(http_request.body, types.AsyncGeneratorType):
                        log_string += "\nFile upload"
                        logger.info(log_string)
                        return
                except AttributeError:
                    pass
                if http_request.body:
                    log_string += "\nA body is sent with the request"
                    logger.info(log_string)
                    return
                log_string += "\nNo body was attached to the request"
                logger.info(log_string)

            except Exception as err:  # pylint: disable=broad-except
                logger.warning("Failed to log request: %s", repr(err))
        else:
            super().on_request(request)


    def on_response(self, request, response):  # pylint: disable=too-many-return-statements, too-many-statements
        # type: (PipelineRequest, PipelineResponse) -> None
        if self._enable_diagnostics_logging:
            http_response = response.http_response
            ir = http_response.internal_response
            try:
                logger = response.context["logger"]

                if not logger.isEnabledFor(logging.INFO):
                    return

                multi_record = os.environ.get(HttpLoggingPolicy.MULTI_RECORD_LOG, False)
                if multi_record:
                    logger.info("Response status: %r", http_response.status_code)
                    logger.info("Response status reason: %r", ir.reason)
                    try:
                        logger.info("Elapsed Time: %r", ir.elapsed)
                    except AttributeError:
                        logger.info("Elapsed Time: %r", None)
                    if http_response.status_code >= 400:
                        sm = ir.text
                        sm.replace("true", "True")
                        sm.replace("false", "False")
                        temp_sm = ast.literal_eval(sm)
                        temp_sm['message'] = temp_sm['message'].replace("\r", " ")
                        logger.into("Response status error message: %r", temp_sm['message'])
                    logger.info("Response headers:")
                    for res_header, value in http_response.headers.items():
                        logger.info("    %r: %r", res_header, value)
                    return
                log_string = "Response status: {}".format(http_response.status_code)
                log_string += "\nResponse status reason: {}".format(ir.reason)
                try:
                    log_string += "\nElapsed Time: {}".format(ir.elapsed)
                except AttributeError:
                    log_string += "\nElapsed Time: {}".format(None)
                if http_response.status_code >= 400:
                    sm = ir.text
                    sm.replace("true", "True")
                    sm.replace("false", "False")
                    temp_sm = ast.literal_eval(sm)
                    temp_sm['message'] = temp_sm['message'].replace("\r", " ")
                    log_string += "\nResponse status error message: {}".format(temp_sm['message'])
                log_string += "\nResponse headers:"
                for res_header, value in http_response.headers.items():
                    log_string += "\n    '{}': '{}'".format(res_header, value)
                logger.info(log_string)
            except Exception as err:  # pylint: disable=broad-except
                logger.warning("Failed to log response: %s", repr(err))
        else:
            super().on_response(request, response)
