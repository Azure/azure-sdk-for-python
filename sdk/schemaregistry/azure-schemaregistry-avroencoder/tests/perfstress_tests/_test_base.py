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
from azure.schemaregistry.encoder.avroencoder import AvroEncoder
from azure.schemaregistry.aio import SchemaRegistryClient as AsyncSchemaRegistryClient
from azure.schemaregistry.encoder.avroencoder.aio import AvroEncoder as AsyncAvroEncoder


class _SchemaRegistryAvroTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        self.fully_qualified_namespace = self.get_from_env(
            "SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE"
        )
        self.group_name = self.get_from_env("SCHEMAREGISTRY_GROUP")
        self.definition, num_fields = self._create_schema_definition()
        self.content = self._create_content(num_fields)

    def _create_schema_definition(self):
        schema_size = self.args.schema_size

        # random string to avoid conflicting requests
        letters = string.ascii_lowercase
        randletters = ''.join(random.choice(letters) for i in range(10))

        fields = []
        schema = {
            "type": "record",
            "name": f"example.User{randletters}",
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
        return definition, num_fields

    def _create_content(self, num_fields):
        content = {"favor_number00000": 0}
        for i in range(1, num_fields):
            num_idx = f"{i:05d}"
            content[f"favo_number{num_idx}"] = i
        return content

    @staticmethod
    def add_arguments(parser):
        super(_SchemaRegistryAvroTest, _SchemaRegistryAvroTest).add_arguments(parser)
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


class _EncodeTest(_SchemaRegistryAvroTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.sync_credential = DefaultAzureCredential()
        self.sync_client = SchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.sync_credential,
        )
        self.sync_encoder = AvroEncoder(
            client=self.sync_client, group_name=self.group_name, auto_register_schemas=True
        )
        self.async_credential = AsyncDefaultAzureCredential()
        self.async_client = AsyncSchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.async_credential,
        )
        self.async_encoder = AsyncAvroEncoder(
            client=self.async_client, group_name=self.group_name, auto_register_schemas=True
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


class _DecodeTest(_SchemaRegistryAvroTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.sync_credential = DefaultAzureCredential()
        self.sync_client = SchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.sync_credential,
        )
        self.sync_encoder = AvroEncoder(
            client=self.sync_client, group_name=self.group_name, auto_register_schemas=True
        )
        self.async_credential = AsyncDefaultAzureCredential()
        self.async_client = AsyncSchemaRegistryClient(
            fully_qualified_namespace=self.fully_qualified_namespace,
            credential=self.async_credential,
        )
        self.async_encoder = AsyncAvroEncoder(
            client=self.async_client, group_name=self.group_name, auto_register_schemas=True
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
