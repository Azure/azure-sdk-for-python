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
import cgi
import collections
from json import loads

from typing import TYPE_CHECKING

from azure.core.exceptions import HttpResponseError

from .._utils import _case_insensitive_dict
from ..pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from ._helpers import (
    FilesType,
    lookup_encoding,
    parse_lines_from_text,
    set_content_body,
    set_json_body,
    set_multipart_body,
    set_urlencoded_body,
    format_parameters,
)
from ..exceptions import StreamClosedError, ResponseNotReadError, StreamConsumedError
if TYPE_CHECKING:
    from typing import (
        Iterable,
        Optional,
        Any,
        Iterator,
        Union,
        Dict,
    )
    from ._helpers import HeadersType
    ByteStream = Iterable[bytes]
    ContentType = Union[str, bytes, ByteStream]

    from ._helpers import ParamsType, HeadersType, ContentTypeBase as ContentType



################################## CLASSES ######################################

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
    :keyword dict data: Form data you want in your request body. Use for form-encoded data, i.e.
     HTML forms.
    :keyword any json: A JSON serializable object. We handle JSON-serialization for your
     object, so use this for more complicated data structures than `data`.
    :keyword files: Files you want to in your request body. Use for uploading files with
     multipart encoding. Your input should be a mapping or sequence of file name to file content.
     Use the `data` kwarg in addition if you want to include non-file data files as part of your request.
    :paramtype files: mapping or sequence
    :keyword content: Content you want in your request body. Think of it as the kwarg you should input
     if your data doesn't fit into `json`, `data`, or `files`. Accepts a bytes type, or a generator
     that yields bytes.
    :paramtype content: str or bytes or iterable[bytes] or asynciterable[bytes]
    :ivar str url: The URL this request is against.
    :ivar str method: The method type of this request.
    :ivar headers: The HTTP headers you passed in to your request
    :vartype headers: mapping or sequence
    :ivar bytes content: The content passed in for the request
    """

    def __init__(self, method, url, **kwargs):
        # type: (str, str, Any) -> None

        self.url = url
        self.method = method

        params = kwargs.pop("params", None)
        if params:
            self.url = format_parameters(self.url, params)
        self._files = None
        self._data = None

        default_headers = self._set_body(
            content=kwargs.pop("content", None),
            data=kwargs.pop("data", None),
            files=kwargs.pop("files", None),
            json=kwargs.pop("json", None),
        )
        self.headers = _case_insensitive_dict(default_headers)
        self.headers.update(kwargs.pop("headers", {}))

        if kwargs:
            raise TypeError(
                "You have passed in kwargs '{}' that are not valid kwargs.".format(
                    "', '".join(list(kwargs.keys()))
                )
            )

    def _set_body(self, content, data, files, json):
        # type: (Optional[ContentType], Optional[dict], Optional[FilesType], Any) -> Dict[str, str]
        """Sets the body of the request, and returns the default headers
        """
        default_headers = {}
        if data is not None and not isinstance(data, dict):
            # should we warn?
            content = data
        if content is not None:
            default_headers, self._data = set_content_body(content)
            return default_headers
        if json is not None:
            default_headers, self._data = set_json_body(json)
            return default_headers
        if files:
            default_headers, self._files = set_multipart_body(files)
        if data:
            default_headers, self._data = set_urlencoded_body(data)
        if files and data:
            # little hacky, but for files we don't send a content type with
            # boundary so requests / aiohttp etc deal with it
            default_headers.pop("Content-Type")
        return default_headers

    def _update_headers(self, default_headers):
        # type: (Dict[str, str]) -> None
        for name, value in default_headers.items():
            if name == "Transfer-Encoding" and "Content-Length" in self.headers:
                continue
            self.headers.setdefault(name, value)

    @property
    def content(self):
        # type: (...) -> Any
        """Gets the request content.
        """
        return self._data or self._files
    #     if not self._read_content:
    #         raise RequestNotReadError()
    #     return self._content

    # def read(self):
    #     # type: (...) -> bytes
    #     if not self._read_content:
    #         if not isinstance(self._content, collections.Iterable):
    #             raise TypeError("read() should only be called on sync streams.")
    #         self._content = b"".join(self._content)
    #         self._read_content = True
    #     return self._content

    def __repr__(self):
        # type: (...) -> str
        return "<HttpRequest [{}], url: '{}'>".format(
            self.method, self.url
        )

    def __deepcopy__(self, memo=None):
        try:
            return HttpRequest(
                method=self.method,
                url=self.url,
                headers=self.headers,
                files=copy.deepcopy(self._files),
                data=copy.deepcopy(self._data),
            )
        except (ValueError, TypeError):
            return copy.copy(self)

    def _to_pipeline_transport_request(self):
        request = PipelineTransportHttpRequest(
            method=self.method,
            url=self.url,
            headers=self.headers,
            files=self._files,
            data=self._data,
        )
        # following pipeline.transport, we pop the content-type if there are files
        # this is bc we want an empty content type so the transport, i.e. requests,
        # will set our boundary for us
        if request.files:
            request.headers.pop("Content-Type", None)
        return request


class _HttpResponseBase(object):
    """Class for HttpResponse.

    :keyword request: The request that resulted in this response.
    :paramtype request: ~azure.core.rest.HttpRequest
    :ivar int status_code: The status code of this response
    :ivar headers: The response headers
    :vartype headers: dict[str, any]
    :ivar str reason: The reason phrase for this response
    :ivar bytes content: The response content in bytes
    :ivar str url: The URL that resulted in this response
    :ivar str encoding: The response encoding. Is settable, by default
     is the response Content-Type header
    :ivar str text: The response body as a string.
    :ivar request: The request that resulted in this response.
    :vartype request: ~azure.core.rest.HttpRequest
    :ivar str content_type: The content type of the response
    :ivar bool is_error: Whether this response is an error.
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.request = kwargs.pop("request")
        self.internal_response = kwargs.pop("internal_response")
        self.status_code = None
        self.headers = {}
        self.reason = None
        self.is_closed = False
        self.is_stream_consumed = False
        self._num_bytes_downloaded = 0
        self.content_type = None
        self._json = None  # this is filled in ContentDecodePolicy, when we deserialize
        self._connection_data_block_size = None
        self._content = None

    @property
    def url(self):
        # type: (...) -> str
        """Returns the URL that resulted in this response"""
        return self.request.url

    def _get_charset_encoding(self):
        content_type = self.headers.get("Content-Type")

        if not content_type:
            return None
        _, params = cgi.parse_header(content_type)
        encoding = params.get('charset') # -> utf-8
        if encoding is None or not lookup_encoding(encoding):
            return None
        return encoding

    def _get_content(self):
        """Return the internal response's content"""
        return self._content

    def _set_content(self, val):
        """Set the internal response's content"""
        self._content = val

    def _has_content(self):
        """How to check if your internal response has content"""
        return self._content is not None

    @property
    def encoding(self):
        # type: (...) -> Optional[str]
        """Returns the response encoding. By default, is specified
        by the response Content-Type header.
        """

        try:
            return self._encoding
        except AttributeError:
            return self._get_charset_encoding()

    @encoding.setter
    def encoding(self, value):
        # type: (str) -> None
        """Sets the response encoding"""
        self._encoding = value

    @property
    def text(self):
        # type: (...) -> str
        """Returns the response body as a string"""
        encoding = self.encoding
        if encoding == "utf-8" or encoding is None:
            encoding = "utf-8-sig"
        return self.content.decode(encoding)

    @property
    def num_bytes_downloaded(self):
        # type: (...) -> int
        """See how many bytes of your stream response have been downloaded"""
        return self._num_bytes_downloaded

    def json(self):
        # type: (...) -> Any
        """Returns the whole body as a json object.

        :return: The JSON deserialized response body
        :rtype: any
        :raises json.decoder.JSONDecodeError or ValueError (in python 2.7) if object is not JSON decodable:
        """
        if not self._has_content():
            raise ResponseNotReadError()
        if not self._json:
            self._json = loads(self.text)
        return self._json

    def raise_for_status(self):
        # type: (...) -> None
        """Raises an HttpResponseError if the response has an error status code.

        If response is good, does nothing.
        """
        if self.status_code >= 400:
            raise HttpResponseError(response=self)

    @property
    def content(self):
        # type: (...) -> bytes
        """Return the response's content in bytes."""
        if not self._has_content():
            raise ResponseNotReadError()
        return self._get_content()

    def __repr__(self):
        # type: (...) -> str
        content_type_str = (
            ", Content-Type: {}".format(self.content_type) if self.content_type else ""
        )
        return "<HttpResponse: {} {}{}>".format(
            self.status_code, self.reason, content_type_str
        )

    def _validate_streaming_access(self):
        # type: (...) -> None
        if self.is_stream_consumed:
            raise StreamConsumedError()
        if self.is_closed:
            raise StreamClosedError()

class HttpResponse(_HttpResponseBase):  # pylint: disable=too-many-instance-attributes

    def __enter__(self):
        # type: (...) -> HttpResponse
        return self

    def close(self):
        # type: (...) -> None
        self.is_closed = True
        self.internal_response.close()

    def __exit__(self, *args):
        # type: (...) -> None
        self.close()

    def read(self):
        # type: (...) -> bytes
        """
        Read the response's bytes.

        """
        if not self._has_content():
            self._set_content(b"".join(self.iter_bytes()))
        return self.content

    def _stream_download_helper(self, decompress, chunk_size=None):
        if self.is_stream_consumed:
            raise StreamConsumedError()
        if self.is_closed:
            raise StreamClosedError()

        self.is_stream_consumed = True
        stream_download = self._stream_download_generator(
            pipeline=None,
            response=self,
            chunk_size=chunk_size or self._connection_data_block_size,
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
        if self._has_content():
            if chunk_size is None:
                chunk_size = len(self.content)
            for i in range(0, len(self.content), chunk_size):
                yield self.content[i: i + chunk_size]
        else:
            for part in self._stream_download_helper(decompress=True, chunk_size=chunk_size):
                yield part
        self.close()

    def iter_text(self, chunk_size=None):
        # type: (int) -> Iterator[str]
        """Iterate over the response text
        """
        for byte in self.iter_bytes(chunk_size):
            text = byte.decode(self.encoding or "utf-8")
            yield text

    def iter_lines(self, chunk_size=None):
        # type: (int) -> Iterator[str]
        for text in self.iter_text(chunk_size):
            lines = parse_lines_from_text(text)
            for line in lines:
                yield line

    def _close_stream(self):
        # type: (...) -> None
        self.is_stream_consumed = True
        self.close()
