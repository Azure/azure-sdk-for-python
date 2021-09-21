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
try:
    import collections.abc as collections
except ImportError:
    import collections  # type: ignore

from requests.structures import CaseInsensitiveDict

from ._http_response_impl import _HttpResponseBaseImpl, HttpResponseImpl
from ..pipeline.transport._requests_basic import StreamDownloadGenerator

class _ItemsView(collections.ItemsView):

    def __contains__(self, item):
        if not (isinstance(item, (list, tuple)) and len(item) == 2):
            return False  # requests raises here, we just return False
        for k, v in self.__iter__():
            if item[0].lower() == k.lower() and item[1] == v:
                return True
        return False

    def __repr__(self):
        return 'ItemsView({})'.format(dict(self.__iter__()))

class _CaseInsensitiveDict(CaseInsensitiveDict):
    """Overriding default requests dict so we can unify
    to not raise if users pass in incorrect items to contains.
    Instead, we return False
    """

    def items(self):
        """Return a new view of the dictionary's items."""
        return _ItemsView(self)

class _RestRequestsTransportResponseBase(_HttpResponseBaseImpl):
    def __init__(self, **kwargs):
        internal_response = kwargs.pop("internal_response")
        content = None
        if internal_response._content_consumed:
            content = internal_response.content
        super(_RestRequestsTransportResponseBase, self).__init__(
            internal_response=internal_response,
            status_code=internal_response.status_code,
            headers=_CaseInsensitiveDict(internal_response.headers),
            reason=internal_response.reason,
            content_type=internal_response.headers.get('content-type', ""),
            content=content,
            **kwargs
        )

class RestRequestsTransportResponse(HttpResponseImpl, _RestRequestsTransportResponseBase):

    def __init__(self, **kwargs):
        super(RestRequestsTransportResponse, self).__init__(
            stream_download_generator=StreamDownloadGenerator,
            **kwargs
        )
