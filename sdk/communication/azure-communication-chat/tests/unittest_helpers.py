# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from azure.core.pipeline.transport import HttpResponse
from azure.core.pipeline.transport._base import _HttpResponseBase

class MockHttpResponse(_HttpResponseBase):
    def __init__(self, status_code=200, headers=None, json_payload=None):
        self.status_code = status_code
        self.headers = headers or {"Content-Type": "application/json"}
        self._body = json.dumps(json_payload).encode("utf-8") if json_payload else b""
        self.reason = "OK"
        self.content_type = self.headers.get("Content-Type", "")

    def text(self, encoding=None):
        return self._body.decode(encoding or "utf-8")

    @property
    def content(self):
        return self._body

    def read(self):
        return self._body

    def close(self):
        pass

def mock_response(status_code=200, headers=None, json_payload=None):
    return MockHttpResponse(status_code=status_code, headers=headers, json_payload=json_payload)