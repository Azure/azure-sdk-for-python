# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _GetSchemaTest


class GetSchemaByIdTest(_GetSchemaTest):
    def run_sync(self):
        self.sync_client.get_schema(self.schema_id)

    async def run_async(self):
        await self.async_client.get_schema(self.schema_id)
