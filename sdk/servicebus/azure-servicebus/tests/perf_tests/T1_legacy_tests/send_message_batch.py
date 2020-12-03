# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _SendTest

from azure.servicebus import BatchMessage


class LegacySendMessageBatchTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = b'a' * self.args.message_size

    def run_sync(self):
        messages = (self.data for _ in range(self.args.batch_size))
        batch = BatchMessage(messages)
        self.sender.send(batch)

    async def run_async(self):
        messages = (self.data for _ in range(self.args.batch_size))
        batch = BatchMessage(messages)
        await self.async_sender.send(batch)

    @staticmethod
    def add_arguments(parser):
        super(LegacySendMessageBatchTest, LegacySendMessageBatchTest).add_arguments(parser)
        parser.add_argument('--batch-size', nargs='?', type=int, help='Maximum size of a batch of messages. Defaults to 4*1024*1024', default=4*1024*1024)
