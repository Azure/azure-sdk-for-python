# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _SendTest

from azure.servicebus import ServiceBusMessage

class SendMessageBatchTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = b'a' * self.args.message_size

    def run_sync(self):
        batch = self.sender.create_message_batch(max_size_in_bytes=self.args.batch_size)
        try:
            while True:
                message = ServiceBusMessage(self.data)
                batch.add_message(message)
        except ValueError:
            # Batch full
            self.sender.send_messages(batch)

    async def run_async(self):
        batch = await self.async_sender.create_message_batch(max_size_in_bytes=self.args.batch_size)
        try:
            while True:
                message = ServiceBusMessage(self.data)
                batch.add_message(message)
        except ValueError:
            # Batch full
            await self.sender.send_messages(batch)

    @staticmethod
    def add_arguments(parser):
        super(SendMessageTest, SendMessageTest).add_arguments(parser)
        parser.add_argument('--batch-size', nargs='?', type=int, help='Maximum size of a batch of messages. Defaults to 4*1024*1024', default=4*1024*1024)
