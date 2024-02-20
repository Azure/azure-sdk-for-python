# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid

from ._base import _TableTest, get_base_entity


class CreateEntityBatchTest(_TableTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.base_entity = get_base_entity(self.args.full_edm)
        self.base_entity["PartitionKey"] = str(uuid.uuid4())

    def run_sync(self):
        batch_size = 0
        batch = []
        for row in range(self.args.count):
            self.base_entity["RowKey"] = str(row)
            batch.append(("upsert", self.base_entity))
            batch_size += 1
            if batch_size >= 100:
                self.table_client.submit_transaction(batch)
                batch = []
                batch_size = 0
        if batch_size:
            self.table_client.submit_transaction(batch)

    async def run_async(self):
        batch_size = 0
        batch = []
        for row in range(self.args.count):
            self.base_entity["RowKey"] = str(row)
            batch.append(("upsert", self.base_entity))
            batch_size += 1
            if batch_size >= 100:
                await self.async_table_client.submit_transaction(batch)
                batch = []
                batch_size = 0
        if batch_size:
            await self.async_table_client.submit_transaction(batch)

    @staticmethod
    def add_arguments(parser):
        super(CreateEntityBatchTest, CreateEntityBatchTest).add_arguments(parser)
        parser.add_argument(
            "-c",
            "--count",
            nargs="?",
            type=int,
            help="Number of entities to batch create. Defaults to 100",
            default=100,
        )
