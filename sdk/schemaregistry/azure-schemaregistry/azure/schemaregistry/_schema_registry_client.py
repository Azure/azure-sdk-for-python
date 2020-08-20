# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, TYPE_CHECKING, Union
from enum import Enum

from ._generated._azure_schema_registry import AzureSchemaRegistry

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
        self._generated_client = AzureSchemaRegistry(credential=credential, endpoint=endpoint, **kwargs)

    def register_schema(self, schema_group, schema_name, serialization_type, schema_string):
        # type: (str, str, str, str) -> str
        """

        :param schema_group:
        :param schema_name:
        :param serialization_type:
        :param schema_string:
        :return:
        """
        schema_id_model = self._generated_client.schema.register(
            group_name=schema_group,
            schema_name=schema_name,
            schema_content=schema_string
        )
        return schema_id_model.id

    def get_schema(self, schema_id):
        # type: (str) -> str
        """

        :param schema_id:
        :return:
        """
        return self._client.schema.get_by_id(schema_id)

    def get_schema_id(self, schema_group, schema_name, serialization_type, schema_string):
        # type: (str, str, str, Union[str, Enum]) -> str
        """

        :param schema_group:
        :param schema_name:
        :param serialization_type:
        :param schema_string:
        :return:
        """
        schema_id_model = self._generated_client.schema.query_id_by_content(
            group_name=schema_group,
            schema_name=schema_name,
            schema_content=schema_string
        )
        return schema_id_model.id
