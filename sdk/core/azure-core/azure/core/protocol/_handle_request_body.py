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
from json import dumps
from typing import TYPE_CHECKING, Type
from ..pipeline.transport._base import _format_data
if TYPE_CHECKING:
    from ._types import (
        ContentTypes,
        FileTypes,
        HeaderTypes,
        ByteStream,
    )
    from typing import (
        Any,
        Dict,
        Optional,
        Tuple,
        Union,
    )
    try:
        from multidict import CIMultiDict
        from requests.structures import CaseInsensitiveDict
    except ImportError:
        pass

def _verify_body(
    content,  # type: Optional[ContentTypes]
    json,  # type: Any
    files,  # type: Optional[FileTypes]
    data,  # type: Optional[Dict]
):
    # type: (...) -> None
    types_of_body = [
        content,
        json,
        files,
        data,
    ]
    allowed_combos = [
        set([files, data])  # allowed for multipart
    ]
    set_bodies = [t for t in types_of_body if t]
    if len(set_bodies) > 1 and set(set_bodies) not in allowed_combos:
        raise ValueError(
            "You can only set your request body with one of the following kwargs: "
            "'content', 'json', 'data', or 'files'"
        )

def handle_request_body(
    content,  # type: Optional[ContentTypes]
    json,  # type: Any
    files,  # type: Optional[FileTypes]
    data,  # type: Optional[Dict]
    headers,  # type: Union[CaseInsensitiveDict, CIMultiDict]
):
    # type: (...) -> Any
    """Users can specify the body through 'content', 'json', 'data', or 'files'.
    """
    _verify_body(content, json, files, data)
    if content is not None:
        return handle_request_body_content(content, headers)
    if json is not None:
        return handle_request_body_json(json, headers)
    if files:
        return handle_request_body_multipart(data or {}, files, headers)
    if data:
        return handle_request_body_data(data, headers)
    return None

def handle_request_body_content(content, headers):
    # type: (ContentTypes, Union[CaseInsensitiveDict, CIMultiDict]) -> ContentTypes
    """Content is either str / bytes, or an iterator of str / bytes
    """
    if isinstance(content, (str, bytes)):
        if not headers.get("Content-Length"):
            headers["Content-Length"] = str(len(content))
        return content
    elif not any(
        hasattr(content, attr) for attr in ["read", "__iter__", "__aiter__"]
    ):
        raise TypeError(
            "The `content` kwarg takes in either str / bytes, or an iterator of str / bytes. "
            "The value '{}' you inputted through `content` has type '{}'".format(
                content, type(content)
            )
        )
    return content

def handle_request_body_json(json, headers):
    # type: (Any, Union[CaseInsensitiveDict, CIMultiDict]) -> Any
    """Content is JSON encodable
    """
    try:
        if not headers.get("Content-Type"):
            headers["Content-Type"] = "application/json"
        return dumps(json)
    except TypeError:
        raise TypeError(
            "The value '{}' you gave to `json` is not JSON serializable.".format(
                json
            )
        )

def handle_request_body_multipart(data, files, headers):
    # type: (Dict, FileTypes, Union[CaseInsensitiveDict, CIMultiDict]) -> dict
    """Handle multipart forms here
    """
    return {
        f: _format_data(d) for f, d in data.items() if d is not None
    }

def handle_request_body_data(data, headers):
    # type: (Dict, Union[CaseInsensitiveDict, CIMultiDict]) -> dict
    if not headers.get("Content-Type"):
        headers["Content-Type"] = "application/x-www-form-url-encoded"
    return {
        f: d for f, d in data.items() if d is not None
    }

def set_content_length_header(body, headers):
    # type: (Any, Union[CaseInsensitiveDict, CIMultiDict]) -> None
    """Sets Content-Length header if not set / can be set."""
    try:
        if not headers.get("Content-Length"):
            headers["Content-Length"] = str(len(body))
    except TypeError:
        pass
