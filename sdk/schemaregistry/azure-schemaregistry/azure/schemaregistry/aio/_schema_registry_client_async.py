# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, TYPE_CHECKING, Union
from enum import Enum

from .._generated.aio._azure_schema_registry_async import AzureSchemaRegistry

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class SchemaRegistryClient:
    """

    """
    def __init__(
        self,
        endpoint: str,
        credential: AsyncTokenCredential,
        **kwargs: Any
    ) -> None:
        self._generated_client = AzureSchemaRegistry(credential, endpoint, **kwargs)

    async def register_schema(
        self,
        schema_group: str,
        schema_name: str,
        serialization_type: str,
        schema_string: str
    ) -> str:
        """

        :param schema_group:
        :param schema_name:
        :param serialization_type:
        :param schema_string:
        :return:
        """
        schema_id_model = await self._generated_client.schema.register(
            group_name=schema_group,
            schema_name=schema_name,
            schema_content=schema_string
        )
        return schema_id_model.id

    async def get_schema(
        self,
        schema_id: str
    ) -> str:
        """

        :param schema_id:
        :return:
        """
        return await self._generated_client.schema.get_by_id(schema_id=schema_id)

    async def get_schema_id(
        self,
        schema_group: str,
        schema_name: str,
        serialization_type: Union[str, Enum],
        schema_string: str
    ) -> str:
        """

        :param schema_group:
        :param schema_name:
        :param serialization_type:
        :param schema_string:
        :return:
        """
        schema_id_model = await self._generated_client.schema.query_id_by_content(
            group_name=schema_group,
            schema_name=schema_name,
            schema_content=schema_string
        )
        return schema_id_model.id
