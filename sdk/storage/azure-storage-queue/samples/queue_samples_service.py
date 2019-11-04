# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: queue_samples_service.py

DESCRIPTION:
    These samples demonstrate the following: setting and getting queue service properties,
    listing the queues in the service, and getting a QueueClient from a QueueServiceClient.

USAGE:
    python queue_samples_service.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os


class QueueServiceSamples(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    def queue_service_properties(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(conn_str=self.connection_string)

        # [START set_queue_service_properties]
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
        queue_service.set_service_properties(logging, hour_metrics, minute_metrics, cors)
        # [END set_queue_service_properties]

        # [START get_queue_service_properties]
        properties = queue_service.get_service_properties()
        # [END get_queue_service_properties]

    def queues_in_account(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(conn_str=self.connection_string)

        # [START qsc_create_queue]
        queue_service.create_queue("myqueue1")
        # [END qsc_create_queue]

        try:
            # [START qsc_list_queues]
            # List all the queues in the service
            list_queues = queue_service.list_queues()
            for queue in list_queues:
                print(queue)

            # List the queues in the service that start with the name "my"
            list_my_queues = queue_service.list_queues(name_starts_with="my")
            for queue in list_my_queues:
                print(queue)
            # [END qsc_list_queues]

        finally:
            # [START qsc_delete_queue]
            queue_service.delete_queue("myqueue1")
            # [END qsc_delete_queue]

    def get_queue_client(self):
        # Instantiate the QueueServiceClient from a connection string
        from azure.storage.queue import QueueServiceClient, QueueClient
        queue_service = QueueServiceClient.from_connection_string(conn_str=self.connection_string)

        # [START get_queue_client]
        # Get the queue client to interact with a specific queue
        queue = queue_service.get_queue_client(queue="myqueue2")
        # [END get_queue_client]


if __name__ == '__main__':
    sample = QueueServiceSamples()
    sample.queue_service_properties()
    sample.queues_in_account()
    sample.get_queue_client()