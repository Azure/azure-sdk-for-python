# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _RegisterTest


class RegisterSchemaTest(_RegisterTest):
    def run_sync(self):
        for i in range(self.args.num_schemas):
            self.sync_client.register_schema(
                self.group_name, f"{self.name}{i}", self.definition, self.format
            )

    async def run_async(self):
        for i in range(self.args.num_schemas):
            await self.async_client.register_schema(
                self.group_name, f"{self.name}{i}", self.definition, self.format
            )
