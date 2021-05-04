# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio

from ._test_base import _ReceiveTest


class LegacyReceiveMessageBatchTest(_ReceiveTest):
    def run_sync(self):
        count = 0
        while count < self.args.num_messages:
            batch = self.receiver.fetch_next(max_batch_size=self.args.num_messages - count)
            if self.args.peeklock:
                for msg in batch:
                    msg.complete()
            count += len(batch)

    async def run_async(self):
        count = 0
        while count < self.args.num_messages:
            batch = await self.async_receiver.fetch_next(max_batch_size=self.args.num_messages - count)
            if self.args.peeklock:
                await asyncio.gather(*[m.complete() for m in batch])
            count += len(batch)
