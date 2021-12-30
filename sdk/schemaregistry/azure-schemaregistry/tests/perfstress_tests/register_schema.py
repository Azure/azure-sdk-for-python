# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _RegisterTest


class RegisterSchemaTest(_RegisterTest):
    def run_sync(self):
        self.sync_client.register_schema(
            self.group_name, self.name, self.definition, self.format
        )

    async def run_async(self):
        await self.async_client.register_schema(
            self.group_name, self.name, self.definition, self.format
        )
