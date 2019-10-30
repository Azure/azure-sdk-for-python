# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: queue_samples_service_async.py

DESCRIPTION:
    These samples demonstrate the following: setting and getting queue service properties,
    listing the queues in the service, and getting a QueueClient from a QueueServiceClient.

USAGE:
    python queue_samples_service_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""


import asyncio
import os


class QueueServiceSamplesAsync(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    async def queue_service_properties_async(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(conn_str=self.connection_string)

        async with queue_service:
            # [START async_set_queue_service_properties]
            # Create service properties
            from azure.storage.queue import QueueAnalyticsLogging, Metrics, CorsRule, RetentionPolicy

            # Create logging settings
            logging = QueueAnalyticsLogging(read=True, write=True, delete=True, retention_policy=RetentionPolicy(enabled=True, days=5))

            # Create metrics for requests statistics
            hour_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))
            minute_metrics = Metrics(enabled=True, include_apis=True, retention_policy=RetentionPolicy(enabled=True, days=5))

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
                allowed_headers=allowed_headers
            )

            cors = [cors_rule1, cors_rule2]

            # Set the service properties
            await queue_service.set_service_properties(logging, hour_metrics, minute_metrics, cors)
            # [END async_set_queue_service_properties]

            # [START async_get_queue_service_properties]
            properties = await queue_service.get_service_properties()
            # [END async_get_queue_service_properties]

    async def queues_in_account_async(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue.aio import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(conn_str=self.connection_string)

        async with queue_service:
            # [START async_qsc_create_queue]
            await queue_service.create_queue("myqueue1")
            # [END async_qsc_create_queue]

            try:
                # [START async_qsc_list_queues]
                # List all the queues in the service
                list_queues = queue_service.list_queues()
                async for queue in list_queues:
                    print(queue)

                # List the queues in the service that start with the name "my_"
                list_my_queues = queue_service.list_queues(name_starts_with="my_")
                async for queue in list_my_queues:
                    print(queue)
                # [END async_qsc_list_queues]

            finally:
                # [START async_qsc_delete_queue]
                await queue_service.delete_queue("myqueue1")
                # [END async_qsc_delete_queue]

    async def get_queue_client_async(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue.aio import QueueServiceClient, QueueClient
        queue_service = QueueServiceClient.from_connection_string(conn_str=self.connection_string)

        # [START async_get_queue_client]
        # Get the queue client to interact with a specific queue
        queue = queue_service.get_queue_client(queue="myqueue2")
        # [END async_get_queue_client]


async def main():
    sample = QueueServiceSamplesAsync()
    await sample.queue_service_properties_async()
    await sample.queues_in_account_async()
    await sample.get_queue_client_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
