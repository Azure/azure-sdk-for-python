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

from typing import TYPE_CHECKING

from ..pipeline.transport._base import (
    HttpRequest as _PipelineTransportHttpRequest,
    _case_insensitive_dict
)
from ._handle_request_body import (
    handle_request_body,
    set_content_length_header
)

if TYPE_CHECKING:
    from typing import Any, Optional, Union
    from ._types import QueryTypes
    try:
        from multidict import CIMultiDict
        from requests.structures import CaseInsensitiveDict
    except ImportError:
        pass

def _format_parameters(url, query):
    # type: (str, Optional[QueryTypes]) -> str
    """Placeholder code using current implementation in pipeline.transport
    Johan is working on new code that accepts list of tuples etc.
    """
    dummy_request = _PipelineTransportHttpRequest(method="dummy", url=url)
    query = kwargs.pop("query", None)
    if query:
        dummy_request.format_parameters(query)
    return dummy_request.url

class HttpRequest(object):
    """Represents an HTTP request.

    :param method: HTTP method (GET, HEAD, etc.)
    :type method: str or ~azure.core.protocol.HttpVerbs
    :param str url: The url for your request
    :keyword params: Query parameters to be mapped into your URL. Your input
     should be a mapping or sequence of query name to query value(s).
    :paramtype params: mapping or sequence
    :keyword headers: HTTP headers you want in your request. Your input should
     be a mapping or sequence of header name to header value.
    :paramtype headers: mapping or sequence
    :keyword content: Content you want in your request body.
    :paramtype content: str or bytes or iterable[bytes] or asynciterable[bytes]
    :keyword any json: A JSON serializable object. We handle JSON-serialization for your
     object.
    :keyword dict data: Form data you want in your request body.
    :keyword files: Files you want to in your request body. Your input should be
     a mapping or sequence of file name to file content.
    :paramtype files: mapping or sequence
    """

    def __init__(self, method, url, **kwargs):
        # type: (str, str, Any) -> None
        self.method = method
        self.url = _format_parameters(url, kwargs.pop("query", None))
        self.headers = _case_insensitive_dict(kwargs.pop("headers", None))  # type: Union[CIMultiDict, CaseInsensitiveDict]

        self._body = handle_request_body(
            content=kwargs.pop("content", None),
            json=kwargs.pop("json", None),
            files=kwargs.pop("files", None),
            data=kwargs.pop("data", None),
            headers=self.headers,
            **kwargs
        )
        if self._body:
            set_content_length_header(self._body, self.headers)

    def __repr__(self):
        return "<HttpRequest [{}], url: '{}'>".format(
            self.method, self.url
        )