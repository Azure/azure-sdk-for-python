# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import math
import random, string
import sys

from azure_devtools.perfstress_tests import PerfStressTest
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonschemaencoder import JsonSchemaEncoder
from azure.schemaregistry.aio import SchemaRegistryClient as AsyncSchemaRegistryClient
from azure.schemaregistry.encoder.jsonschemaencoder.aio import JsonSchemaEncoder as AsyncJsonSchemaEncoder


class _SchemaRegistryJsonTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        self.fully_qualified_namespace = self.get_from_env(
            "SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE"
        )
        self.group_name = self.get_from_env("SCHEMAREGISTRY_GROUP")
        self.definition, num_properties = self._create_schema_definition()
        self.content = self._create_content(num_properties)

    def _create_schema_definition(self):
        schema_size = self.args.schema_size

        # random string to avoid conflicting requests
        letters = string.ascii_lowercase
        randletters = ''.join(random.choice(letters) for i in range(10))

        properties = {}
        schema = {
            "$id": "https://example.com/person.schema.json",
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "Person",
            "type": "object",
            "properties": properties
        }

        # TODO: x bytes
        schema_no_properties_size = sys.getsizeof(json.dumps(schema, separators=(",", ":")))
        properties["favor_number00000"] = {"type": "integer"}
        # TODO: each additional property is y bytes
        schema_one_property_size = sys.getsizeof(json.dumps(schema, separators=(",", ":")))
        property_size = schema_one_property_size - schema_no_properties_size

        # calculate number of properties to add to get args.schema_size rounded down to nearest multiple
        num_properties = math.floor((schema_size - schema_no_properties_size) / property_size)

        for i in range(1, num_properties):
            num_idx = f"{i:05d}"
            properties[f"favo_number{num_idx}"] = {"type": "integer"}
        definition = json.dumps(schema, separators=(",", ":"))
        return definition, num_properties

    def _create_content(self, num_properties):
        content = {"favor_number00000": 0}
        for i in range(1, num_properties):
            num_idx = f"{i:05d}"
            content[f"favo_number{num_idx}"] = i
        return content

    @staticmethod
    def add_arguments(parser):
        super(_SchemaRegistryJsonTest, _SchemaRegistryJsonTest).add_arguments(parser)
        parser.add_argument(
            "--schema-size",
            nargs="?",
            type=int,
            help="Size of a single schema. Max 1000000 bytes. Defaults to 150 bytes",
            default=150,
        )
        parser.add_argument(
            "--num-values",
            nargs="?",
            type=int,
            help="Number of values to encode/decode with given schema. Default is 1.",
            default=1,
        )


class _EncodeTest(_SchemaRegistryJsonTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.sync_credential = DefaultAzureCredential()
        self.sync_client = SchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.sync_credential,
        )
        self.sync_encoder = JsonSchemaEncoder(
            client=self.sync_client, group_name=self.group_name, auto_register=True
        )
        self.async_credential = AsyncDefaultAzureCredential()
        self.async_client = AsyncSchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.async_credential,
        )
        self.async_encoder = AsyncJsonSchemaEncoder(
            client=self.async_client, group_name=self.group_name, auto_register=True
        )

    async def global_setup(self):
        await super().global_setup()

    async def close(self):
        self.sync_client.close()
        self.sync_credential.close()
        self.sync_encoder.close()
        await self.async_client.close()
        await self.async_credential.close()
        await self.async_encoder.close()
        await super().close()


class _DecodeTest(_SchemaRegistryJsonTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.sync_credential = DefaultAzureCredential()
        self.sync_client = SchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.sync_credential,
        )
        self.sync_encoder = JsonSchemaEncoder(
            client=self.sync_client, group_name=self.group_name, auto_register=True
        )
        self.async_credential = AsyncDefaultAzureCredential()
        self.async_client = AsyncSchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.async_credential,
        )
        self.async_encoder = AsyncJsonSchemaEncoder(
            client=self.async_client, group_name=self.group_name, auto_register=True
        )
        self.encoded_content = self._encode_content()

    def _encode_content(self):
        with self.sync_encoder as encoder:
            return encoder.encode(self.content, schema=self.definition)

    async def global_setup(self):
        await super().global_setup()

    async def close(self):
        self.sync_client.close()
        self.sync_credential.close()
        self.sync_encoder.close()
        await self.async_client.close()
        await self.async_credential.close()
        await self.async_encoder.close()
        await super().close()
