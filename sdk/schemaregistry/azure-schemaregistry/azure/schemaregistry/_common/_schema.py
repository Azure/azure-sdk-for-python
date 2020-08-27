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


# TODO: Arthur: schema id will be the type of long instead of string


class DictMixin(object):

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        self.__dict__[key] = None

    def __eq__(self, other):
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith('_')})

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return [k for k in self.__dict__ if not k.startswith('_')]

    def values(self):
        return [v for k, v in self.__dict__.items() if not k.startswith('_')]

    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith('_')]

    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class SchemaMeta(DictMixin):
    """
    Id and meta properties of a schema.

    :ivar id: References specific schema in registry namespace.
    :type id: str
    :ivar location: URL location of schema, identified by schema group, schema name, and version.
    :type location: str
    :ivar id_location: URL location of schema, identified by schema ID.  # TODO: JS name is LocationById
    :type id_location: str
    :ivar type: Serialization type for the schema being stored.
    :type type: str
    :ivar version: Version of the returned schema.
    :type version: int
    """
    def __init__(
        self,
        **kwargs
    ):
        # type: (Any) -> None
        self.location = kwargs.get('Location')
        self.id = kwargs.get("X-Schema-Id")
        self.id_location = kwargs.get('X-Schema-Id-Location')
        self.type = kwargs.get('X-Schema-Type')
        self.version = kwargs.get('X-Schema-Version')


class SchemaId(SchemaMeta):  # TODO: need a better name here?
    """
    Id and meta properties of a schema.

    :ivar id: References specific schema in registry namespace.
    :type id: str
    :ivar location: URL location of schema, identified by schema group, schema name, and version.
    :type location: str
    :ivar location_by_id: URL location of schema, identified by schema ID.
    :type location_by_id: str
    :ivar type: Serialization type for the schema being stored.
    :type type: str
    :ivar version: Version of the returned schema.
    :type version: int

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
            :start-after: [START print_schema_id]
            :end-before: [END print_schema_id]
            :language: python
            :dedent: 4
            :caption: SchemaId object.

    """
    def __init__(
        self,
        schema_id,
        **kwargs
    ):
        # type: (str, Any) -> None
        super(SchemaId, self).__init__(**kwargs)
        self.id = schema_id


class Schema(SchemaMeta):
    """
    Id, meta properties and schema content of a schema.

    :ivar content: The content of the schema.
    :type content: str
    :ivar id: References specific schema in registry namespace.
    :type id: str
    :ivar location: URL location of schema, identified by schema group, schema name, and version.
    :type location: str
    :ivar location_by_id: URL location of schema, identified by schema ID.
    :type location_by_id: str
    :ivar type: Serialization type for the schema being stored.
    :type type: str
    :ivar version: Version of the returned schema.
    :type version: int

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
        schema_str,
        **kwargs
    ):
        # type: (str, Any) -> None
        super(Schema, self).__init__(**kwargs)
        self.content = schema_str
