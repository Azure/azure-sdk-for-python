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
from __future__ import annotations
import logging
import collections.abc as collections
from typing import TYPE_CHECKING, Any
import requests  # pylint: disable=networking-import-outside-azure-core-transport
from requests.structures import CaseInsensitiveDict  # pylint: disable=networking-import-outside-azure-core-transport
from urllib3.exceptions import (
    DecodeError as CoreDecodeError,
    ReadTimeoutError,
    ProtocolError,
)

from ..runtime.pipeline import Pipeline
from ._http_response_impl import _HttpResponseBaseImpl, HttpResponseImpl
from ..exceptions import (
    ServiceRequestError,
    ServiceResponseError,
    IncompleteReadError,
    HttpResponseError,
    DecodeError,
)

if TYPE_CHECKING:
    from ..rest import HttpRequest, HttpResponse

_LOGGER = logging.getLogger(__name__)


class _ItemsView(collections.ItemsView):
    def __contains__(self, item):
        if not (isinstance(item, (list, tuple)) and len(item) == 2):
            return False  # requests raises here, we just return False
        for k, v in self.__iter__():
            if item[0].lower() == k.lower() and item[1] == v:
                return True
        return False

    def __repr__(self):
        return "ItemsView({})".format(dict(self.__iter__()))


class _CaseInsensitiveDict(CaseInsensitiveDict):
    """Overriding default requests dict so we can unify
    to not raise if users pass in incorrect items to contains.
    Instead, we return False
    """

    def items(self):
        """Return a new view of the dictionary's items.

        :rtype: ~collections.abc.ItemsView[str, str]
        :returns: a view object that displays a list of (key, value) tuple pairs
        """
        return _ItemsView(self)


class _RestRequestsTransportResponseBase(_HttpResponseBaseImpl):
    def __init__(self, **kwargs):
        internal_response = kwargs.pop("internal_response")
        content = None
        if internal_response._content_consumed:
            content = internal_response.content
        headers = _CaseInsensitiveDict(internal_response.headers)
        super(_RestRequestsTransportResponseBase, self).__init__(
            internal_response=internal_response,
            status_code=internal_response.status_code,
            headers=headers,
            reason=internal_response.reason,
            content_type=headers.get("content-type"),
            content=content,
            **kwargs,
        )


class RestRequestsTransportResponse(HttpResponseImpl, _RestRequestsTransportResponseBase):
    def __init__(self, **kwargs):
        super(RestRequestsTransportResponse, self).__init__(stream_download_generator=StreamDownloadGenerator, **kwargs)


class StreamDownloadGenerator:
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :type pipeline: ~corehttp.runtime.pipeline.Pipeline
    :param response: The response object.
    :type response: ~corehttp.rest.HttpResponse
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """

    def __init__(
        self, pipeline: Pipeline[HttpRequest, HttpResponse], response: RestRequestsTransportResponse, **kwargs: Any
    ) -> None:

        self.pipeline = pipeline
        self.request = response.request
        self.response = response

        # TODO: determine if block size should be public on RestTransportResponse.
        self.block_size = response._block_size
        decompress = kwargs.pop("decompress", True)
        if len(kwargs) > 0:
            raise TypeError("Got an unexpected keyword argument: {}".format(list(kwargs.keys())[0]))
        internal_response = response._internal_response
        if decompress:
            self.iter_content_func = internal_response.iter_content(self.block_size)
        else:
            self.iter_content_func = _read_raw_stream(internal_response, self.block_size)
        self.content_length = int(response.headers.get("Content-Length", 0))

    def __len__(self):
        return self.content_length

    def __iter__(self):
        return self

    def __next__(self):
        internal_response = self.response._internal_response  # pylint: disable=protected-access
        try:
            chunk = next(self.iter_content_func)
            if not chunk:
                raise StopIteration()
            return chunk
        except StopIteration:
            internal_response.close()
            raise StopIteration()  # pylint: disable=raise-missing-from
        except requests.exceptions.StreamConsumedError:
            raise
        except requests.exceptions.ContentDecodingError as err:
            raise DecodeError(err, error=err) from err
        except requests.exceptions.ChunkedEncodingError as err:
            msg = err.__str__()
            if "IncompleteRead" in msg:
                _LOGGER.warning("Incomplete download: %s", err)
                internal_response.close()
                raise IncompleteReadError(err, error=err) from err
            _LOGGER.warning("Unable to stream download: %s", err)
            internal_response.close()
            raise HttpResponseError(err, error=err) from err
        except Exception as err:
            _LOGGER.warning("Unable to stream download: %s", err)
            internal_response.close()
            raise


def _read_raw_stream(response, chunk_size=1):
    # Special case for urllib3.
    if hasattr(response.raw, "stream"):
        try:
            yield from response.raw.stream(chunk_size, decode_content=False)
        except ProtocolError as e:
            raise ServiceResponseError(e, error=e) from e
        except CoreDecodeError as e:
            raise DecodeError(e, error=e) from e
        except ReadTimeoutError as e:
            raise ServiceRequestError(e, error=e) from e
    else:
        # Standard file-like object.
        while True:
            chunk = response.raw.read(chunk_size)
            if not chunk:
                break
            yield chunk

    # following behavior from requests iter_content, we set content consumed to True
    # https://github.com/psf/requests/blob/master/requests/models.py#L774
    response._content_consumed = True  # pylint: disable=protected-access
