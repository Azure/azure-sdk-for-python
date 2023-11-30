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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._constants import SchemaFormat


class SchemaProperties(object):
    """
    Meta properties of a schema.

    :keyword id: References specific schema in registry namespace.
    :paramtype id: str
    :keyword format: Format for the schema being stored.
    :paramtype format: ~azure.schemaregistry.SchemaFormat
    :keyword group_name: Schema group under which schema is stored.
    :paramtype group_name: str
    :keyword name: Name of schema.
    :paramtype name: str
    :keyword version: Version of schema.
    :paramtype version: int

    :ivar id: References specific schema in registry namespace.
    :vartype id: str
    :ivar format: Format for the schema being stored.
    :vartype format: ~azure.schemaregistry.SchemaFormat
    :ivar group_name: Schema group under which schema is stored.
    :vartype group_name: str
    :ivar name: Name of schema.
    :vartype name: str
    :ivar version: Version of schema.
    :vartype version: int
    """

    def __init__(
        self,
        *,
        id: str,    # pylint: disable=redefined-builtin
        format: "SchemaFormat", # pylint: disable=redefined-builtin
        group_name: str,
        name: str,
        version: int,
    ) -> None:
        self.id = id
        self.format = format
        self.group_name = group_name
        self.name = name
        self.version = version

    def __repr__(self) -> str:
        return (
            f"SchemaProperties(id={self.id}, format={self.format}, "
            f"group_name={self.group_name}, name={self.name}, version={self.version})"[
                :1024
            ]
        )


class Schema(object):
    """
    The schema content of a schema, along with id and meta properties.

    :keyword definition: The content of the schema.
    :paramtype definition: str
    :keyword properties: The properties of the schema.
    :paramtype properties: SchemaProperties

    :ivar definition: The content of the schema.
    :vartype definition: str
    :ivar properties: The properties of the schema.
    :vartype properties: SchemaProperties
    """

    def __init__(
        self,
        definition: str,
        properties: "SchemaProperties",
    ) -> None:
        self.definition = definition
        self.properties = properties

    def __repr__(self) -> str:
        return f"Schema(definition={self.definition}, properties={self.properties})"[:1024]
