# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
############################## LISTS USED TO PARAMETERIZE TESTS ##############################
from azure.core.rest import HttpRequest as RestHttpRequest
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest

HTTP_REQUESTS = [PipelineTransportHttpRequest, RestHttpRequest]


############################## HELPER FUNCTIONS ##############################

def is_rest(http_request):
    return hasattr(http_request, "content")

def create_http_request(http_request, *args, **kwargs):
    if hasattr(http_request, "content"):
        method = args[0]
        url = args[1]
        try:
            headers = args[2]
        except IndexError:
            headers = None
        try:
            files = args[3]
        except IndexError:
            files = None
        try:
            data = args[4]
        except IndexError:
            data = None
        return http_request(
            method=method,
            url=url,
            headers=headers,
            files=files,
            data=data,
            **kwargs
        )
    return http_request(*args, **kwargs)
