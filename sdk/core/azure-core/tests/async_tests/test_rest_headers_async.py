# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.core.rest import HttpRequest

@pytest.mark.asyncio
async def test_response_headers_case_insensitive(client):
    request = HttpRequest("GET", "/basic/headers")
    response = await client.send_request(request)
    response.raise_for_status()
    assert (
        response.headers["lowercase-header"] ==
        response.headers["LOWERCASE-HEADER"] ==
        response.headers["Lowercase-Header"] ==
        response.headers["lOwErCasE-HeADer"] ==
        "lowercase"
    )
    assert (
        response.headers["allcaps-header"] ==
        response.headers["ALLCAPS-HEADER"] ==
        response.headers["Allcaps-Header"] ==
        response.headers["AlLCapS-HeADer"] ==
        "ALLCAPS"
    )
    assert (
        response.headers["camelcase-header"] ==
        response.headers["CAMELCASE-HEADER"] ==
        response.headers["CamelCase-Header"] ==
        response.headers["cAMeLCaSE-hEadER"] ==
        "camelCase"
    )
    return response
