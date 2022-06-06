# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure_devtools.perfstress_tests import BatchPerfTest
import random

class MockReceiver():
    def receive(self, min_messages=1, max_messages=5):
        for i in range(random.randint(min_messages, max_messages)):
            yield i

class AsyncMockReceiver():
    async def receive(self, min_messages=1, max_messages=5):
        for i in range(random.randint(min_messages, max_messages)):
            yield i


class SampleBatchTest(BatchPerfTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # Setup service clients
        self.receiver_client = MockReceiver()
        self.async_receiver_client = AsyncMockReceiver()

    def run_batch_sync(self) -> int:
        messages = self.receiver_client.receive(
            max_messages=self.args.max_message_count,
            min_messages=self.args.min_message_count
        )
        return len(list(messages))

    async def run_batch_async(self) -> int:
        messages = self.async_receiver_client.receive(
            max_messages=self.args.max_message_count,
            min_messages=self.args.min_message_count
        )
        return len([m async for m in messages])
        
    @staticmethod
    def add_arguments(parser):
        super(SampleBatchTest, SampleBatchTest).add_arguments(parser)
        parser.add_argument('--max-message-count', nargs='?', type=int, default=10)
        parser.add_argument('--min-message-count', nargs='?', type=int, default=0)
