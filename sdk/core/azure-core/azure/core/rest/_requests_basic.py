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

from ..pipeline.transport._requests_basic import StreamDownloadGenerator
from ._helpers import StreamConsumedError, ResponseClosedError

if TYPE_CHECKING:
    from typing import Optional, Iterator
try:
    from ._rest_py3 import HttpResponse
except (SyntaxError, ImportError):
    from ._rest import HttpResponse


class RequestsTransportResponse(HttpResponse):
    def __init__(self, **kwargs):
        super(RequestsTransportResponse, self).__init__(**kwargs)
        self.status_code = self.internal_response.status_code
        self.headers = self.internal_response.headers
        self.reason = self.internal_response.reason
        self.content_type = self.internal_response.headers["Content-Type"]

    @property
    def text(self):
        # type: (...) -> str
        encoding = self.encoding
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
        return self.internal_response.text

    def _stream_download_helper(self, decompress, chunk_size=None):
        if self.is_stream_consumed:
            raise StreamConsumedError()
        if self.is_closed:
            raise ResponseClosedError()

        self.is_stream_consumed = True
        stream_download = StreamDownloadGenerator(
            pipeline=None,
            response=self,
            chunk_size=chunk_size,
            decompress=decompress,
        )
        for part in stream_download:
            self._num_bytes_downloaded += len(part)
            yield part

    def iter_raw(self, chunk_size=None):
        # type: (Optional[int]) -> Iterator[bytes]
        """Iterate over the raw response bytes
        """
        for raw_bytes in self._stream_download_helper(decompress=False, chunk_size=chunk_size):
            yield raw_bytes
        self.close()

    def iter_bytes(self, chunk_size=None):
        # type: (Optional[int]) -> Iterator[bytes]
        """Iterate over the response bytes
        """
        if self._read_content:
            if chunk_size is None:
                chunk_size = len(self._content)
            for i in range(0, len(self._content), chunk_size):
                yield self._content[i: i + chunk_size]
        else:
            for part in self._stream_download_helper(decompress=True, chunk_size=chunk_size):
                yield part
        self.close()
