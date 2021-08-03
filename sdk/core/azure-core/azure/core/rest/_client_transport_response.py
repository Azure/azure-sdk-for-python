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
from ._rest import _HttpResponseBase, _case_insensitive_dict, HttpResponse

class _HttpClientTransportResponse(_HttpResponseBase):

    def __init__(self, **kwargs):
        super(_HttpClientTransportResponse, self).__init__(**kwargs)
        self.status_code = self._internal_response.status
        self.headers = _case_insensitive_dict(self._internal_response.getheaders())
        self.reason = self._internal_response.reason
        self.content_type = self.headers.get("Content-Type")
        self._data = None

    @property
    def content(self):
        if self._data is None:
            self._data = self._internal_response.read()
        return self._data

class HttpClientTransportResponse(_HttpClientTransportResponse, HttpResponse):
    pass
