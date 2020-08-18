# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, TYPE_CHECKING

from ._generated._azure_schema_registry import AzureSchemaRegistry
from ._common._schema import Schema

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class SchemaRegistryClient:
    """

    """
    def __init__(
        self,
        endpoint,
        credential,
        **kwargs
    ):
        # type: (str, TokenCredential, Any) -> None
        self._client = AzureSchemaRegistry(credential=credential, endpoint=endpoint)

    def register_schema(self, schema_group, schema_name, serialization_type, schema_string):
        # type: (str, str, str, str) -> Schema
        """

        :param schema_group:
        :param schema_name:
        :param serialization_type:
        :param schema_string:
        :return:
        """
        res = self._client.schema.register(schema_group, schema_name, schema_string)
        return res

    def get_schema(self, schema_id):
        # type: (str) -> Schema
        """

        :param schema_id:
        :return:
        """
        return self._client.schema.get_by_id(schema_id)

    def get_schema_id(self, schema_group, schema_name, serialization_type, schema_string):  # TODO: all should match?
        # type: (str, str, str, Union[str, Enum]) -> str
        """

        :param schema_group:
        :param schema_name:
        :param serialization_type:
        :param schema_string:
        :return:
        """
        return self._client.schema.get_id_by_content(schema_group, schema_name, serialization_type, schema_string)
