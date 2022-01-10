# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import math
import sys

from azure_devtools.perfstress_tests import PerfStressTest
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.aio import SchemaRegistryClient as AsyncSchemaRegistryClient


class _SchemaRegistryTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        self.fully_qualified_namespace = self.get_from_env(
            "SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE"
        )
        self.group_name = self.get_from_env("SCHEMAREGISTRY_GROUP")
        self.name = "your-schema-name"
        self.format = "Avro"
        self.definition = self._create_schema_definition()

    def _create_schema_definition(self):
        schema_size = self.args.schema_size

        fields = []
        schema = {
            "type": "record",
            "name": "example.User",
            "fields": fields,
        }

        # 100 bytes
        schema_no_fields_size = sys.getsizeof(json.dumps(schema, separators=(",", ":")))
        fields.append({"name": "favor_number00000", "type": ["int", "null"]})
        # each additional field is 50 bytes
        schema_one_field_size = sys.getsizeof(json.dumps(schema, separators=(",", ":")))
        field_size = schema_one_field_size - schema_no_fields_size

        # calculate number of fields to add to get args.schema_size rounded down to nearest 50 multiple
        num_fields = math.floor((schema_size - schema_no_fields_size) / field_size)

        for i in range(1, num_fields):
            num_idx = f"{i:05d}"
            fields.append(
                {"name": f"favo_number{num_idx}", "type": ["int", "null"]},
            )
        definition = json.dumps(schema, separators=(",", ":"))
        return definition

    @staticmethod
    def add_arguments(parser):
        super(_SchemaRegistryTest, _SchemaRegistryTest).add_arguments(parser)
        parser.add_argument(
            "--schema-size",
            nargs="?",
            type=int,
            help="Size of a single schema. Max 1000000 bytes. Defaults to 150 bytes",
            default=150,
        )
        parser.add_argument(
            "--num-schemas",
            nargs="?",
            type=int,
            help="""Number of schemas to register/get by ID/get properties for. Default is 10.
                May result in 'Forbidden' Exception for `RegisterSchemaTest` operation, if reached
                the limit of schemas allowed for Schema Registry tier.""",
            default=10,
        )


class _RegisterTest(_SchemaRegistryTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.sync_credential = DefaultAzureCredential()
        self.sync_client = SchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.sync_credential,
        )
        self.async_credential = AsyncDefaultAzureCredential()
        self.async_client = AsyncSchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.async_credential,
        )

    async def global_setup(self):
        await super().global_setup()

    async def close(self):
        self.sync_client.close()
        self.sync_credential.close()
        await self.async_client.close()
        await self.async_credential.close()
        await super().close()


class _GetSchemaTest(_SchemaRegistryTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.sync_credential = DefaultAzureCredential()
        self.sync_client = SchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.sync_credential,
        )
        self.async_credential = AsyncDefaultAzureCredential()
        self.async_client = AsyncSchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.async_credential,
        )
        self.schema_id = self._preregister_schema()

    def _preregister_schema(self):
        with self.sync_client as client:
            schema_properties = client.register_schema(
                self.group_name, self.name, self.definition, self.format
            )
            return schema_properties.id

    async def global_setup(self):
        await super().global_setup()

    async def close(self):
        self.sync_client.close()
        self.sync_credential.close()
        await self.async_client.close()
        await self.async_credential.close()
        await super().close()
