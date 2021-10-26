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
try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache
from io import BytesIO
from typing import Any, Dict, Mapping

from ._constants import SCHEMA_ID_START_INDEX, SCHEMA_ID_LENGTH, DATA_START_INDEX
from ._utils import parse_schema
from azure.core.messaging import MessageWithMetadata


class AvroEncoder(object):
    """
    AvroEncoder provides the ability to serialize and deserialize data according
    to the given avro schema. It would automatically register, get and cache the schema.

    :keyword client: Required. The schema registry client
     which is used to register schema and retrieve schema from the service.
    :paramtype client: ~azure.schemaregistry.SchemaRegistryClient
    :keyword str group_name: Required. Schema group under which schema should be registered.
    :keyword bool auto_register_schemas: When true, register new schemas passed to serialize.
     Otherwise, and by default, serialization will fail if the schema has not been pre-registered in the registry.

    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        try:
            self._schema_group = kwargs.pop("group_name")
            self._schema_registry_client = kwargs.pop("client") # type: "SchemaRegistryClient"
        except KeyError as e:
            raise TypeError("'{}' is a required keyword.".format(e.args[0]))
        self._auto_register_schemas = kwargs.get("auto_register_schemas", False)

    def __enter__(self):
        # type: () -> SchemaRegistryAvroEncoder
        self._schema_registry_client.__enter__()
        return self

    def __exit__(self, *exc_details):
        # type: (Any) -> None
        self._schema_registry_client.__exit__(*exc_details)

    def close(self):
        # type: () -> None
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._schema_registry_client.close()

    def encode_body(self, value, **kwargs):
        # type: (Any, Any) -> bytes
        """
        Encode data with the given schema.

        :param value: The data to be encoded.
        :type value: Any
        :keyword schema: The schema used to encode the data.
        :paramtype schema: str
        :rtype: MessageWithMetadata
        """
        pass

    def decode_body(self, message, **kwargs):
        # type: (MessageWithMetadata, Any) -> Any
        """
        Decode bytes data.

        :param bytes value: The bytes data needs to be decoded.
        :rtype: Any
        """
        pass
