# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _GetSchemaTest

class GetSchemaPropertiesTest(_GetSchemaTest):
    def run_sync(self):
        for _ in range(self.args.num_schemas):
            self.sync_client.get_schema_properties(self.group_name, self.name, self.definition, self.format)

    async def run_async(self):
        for _ in range(self.args.num_schemas):
            await self.async_client.get_schema_properties(self.group_name, self.name, self.definition, self.format)
