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
import copy
from typing import Any
from ._types import (
    QueryParamTypes,
    HeaderTypes,
    CookieTypes,
    Content,
    RequestFiles,
    ByteStream,
)

class HttpRequest(object):
    """Represents a HTTP request.

    URL can be given without query parameters, to be added later using "format_parameters".
    """

    def __init__(
        self,
        method: str,
        url: str,
        *,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        content: Content = None,
        data: dict = None,
        files: RequestFiles = None,
        json: Any = None,
        stream_response: bool = True,
    ) -> None:
        self.method = method
        self.url = url
        # doesn't expose params, automatically formats URL with it
        self.headers = headers
        self.stream_response = stream_response


    def __repr__(self):
        return "<HttpRequest [{}], url: '{}'>".format(
            self.method, self.url
        )

    def __deepcopy__(self, memo=None):
        try:
            return HttpRequest(self.method, self.url, self.headers, None, None)
        except (ValueError, TypeError):
            return copy.copy(self)

    @property
    def content(self) -> bytes:
        """The query parameters of the request as a dict.
        """
        return b''
