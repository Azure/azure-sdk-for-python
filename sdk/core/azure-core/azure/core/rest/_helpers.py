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
import codecs
import cgi
from json import dumps
try:
    import collections.abc as collections
except ImportError:
    import collections  # type: ignore
from typing import (
    Optional,
    Union,
    Mapping,
    Sequence,
    Tuple,
    IO,
    Any,
    Dict,
    Iterable,
    MutableMapping,
)
import xml.etree.ElementTree as ET
import six
try:
    binary_type = str
    from urlparse import urlparse  # type: ignore
except ImportError:
    binary_type = bytes  # type: ignore
    from urllib.parse import urlparse
from azure.core.serialization import AzureJSONEncoder
from ..utils._pipeline_transport_rest_shared import (
    _format_parameters_helper,
    _pad_attr_name,
    _prepare_multipart_body_helper,
    _serialize_request,
    _format_data_helper,
)

################################### TYPES SECTION #########################

PrimitiveData = Optional[Union[str, int, float, bool]]


ParamsType = Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]]

FileContent = Union[str, bytes, IO[str], IO[bytes]]
FileType = Union[
    Tuple[Optional[str], FileContent],
]

FilesType = Union[
    Mapping[str, FileType],
    Sequence[Tuple[str, FileType]]
]

ContentTypeBase = Union[str, bytes, Iterable[bytes]]

########################### HELPER SECTION #################################

def _verify_data_object(name, value):
    if not isinstance(name, str):
        raise TypeError(
            "Invalid type for data name. Expected str, got {}: {}".format(
                type(name), name
            )
        )
    if value is not None and not isinstance(value, (str, bytes, int, float)):
        raise TypeError(
            "Invalid type for data value. Expected primitive type, got {}: {}".format(
                type(name), name
            )
        )

def set_urlencoded_body(data, has_files):
    body = {}
    default_headers = {}
    for f, d in data.items():
        if not d:
            continue
        if isinstance(d, list):
            for item in d:
                _verify_data_object(f, item)
        else:
            _verify_data_object(f, d)
        body[f] = d
    if not has_files:
        # little hacky, but for files we don't send a content type with
        # boundary so requests / aiohttp etc deal with it
        default_headers["Content-Type"] = "application/x-www-form-urlencoded"
    return default_headers, body

def set_multipart_body(files):
    formatted_files = {
        f: _format_data_helper(d) for f, d in files.items() if d is not None
    }
    return {}, formatted_files

def set_xml_body(content):
    headers = {}
    bytes_content = ET.tostring(content, encoding="utf8")
    body = bytes_content.replace(b"encoding='utf8'", b"encoding='utf-8'")
    if body:
        headers["Content-Length"] = str(len(body))
    return headers, body

def _shared_set_content_body(content):
    # type: (Any) -> Tuple[MutableMapping[str, str], Optional[ContentTypeBase]]
    headers = {}  # type: MutableMapping[str, str]

    if isinstance(content, ET.Element):
        # XML body
        return set_xml_body(content)
    if isinstance(content, (str, bytes)):
        headers = {}
        body = content
        if isinstance(content, six.string_types):
            headers["Content-Type"] = "text/plain"
        if body:
            headers["Content-Length"] = str(len(body))
        return headers, body
    if isinstance(content, collections.Iterable):
        return {}, content
    return headers, None

def set_content_body(content):
    headers, body = _shared_set_content_body(content)
    if body is not None:
        return headers, body
    raise TypeError(
        "Unexpected type for 'content': '{}'. ".format(type(content)) +
        "We expect 'content' to either be str, bytes, or an Iterable"
    )

def set_json_body(json):
    # type: (Any) -> Tuple[Dict[str, str], Any]
    body = dumps(json, cls=AzureJSONEncoder)
    return {
        "Content-Type": "application/json",
        "Content-Length": str(len(body))
    }, body

def lookup_encoding(encoding):
    # type: (str) -> bool
    # including check for whether encoding is known taken from httpx
    try:
        codecs.lookup(encoding)
        return True
    except LookupError:
        return False

def get_charset_encoding(response):
    # type: (...) -> Optional[str]
    content_type = response.headers.get("Content-Type")

    if not content_type:
        return None
    _, params = cgi.parse_header(content_type)
    encoding = params.get('charset') # -> utf-8
    if encoding is None or not lookup_encoding(encoding):
        return None
    return encoding

def decode_to_text(encoding, content):
    # type: (Optional[str], bytes) -> str
    if not content:
        return ""
    if encoding == "utf-8":
        encoding = "utf-8-sig"
    if encoding:
        return content.decode(encoding)
    return codecs.getincrementaldecoder("utf-8-sig")(errors="replace").decode(content)

class HttpRequestBackcompatMixin(object):

    def __getattr__(self, attr):
        backcompat_attrs = [
            "files",
            "data",
            "multipart_mixed_info",
            "query",
            "body",
            "format_parameters",
            "set_streamed_data_body",
            "set_text_body",
            "set_xml_body",
            "set_json_body",
            "set_formdata_body",
            "set_bytes_body",
            "set_multipart_mixed",
            "prepare_multipart_body",
            "serialize",
        ]
        attr = _pad_attr_name(attr, backcompat_attrs)
        return self.__getattribute__(attr)

    def __setattr__(self, attr, value):
        backcompat_attrs = [
            "multipart_mixed_info",
            "files",
            "data",
            "body",
        ]
        attr = _pad_attr_name(attr, backcompat_attrs)
        super(HttpRequestBackcompatMixin, self).__setattr__(attr, value)

    @property
    def _multipart_mixed_info(self):
        """DEPRECATED: Information used to make multipart mixed requests.
        This is deprecated and will be removed in a later release.
        """
        try:
            return self._multipart_mixed_info_val
        except AttributeError:
            return None

    @_multipart_mixed_info.setter
    def _multipart_mixed_info(self, val):
        """DEPRECATED: Set information to make multipart mixed requests.
        This is deprecated and will be removed in a later release.
        """
        self._multipart_mixed_info_val = val

    @property
    def _query(self):
        """DEPRECATED: Query parameters passed in by user
        This is deprecated and will be removed in a later release.
        """
        query = urlparse(self.url).query
        if query:
            return {p[0]: p[-1] for p in [p.partition("=") for p in query.split("&")]}
        return {}

    @property
    def _body(self):
        """DEPRECATED: Body of the request. You should use the `content` property instead
        This is deprecated and will be removed in a later release.
        """
        return self._data

    @_body.setter
    def _body(self, val):
        """DEPRECATED: Set the body of the request
        This is deprecated and will be removed in a later release.
        """
        self._data = val

    def _format_parameters(self, params):
        """DEPRECATED: Format the query parameters
        This is deprecated and will be removed in a later release.
        You should pass the query parameters through the kwarg `params`
        instead.
        """
        return _format_parameters_helper(self, params)

    def _set_streamed_data_body(self, data):
        """DEPRECATED: Set the streamed request body.
        This is deprecated and will be removed in a later release.
        You should pass your stream content through the `content` kwarg instead
        """
        if not isinstance(data, binary_type) and not any(
            hasattr(data, attr) for attr in ["read", "__iter__", "__aiter__"]
        ):
            raise TypeError(
                "A streamable data source must be an open file-like object or iterable."
            )
        headers = self._set_body(content=data)
        self._files = None
        self.headers.update(headers)

    def _set_text_body(self, data):
        """DEPRECATED: Set the text body
        This is deprecated and will be removed in a later release.
        You should pass your text content through the `content` kwarg instead
        """
        headers = self._set_body(content=data)
        self.headers.update(headers)
        self._files = None

    def _set_xml_body(self, data):
        """DEPRECATED: Set the xml body.
        This is deprecated and will be removed in a later release.
        You should pass your xml content through the `content` kwarg instead
        """
        headers = self._set_body(content=data)
        self.headers.update(headers)
        self._files = None

    def _set_json_body(self, data):
        """DEPRECATED: Set the json request body.
        This is deprecated and will be removed in a later release.
        You should pass your json content through the `json` kwarg instead
        """
        headers = self._set_body(json=data)
        self.headers.update(headers)
        self._files = None

    def _set_formdata_body(self, data=None):
        """DEPRECATED: Set the formrequest body.
        This is deprecated and will be removed in a later release.
        You should pass your stream content through the `files` kwarg instead
        """
        if data is None:
            data = {}
        content_type = self.headers.pop("Content-Type", None) if self.headers else None

        if content_type and content_type.lower() == "application/x-www-form-urlencoded":
            headers = self._set_body(data=data)
            self._files = None
        else:  # Assume "multipart/form-data"
            headers = self._set_body(files=data)
            self._data = None
        self.headers.update(headers)

    def _set_bytes_body(self, data):
        """DEPRECATED: Set the bytes request body.
        This is deprecated and will be removed in a later release.
        You should pass your bytes content through the `content` kwarg instead
        """
        headers = self._set_body(content=data)
        # we don't want default Content-Type
        # in 2.7, byte strings are still strings, so they get set with text/plain content type

        headers.pop("Content-Type", None)
        self.headers.update(headers)
        self._files = None

    def _set_multipart_mixed(self, *requests, **kwargs):
        """DEPRECATED: Set the multipart mixed info.
        This is deprecated and will be removed in a later release.
        """
        self.multipart_mixed_info = (
            requests,
            kwargs.pop("policies", []),
            kwargs.pop("boundary", None),
            kwargs
        )

    def _prepare_multipart_body(self, content_index=0):
        """DEPRECATED: Prepare your request body for multipart requests.
        This is deprecated and will be removed in a later release.
        """
        return _prepare_multipart_body_helper(self, content_index)

    def _serialize(self):
        """DEPRECATED: Serialize this request using application/http spec.
        This is deprecated and will be removed in a later release.
        :rtype: bytes
        """
        return _serialize_request(self)

    def _add_backcompat_properties(self, request, memo):
        """While deepcopying, we also need to add the private backcompat attrs"""
        request._multipart_mixed_info = copy.deepcopy(self._multipart_mixed_info, memo)  # pylint: disable=protected-access
