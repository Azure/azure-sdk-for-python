# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, TYPE_CHECKING, Union
from enum import Enum

from .._common._response_handlers import _parse_response_schema_id, _parse_response_schema
from .._common._schema import SchemaId, Schema
from .._generated.aio._azure_schema_registry_async import AzureSchemaRegistry

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class SchemaRegistryClient:
    """
    SchemaRegistryClient is as a central schema repository for enterprise-level data infrastructure,
    complete with support for versioning and management.

    :param str endpoint: The Schema Registry service endpoint, for example my-namespace.servicebus.windows.net.
    :param credential: To authenticate to manage the entities of the SchemaRegistry namespace.
    :type credential: TokenCredential

    """
    def __init__(
        self,
        endpoint: str,
        credential: "AsyncTokenCredential",
        **kwargs: Any
    ) -> None:
        self._generated_client = AzureSchemaRegistry(credential, endpoint, **kwargs)

    async def __aenter__(self):
        await self._generated_client.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self._generated_client.__aexit__(*args)

    async def close(self):
        """ This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        await self._generated_client.close()

    async def register_schema(
        self,
        schema_group: str,
        schema_name: str,
        serialization_type: Union[str, Enum],
        schema_string: str
    ) -> SchemaId:
        """
        Register new schema. If schema of specified name does not exist in specified group,
        schema is created at version 1. If schema of specified name exists already in specified group,
        schema is created at latest version + 1.

        :param str schema_group: Schema group under which schema should be registered.
        :param str schema_name: Name of schema being registered.
        :param serialization_type: Serialization type for the schema being registered.
        :type serialization_type: Union[str, Enum]
        :param str schema_string: String representation of the schema being registered.
        :rtype: SchemaId
        """
        return await self._generated_client.schema.register(
            group_name=schema_group,
            schema_name=schema_name,
            schema_content=schema_string,
            # serialization_type=serialization_type,  # TODO: current swagger doesn't support the parameter
            cls=_parse_response_schema_id,
        )

    async def get_schema(
        self,
        schema_id: str
    ) -> Schema:
        """
        Gets a registered schema by its unique ID.
        Azure Schema Registry guarantees that ID is unique within a namespace.

        :param str schema_id: References specific schema in registry namespace.
        :rtype: Schema
        """
        return await self._generated_client.schema.get_by_id(
            schema_id=schema_id,
            cls=_parse_response_schema
        )

    async def get_schema_id(
        self,
        schema_group: str,
        schema_name: str,
        serialization_type: Union[str, Enum],
        schema_string: str
    ) -> str:
        """
        Gets the ID referencing an existing schema within the specified schema group,
        as matched by schema content comparison.

        :param str schema_group: Schema group under which schema should be registered.
        :param str schema_name: Name of schema being registered.
        :param serialization_type: Serialization type for the schema being registered.
        :type serialization_type: Union[str, Enum]
        :param str schema_string: String representation of the schema being registered.
        :rtype: SchemaId
        """
        return await self._generated_client.schema.query_id_by_content(
            group_name=schema_group,
            schema_name=schema_name,
            schema_content=schema_string,
            # serialization_type=serialization_type,  # TODO: current swagger doesn't support the parameter
            cls=_parse_response_schema_id
        )
