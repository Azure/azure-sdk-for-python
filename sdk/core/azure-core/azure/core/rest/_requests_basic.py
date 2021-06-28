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

from ..exceptions import ResponseNotReadError, StreamConsumedError, StreamClosedError
from . import _HttpResponseBase, HttpResponse
from ..pipeline.transport._requests_basic import StreamDownloadGenerator

if TYPE_CHECKING:
    from typing import Iterator

class _RestRequestsTransportResponseBase(_HttpResponseBase):
    def __init__(self, **kwargs):
        super(_RestRequestsTransportResponseBase, self).__init__(**kwargs)
        self.status_code = self.internal_response.status_code
        self.headers = self.internal_response.headers
        self.reason = self.internal_response.reason
        self.content_type = self.internal_response.headers.get('content-type')

    def _get_content(self):
        """Return the internal response's content"""
        if not self.internal_response._content_consumed:  # pylint: disable=protected-access
            # if we just call .content, requests will read in the content.
            # we want to read it in our own way
            return None
        try:
            return self.internal_response.content
        except RuntimeError:
            # requests throws a RuntimeError if the content for a response is already consumed
            return None

    def _set_content(self, val):
        """Set the internal response's content"""
        self.internal_response._content = val  # pylint: disable=protected-access

    def _has_content(self):
        return self._get_content() is not None

    @_HttpResponseBase.encoding.setter  # type: ignore
    def encoding(self, value):
        # type: (str) -> None
        # ignoring setter bc of known mypy issue https://github.com/python/mypy/issues/1465
        self._encoding = value
        encoding = value
        if not encoding:
            # There is a few situation where "requests" magic doesn't fit us:
            # - https://github.com/psf/requests/issues/654
            # - https://github.com/psf/requests/issues/1737
            # - https://github.com/psf/requests/issues/2086
            from codecs import BOM_UTF8
            if self.internal_response.content[:3] == BOM_UTF8:
                encoding = "utf-8-sig"
        if encoding:
            if encoding == "utf-8":
                encoding = "utf-8-sig"
        self.internal_response.encoding = encoding

    @property
    def text(self):
        if not self._has_content():
            raise ResponseNotReadError()
        return self.internal_response.text

def _stream_download_helper(decompress, response):
    if response.is_stream_consumed:
        raise StreamConsumedError()
    if response.is_closed:
        raise StreamClosedError()

    response.is_stream_consumed = True
    stream_download = StreamDownloadGenerator(
        pipeline=None,
        response=response,
        decompress=decompress,
    )
    for part in stream_download:
        response._num_bytes_downloaded += len(part)
        yield part

class RestRequestsTransportResponse(HttpResponse, _RestRequestsTransportResponseBase):

    def iter_bytes(self):
        # type: () -> Iterator[bytes]
        """Iterates over the response's bytes. Will decompress in the process
        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """
        if self._has_content():
            yield self._get_content()
        else:
            for part in _stream_download_helper(
                decompress=True,
                response=self,
            ):
                yield part
        self.close()

    def iter_raw(self):
        # type: () -> Iterator[bytes]
        """Iterates over the response's bytes. Will not decompress in the process
        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """
        for raw_bytes in _stream_download_helper(
            decompress=False,
            response=self,
        ):
            yield raw_bytes
        self.close()
