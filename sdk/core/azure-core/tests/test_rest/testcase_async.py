# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.rest import AsyncHttpResponse

async def _create_http_response(request, stream):
    internal_response = await AioHttpTransport().send(request._internal_request, stream=stream)
    response = AsyncHttpResponse(
        request=request,
        _internal_response=internal_response
    )
    return response