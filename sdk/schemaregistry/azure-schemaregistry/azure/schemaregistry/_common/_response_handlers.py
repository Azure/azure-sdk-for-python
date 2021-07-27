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
from typing import Any, Dict

from azure.core.pipeline import PipelineResponse

#from .._generated.models import SchemaId as InternalSchemaId
from ._schema import SchemaProperties, Schema


def _parse_response_schema_id(pipeline_response, deserialized, response_headers):  # pylint: disable=unused-argument
    # type: (PipelineResponse, InternalSchemaId, Dict[str, Any]) -> SchemaProperties
    """

    :param pipeline_response:
    :param deserialized:
    :param response_headers:
    :return:
    """
    return SchemaProperties(schema_id=deserialized.id, **response_headers)


def _parse_response_schema(pipeline_response, deserialized, response_headers):  # pylint: disable=unused-argument
    # type: (PipelineResponse, str, Dict[str, Any]) -> Schema
    """

    :param pipeline_response:
    :param deserialized:
    :param response_headers:
    :return:
    """

    return Schema(schema_content=deserialized, schema_properties=SchemaProperties(**response_headers))
