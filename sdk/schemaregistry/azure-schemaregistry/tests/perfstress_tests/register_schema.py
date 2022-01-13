# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import uuid
from ._test_base import _RegisterTest


class RegisterSchemaTest(_RegisterTest):
    def run_sync(self):
        for _ in range(self.args.num_schemas):
            self.sync_client.register_schema(
                self.group_name, self.name + str(uuid.uuid4()), self.definition, self.format
            )

    async def run_async(self):
        for _ in range(self.args.num_schemas):
            await self.async_client.register_schema(
                self.group_name, self.name + str(uuid.uuid4()), self.definition, self.format
            )
