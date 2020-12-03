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
        try:
            while True:
                message = ServiceBusMessage(self.data)
                batch.add_message(message)
        except ValueError:
            # Batch full
            self.sender.send_messages(batch)

    async def run_async(self):
        batch = await self.async_sender.create_message_batch()
        try:
            while True:
                message = ServiceBusMessage(self.data)
                batch.add_message(message)
        except ValueError:
            # Batch full
            await self.async_sender.send_messages(batch)
