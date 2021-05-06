# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _ReceiveTest


class LegacyReceiveEventBatchTest(_ReceiveTest):
    def run_sync(self):
        count = 0
        while count < self.args.num_events:
            batch = self.receiver.receive(
                max_batch_size=self.args.num_events - count,
                timeout=self.args.max_wait_time or None
            )
            count += len(batch)

    async def run_async(self):
        count = 0
        while count < self.args.num_events:
            batch = await self.async_receiver.receive(
                max_batch_size=self.args.num_events - count,
                timeout=self.args.max_wait_time or None
            )
            count += len(batch)
