# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _DecodeTest


class DecodeContentTest(_DecodeTest):
    def run_sync(self):
        for _ in range(self.args.num_values):
            self.sync_encoder.decode(self.encoded_content)

    async def run_async(self):
        for _ in range(self.args.num_values):
            await self.async_encoder.decode(self.encoded_content)
