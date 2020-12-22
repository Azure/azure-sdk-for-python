# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _SendTest

from azure_devtools.perfstress_tests import get_random_bytes

from azure.servicebus import ServiceBusMessage


class SendMessageBatchTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = get_random_bytes(self.args.message_size)

    def run_sync(self):
        batch = self.sender.create_message_batch()
        for i in range(self.args.num_messages):
            try:
                batch.add_message(ServiceBusMessage(self.data))
            except ValueError:
                # Batch full
                self.sender.send_messages(batch)
                batch = self.sender.create_message_batch()
                batch.add_message(ServiceBusMessage(self.data))
        self.sender.send_messages(batch)

    async def run_async(self):
        batch = await self.async_sender.create_message_batch()
        for i in range(self.args.num_messages):
            try:
                batch.add_message(ServiceBusMessage(self.data))
            except ValueError:
                # Batch full
                await self.async_sender.send_messages(batch)
                batch = await self.async_sender.create_message_batch()
                batch.add_message(ServiceBusMessage(self.data))
        await self.async_sender.send_messages(batch)
