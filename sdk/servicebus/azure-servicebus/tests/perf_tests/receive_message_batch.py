# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio

from ._test_base import _ReceiveTest


class ReceiveMessageBatchTest(_ReceiveTest):
    def run_sync(self):
        count = 0
        while count < self.args.num_messages:
            batch = self.receiver.receive_messages(
                max_message_count=self.args.num_messages - count,
                max_wait_time=self.args.max_wait_time or None)
            if self.args.peeklock:
                for msg in batch:
                    self.receiver.complete_message(msg)
            count += len(batch)

    async def run_async(self):
        count = 0
        while count < self.args.num_messages:
            batch = await self.async_receiver.receive_messages(
                max_message_count=self.args.num_messages - count,
                max_wait_time=self.args.max_wait_time or None)
            if self.args.peeklock:
                await asyncio.gather(*[self.async_receiver.complete_message(m) for m in batch])
            count += len(batch)
