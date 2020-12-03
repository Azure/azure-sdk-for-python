# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio

from ._test_base import _ReceiveTest


class ReceiveMessageBatchTest(_ReceiveTest):
    def run_sync(self):
        received_msgs = self.receiver.receive_messages(
            max_message_count=self.args.num_messages,
            max_wait_time=self.args.max_wait_time)
        if self.args.peeklock:
            for msg in received_msgs:
                self.receiver.complete_message(msg)

    async def run_async(self):
        received_msgs = await self.async_receiver.receive_messages(
            max_message_count=self.args.num_messages,
            max_wait_time=self.args.max_wait_time)
        if self.args.peeklock:
            await asyncio.gather(*[self.async_receiver.complete_message(m) for m in received_msgs])
