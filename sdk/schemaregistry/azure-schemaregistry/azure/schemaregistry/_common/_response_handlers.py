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
from typing import (
    cast,
    Tuple,
    Mapping,
    Dict,
    TYPE_CHECKING,
    Iterator,
    AsyncIterator,
    Union,
)
from ._constants import SchemaFormat

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineResponse
    from azure.core.rest import HttpResponse, AsyncHttpResponse


def _parse_schema_properties_dict(
    response_headers: Mapping[str, Union[str, int]]
) -> Dict[str, Union[str, int]]:
    return {
        "id": response_headers["Schema-Id"],
        "group_name": response_headers["Schema-Group-Name"],
        "name": response_headers["Schema-Name"],
        "version": int(response_headers["Schema-Version"]),
    }


def _get_format(content_type: str) -> SchemaFormat:
    # pylint:disable=redefined-builtin
    try:
        format = content_type.split("serialization=")[1]
        try:
            return SchemaFormat(format)
        except ValueError:
            return SchemaFormat(format.capitalize())
    except IndexError:
        if 'protobuf' in content_type:
            return SchemaFormat.PROTOBUF
        return SchemaFormat.CUSTOM


def prepare_schema_properties_result(  # pylint:disable=unused-argument,redefined-builtin
    format: str,
    pipeline_response: "PipelineResponse",
    deserialized: Union[Iterator[bytes], AsyncIterator[bytes]],
    response_headers: Mapping[str, Union[str, int]],
) -> Dict[str, Union[str, int]]:
    properties_dict = _parse_schema_properties_dict(response_headers)
    properties_dict["format"] = SchemaFormat(format)
    pipeline_response.http_response.raise_for_status()
    return properties_dict


def prepare_schema_result(  # pylint:disable=unused-argument
    pipeline_response: "PipelineResponse",
    deserialized: Union[Iterator[bytes], AsyncIterator[bytes]],
    response_headers: Mapping[str, Union[str, int]],
) -> Tuple[Union["HttpResponse", "AsyncHttpResponse"], Dict[str, Union[int, str]]]:
    properties_dict = _parse_schema_properties_dict(response_headers)
    properties_dict["format"] = _get_format(
        cast(str, response_headers.get("Content-Type"))
    )
    pipeline_response.http_response.raise_for_status()
    return pipeline_response.http_response, properties_dict
