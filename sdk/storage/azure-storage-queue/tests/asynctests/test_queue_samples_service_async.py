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

from queuetestcase import (
    QueueTestCase,
    record,
    TestMode
)


class TestQueueServiceSamplesAsync(QueueTestCase):

    connection_string = settings.CONNECTION_STRING

    @record
    async def _test_queue_service_properties(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(self.connection_string)

        # [START set_queue_service_properties]
        # Create service properties
        from azure.storage.queue import Logging, Metrics, CorsRule, RetentionPolicy

        # Create logging settings
        logging = Logging(read=True, write=True, delete=True, retention_policy=RetentionPolicy(enabled=True, days=5))

        # Create metrics for requests statistics
        hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))
        minute_metrics = Metrics(enabled=True, include_apis=True,
                                 retention_policy=RetentionPolicy(enabled=True, days=5))

        # Create CORS rules
        cors_rule1 = CorsRule(['www.xyz.com'], ['GET'])
        allowed_origins = ['www.xyz.com', "www.ab.com", "www.bc.com"]
        allowed_methods = ['GET', 'PUT']
        max_age_in_seconds = 500
        exposed_headers = ["x-ms-meta-data*", "x-ms-meta-source*", "x-ms-meta-abc", "x-ms-meta-bcd"]
        allowed_headers = ["x-ms-meta-data*", "x-ms-meta-target*", "x-ms-meta-xyz", "x-ms-meta-foo"]
        cors_rule2 = CorsRule(
            allowed_origins,
            allowed_methods,
            max_age_in_seconds=max_age_in_seconds,
            exposed_headers=exposed_headers,
            allowed_headers=allowed_headers)

        cors = [cors_rule1, cors_rule2]

        # Set the service properties
        await queue_service.set_service_properties(logging, hour_metrics, minute_metrics, cors)
        # [END set_queue_service_properties]

        # [START get_queue_service_properties]
        properties = await queue_service.get_service_properties()
        # [END get_queue_service_properties]

    def test_queue_service_properties(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_queue_service_properties())

    @record
    async def _test_queues_in_account(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(self.connection_string)

        # [START qsc_create_queue]
        queue_service.create_queue("testqueue")
        # [END qsc_create_queue]

        try:
            # [START qsc_list_queues]
            # List all the queues in the service
            list_queues = next(queue_service.list_queues())

            # List the queues in the service that start with the name "test"
            list_test_queues = next(queue_service.list_queues(name_starts_with="test"))
            # [END qsc_list_queues]

        finally:
            # [START qsc_delete_queue]
            queue_service.delete_queue("testqueue")
            # [END qsc_delete_queue]
            
    def test_queues_in_account(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_queues_in_account())

    @record
    async def _test_get_queue_client(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue.aio import QueueServiceClient, QueueClient
        queue_service = QueueServiceClient.from_connection_string(self.connection_string)

        # [START get_queue_client]
        # Get the queue client to interact with a specific queue
        queue = await queue_service.get_queue_client("myqueue")
        # [END get_queue_client]

    def test_get_queue_client(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_queue_client())
