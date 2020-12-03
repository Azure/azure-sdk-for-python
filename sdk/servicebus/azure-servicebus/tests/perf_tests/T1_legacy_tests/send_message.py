# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._test_base import _SendTest

from azure.servicebus import ServiceBusMessage

class LegacySendMessageTest(_SendTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        self.data = b'a' * self.args.message_size

    def run_sync(self):
        message = ServiceBusMessage(self.data)
        self.sender.send_messages(message)

    async def run_async(self):
        message = ServiceBusMessage(self.data)
        await self.async_sender.send_messages(message)
