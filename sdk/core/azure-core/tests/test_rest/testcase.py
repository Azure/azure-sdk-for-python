# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.pipeline.transport import RequestsTransport
from azure.core.rest import HttpResponse, _StreamContextManager

def _create_http_response(request, stream):
    internal_response = RequestsTransport().send(request._internal_request, stream=stream)
    response = HttpResponse(
        request=request,
        _internal_response=internal_response
    )
    return response