# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import asyncio

try:
    import settings_real as settings
except ImportError:
    import queue_settings_fake as settings
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from queuetestcase import (
    QueueTestCase,
    record,
    TestMode
)


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class TestQueueHelloWorldSamplesAsync(QueueTestCase):

    connection_string = settings.CONNECTION_STRING

    async def _test_create_client_with_connection_string(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(self.connection_string)

        # Get queue service properties
        properties = await queue_service.get_service_properties()

        assert properties is not None

    @record
    def test_create_client_with_connection_string(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_client_with_connection_string())
