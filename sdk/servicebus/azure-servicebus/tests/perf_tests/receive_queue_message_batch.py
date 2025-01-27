# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio

from ._test_base import _QueueReceiveBatchTest


class ReceiveQueueMessageBatchTest(_QueueReceiveBatchTest):
    def run_batch_sync(self) -> None:
        batch = self.receiver.receive_messages(
            max_message_count=self.args.num_messages, max_wait_time=self.args.max_wait_time or None
        )
        if self.args.peeklock:
            for msg in batch:
                self.receiver.complete_message(msg)
        return len(batch)

    async def run_batch_async(self) -> None:
        batch = await self.async_receiver.receive_messages(
            max_message_count=self.args.num_messages, max_wait_time=self.args.max_wait_time or None
        )
        if self.args.peeklock:
            await asyncio.gather(*[self.async_receiver.complete_message(m) for m in batch])
        return len(batch)
