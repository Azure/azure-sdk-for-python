# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid

from ._base import _TableTest, get_base_entity


class CreateEntityTest(_TableTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.base_entity = get_base_entity(self.args.full_edm)
        self.base_entity["PartitionKey"] = str(uuid.uuid4())
        self.base_entity["RowKey"] = str(uuid.uuid4())

    def run_sync(self):
        self.table_client.upsert_entity(self.base_entity)

    async def run_async(self):
        await self.async_table_client.upsert_entity(self.base_entity)
