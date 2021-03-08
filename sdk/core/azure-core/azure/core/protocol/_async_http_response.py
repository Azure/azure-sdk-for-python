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
from collections.abc import AsyncIterator
from ._http_response import _HttpResponseBase, PipelineType
from typing import (
    AsyncIterator as AsyncIteratorType,
)
from ..pipeline.transport._base_async import _PartGenerator

class AsyncHttpResponse(_HttpResponseBase):  # pylint: disable=abstract-method
    """An AsyncHttpResponse ABC.

    Allows for the asynchronous streaming of data from the response.
    """

    def stream_download(self, pipeline) -> AsyncIteratorType[bytes]:
        """Generator for streaming response body data.

        Should be implemented by sub-classes if streaming download
        is supported. Will return an asynchronous generator.

        :param pipeline: The pipeline object
        :type pipeline: ~azure.core.pipeline
        :rtype: AsyncIterator[bytes]
        """

    def parts(self) -> AsyncIterator:
        """Assuming the content-type is multipart/mixed, will return the parts as an async iterator.

        :rtype: AsyncIterator
        :raises ValueError: If the content is not multipart/mixed
        """
        if not self.content_type or not self.content_type.startswith("multipart/mixed"):
            raise ValueError(
                "You can't get parts if the response is not multipart/mixed"
            )

        return _PartGenerator(self)