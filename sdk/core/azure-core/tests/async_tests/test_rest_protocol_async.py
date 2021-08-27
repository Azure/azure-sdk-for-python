# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------=
import pytest
from azure.core.rest import AsyncHttpResponse

def test_initialize_response():
    with pytest.raises(TypeError) as ex:
        AsyncHttpResponse()
    assert "Protocols cannot be instantiated" in str(ex)

def test_no_required_params():
    class MyHttpResponse(AsyncHttpResponse):
        pass
    MyHttpResponse()
