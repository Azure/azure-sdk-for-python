# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid

from ._base import _TableTest, get_base_entity


class ListEntitiesTest(_TableTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.partition_key = str(uuid.uuid4())

    async def global_setup(self):
        await super().global_setup()
        batch_size = 0
        batch = []
        for row in range(self.args.count):
            base_entity = get_base_entity(self.args.full_edm)
            base_entity["PartitionKey"] = self.partition_key
            base_entity["RowKey"] = str(row)
            batch.append(("create", base_entity))
            batch_size += 1
            if batch_size >= 100:
                await self.async_table_client.submit_transaction(batch)
                batch = []
                batch_size = 0
        if batch_size:
            await self.async_table_client.submit_transaction(batch)

    def run_sync(self):
        for _ in self.table_client.list_entities():
            pass

    async def run_async(self):
        async for _ in self.async_table_client.list_entities():
            pass

    @staticmethod
    def add_arguments(parser):
        super(ListEntitiesTest, ListEntitiesTest).add_arguments(parser)
        parser.add_argument(
            "-c", "--count", nargs="?", type=int, help="Number of entities to list. Defaults to 100", default=100
        )
