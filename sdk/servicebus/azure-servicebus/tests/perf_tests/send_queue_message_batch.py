# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _SendQueueTest

from devtools_testutils.perfstress_tests import get_random_bytes

from azure.servicebus import ServiceBusMessage


class SendQueueMessageBatchTest(_SendQueueTest):
    def __init__(self, arguments) -> None:
        super().__init__(arguments)
        self.data = get_random_bytes(self.args.message_size)

    def run_batch_sync(self) -> int:
        batch = self.sender.create_message_batch()
        for _ in range(self.args.batch_size):
            batch.add_message(ServiceBusMessage(self.data))
        self.sender.send_messages(batch)
        return self.args.batch_size

    async def run_batch_async(self) -> int:
        batch = await self.async_sender.create_message_batch()
        for _ in range(self.args.batch_size):
            batch.add_message(ServiceBusMessage(self.data))

        await self.async_sender.send_messages(batch)
        return self.args.batch_size
