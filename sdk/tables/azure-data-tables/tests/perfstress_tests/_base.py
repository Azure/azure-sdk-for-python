# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import uuid
from datetime import timezone, datetime
import string
import random

from devtools_testutils.perfstress_tests import PerfStressTest

from azure.data.tables import EdmType, EntityProperty
from azure.data.tables import TableServiceClient as SyncTableServiceClient
from azure.data.tables.aio import TableServiceClient as AsyncTableServiceClient


_LETTERS = string.ascii_letters

_FULL_EDM_ENTITY = {
    "PartitionKey": "",
    "RowKey": "",
    "StringTypeProperty": "StringTypeProperty",
    "DatetimeTypeProperty": datetime(1970, 10, 4, tzinfo=timezone.utc),
    "GuidTypeProperty": uuid.UUID("c9da6455-213d-42c9-9a79-3e9149a57833"),
    "BinaryTypeProperty": b"BinaryTypeProperty",
    "Int64TypeProperty": EntityProperty(2 ^ 32 + 1, EdmType.INT64),
    "DoubleTypeProperty": 200.23,
    "IntTypeProperty": 5,
}

_STRING_ENTITY = {
    "PartitionKey": "",
    "RowKey": "",
    "StringTypeProperty1": "StringTypeProperty",
    "StringTypeProperty2": "1970-10-04T00:00:00+00:00",
    "StringTypeProperty3": "c9da6455-213d-42c9-9a79-3e9149a57833",
    "StringTypeProperty4": "BinaryTypeProperty",
    "StringTypeProperty5": str(2 ^ 32 + 1),
    "StringTypeProperty6": "200.23",
    "StringTypeProperty7": "5",
}


def get_base_entity(full_edm):
    if full_edm:
        return dict(_FULL_EDM_ENTITY)
    return dict(_STRING_ENTITY)


class _ServiceTest(PerfStressTest):
    service_client = None
    async_service_client = None

    def __init__(self, arguments):
        super().__init__(arguments)
        connection_string = self.get_from_env("AZURE_TABLES_CONNECTION_STRING")
        if self.args.no_client_share:
            self.service_client = SyncTableServiceClient.from_connection_string(connection_string)
            self.async_service_client = AsyncTableServiceClient.from_connection_string(connection_string)
        else:
            if not _ServiceTest.service_client:
                _ServiceTest.service_client = SyncTableServiceClient.from_connection_string(connection_string)
                _ServiceTest.async_service_client = AsyncTableServiceClient.from_connection_string(connection_string)
            self.service_client = _ServiceTest.service_client
            self.async_service_client = _ServiceTest.async_service_client

    async def close(self):
        await self.async_service_client.close()
        await super().close()

    @staticmethod
    def add_arguments(parser):
        super(_ServiceTest, _ServiceTest).add_arguments(parser)
        parser.add_argument(
            "--no-client-share",
            action="store_true",
            help="Create one ServiceClient per test instance.  Default is to share a single ServiceClient.",
            default=False,
        )
        parser.add_argument(
            "--full-edm",
            action="store_true",
            help="Whether to use entities that utilize all EDM types for serialization/deserialization, or only strings. Default is False (only strings).",
            default=False,
        )


class _TableTest(_ServiceTest):
    table_name = "".join(random.choice(_LETTERS) for i in range(30))

    def __init__(self, arguments):
        super().__init__(arguments)
        self.table_client = self.service_client.get_table_client(self.table_name)
        self.async_table_client = self.async_service_client.get_table_client(self.table_name)

    async def global_setup(self):
        await super().global_setup()
        await self.async_table_client.create_table()

    async def global_cleanup(self):
        await self.async_table_client.delete_table()
        await super().global_cleanup()

    async def close(self):
        await self.async_table_client.close()
        await super().close()
