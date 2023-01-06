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
from ._schema import SchemaProperties, Schema
from ._constants import SchemaFormat


def _parse_schema_properties_dict(response):
    return {
        "id": response.headers.get("schema-id"),
        "group_name": response.headers.get("schema-group-name"),
        "name": response.headers.get("schema-name"),
        "version": int(response.headers.get("schema-version"))
    }


def _parse_response_schema_properties(response, format):
    # pylint:disable=redefined-builtin
    properties_dict = _parse_schema_properties_dict(response)
    properties_dict["format"] = SchemaFormat(format)
    return SchemaProperties(**properties_dict)

def _get_format(content_type: str) -> SchemaFormat:
    # pylint:disable=redefined-builtin
    try:
        format = content_type.split("serialization=")[1]
        try:
            format = SchemaFormat(format)
        except ValueError:
            format = SchemaFormat(format.capitalize())
    except IndexError:
        format = SchemaFormat.CUSTOM
    return format

def _parse_response_schema(response):
    schema_props_dict = _parse_schema_properties_dict(response)
    schema_props_dict["format"] = _get_format(response.headers.get("content-type"))

    return Schema(
        definition=response.text(), properties=SchemaProperties(**schema_props_dict)
    )
