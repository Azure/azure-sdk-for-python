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
from typing import Any


class SchemaProperties(object):
    """
    Meta properties of a schema.

    :ivar id: References specific schema in registry namespace.
    :type id: str
    :ivar format: Format for the schema being stored.
    :type format: str
    :ivar version: Version of the returned schema.
    :type version: int

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
            :start-after: [START print_schema_properties]
            :end-before: [END print_schema_properties]
            :language: python
            :dedent: 4
            :caption: SchemaProperties object.

    """

    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        self.id = kwargs.pop('id')
        self.format = kwargs.pop('format')
        self.version = kwargs.pop('version')


class Schema(object):
    """
    The schema content of a schema, along with id and meta properties.

    :ivar schema_definition: The content of the schema.
    :type schema_definition: str
    :ivar properties: The properties of the schema.
    :type properties: SchemaProperties

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
            :start-after: [START print_schema]
            :end-before: [END print_schema]
            :language: python
            :dedent: 4
            :caption: Schema object.

    """

    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        self.schema_definition = kwargs.pop("schema_definition")
        self.properties = kwargs.pop("properties")
