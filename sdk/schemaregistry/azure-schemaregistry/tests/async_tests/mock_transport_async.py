# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

from azure.core.pipeline.transport import AsyncHttpTransport


class AsyncMockResponse:
    def __init__(
        self, schema_id, schema_name, schema_group_name, schema_version, content_type, *, content=b"", status_code=200
    ) -> None:
        self._schema_id = schema_id
        self._schema_name = schema_name
        self._schema_group_name = schema_group_name
        self._schema_version = schema_version
        self._content = content
        self.content_type = content_type
        self._status_code = status_code

    @property
    def status_code(self):
        return self._status_code

    @property
    def headers(self):
        return {
            "Schema-Version": self._schema_version,
            "Schema-Group-Name": self._schema_group_name,
            "Schema-Name": self._schema_name,
            "Schema-Id": self._schema_id,
            "Schema-Id-Location": "eastus",
            "Location": "eastus",
            "Content-Type": f"{self.content_type}",
        }

    @property
    def content(self):
        return self._content

    def iter_bytes(self):
        pass

    def raise_for_status(self):
        pass

    async def read(self):
        pass

    def text(self, encoding=None):
        pass

    def reason(self):
        pass


class AsyncMockTransport(AsyncHttpTransport):
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def open(self):
        pass

    async def close(self):
        pass

    async def send(self, request, **kwargs):
        response = self._response
        return response
