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
    :vartype id: str
    :ivar format: Format for the schema being stored.
    :vartype format: ~azure.schemaregistry.SchemaFormat
    :ivar group_name: Schema group under which schema is stored.
    :vartype group_name: str
    :ivar name: Name of schema.
    :vartype name: str
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.id = kwargs.pop("id")
        self.format = kwargs.pop("format")
        self.group_name = kwargs.pop("group_name")
        self.name = kwargs.pop("name")

    def __repr__(self):
        return (
            f"SchemaProperties(id={self.id}, format={self.format}, "
            f"group_name={self.group_name}, name={self.name})"[:1024]
        )


class Schema(object):
    """
    The schema content of a schema, along with id and meta properties.

    :ivar definition: The content of the schema.
    :vartype definition: str
    :ivar properties: The properties of the schema.
    :vartype properties: SchemaProperties
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        self.definition = kwargs.pop("definition")
        self.properties = kwargs.pop("properties")

    def __repr__(self):
        return "Schema(definition={}, properties={})".format(
            self.definition, self.properties
        )[:1024]
