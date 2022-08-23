# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: job_queue_crud_ops.py
DESCRIPTION:
    These samples demonstrates how to create Job Queues used in ACS JobRouter.
    You need a valid connection string to an Azure Communication Service to execute the sample

USAGE:
    python job_queue_crud_ops.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
"""

import os


class JobQueueSamples(object):
    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _job_queue_id = "sample_q_policy"
    _distribution_policy_id = "sample_dp_policy"

    def create_queue(self):
        connection_string = self.endpoint
        job_queue_id = self._job_queue_id
        distribution_policy_id = self._distribution_policy_id
        # [START create_queue]
        from azure.communication.jobrouter import (
            RouterAdministrationClient,
            JobQueue,
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = RouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("RouterAdministrationClient created successfully!")

        job_queue: JobQueue = router_admin_client.create_queue(
            queue_id = job_queue_id,
            distribution_policy_id = distribution_policy_id,
            name = "My job queue"
        )

        print(f"Job queue successfully created with id: {job_queue.id}")

        # [END create_queue]

    def update_queue(self):
        connection_string = self.endpoint
        job_queue_id = self._job_queue_id
        # [START update_queue]
        from azure.communication.jobrouter import (
            RouterAdministrationClient,
            JobQueue,
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = RouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("RouterAdministrationClient created successfully!")

        updated_job_queue: JobQueue = router_admin_client.update_queue(
            queue_id = job_queue_id,
            labels = {
                "Additional-Queue-Label": "ChatQueue"
            }
        )

        print(f"Router queue successfully update with labels {updated_job_queue.labels}")
        # [END update_queue]

    def get_queue(self):
        connection_string = self.endpoint
        job_queue_id = self._job_queue_id
        # [START get_queue]
        from azure.communication.jobrouter import RouterAdministrationClient

        router_admin_client = RouterAdministrationClient.from_connection_string(conn_str = connection_string)

        job_queue = router_admin_client.get_queue(queue_id = job_queue_id)

        print(f"Successfully fetched router queue with id: {job_queue.id}")
        # [END get_queue]

    def get_queue_statistics(self):
        connection_string = self.endpoint
        job_queue_id = self._job_queue_id

        # [START get_queue_statistics]
        from azure.communication.jobrouter import (
            RouterClient,
            QueueStatistics
        )

        router_client: RouterClient = RouterClient.from_connection_string(conn_str = connection_string)

        job_queue_statistics: QueueStatistics = router_client.get_queue_statistics(queue_id = job_queue_id)

        print(f"Successfully fetched queue statistics router queue: {job_queue_statistics}")
        # [END get_queue_statistics]

    def list_queues(self):
        connection_string = self.endpoint
        # [START list_queues]
        from azure.communication.jobrouter import RouterAdministrationClient

        router_admin_client = RouterAdministrationClient.from_connection_string(conn_str = connection_string)

        job_queue_iterator = router_admin_client.list_queues(results_per_page = 10)

        for queue_page in job_queue_iterator.by_page():
            job_queues_in_page = list(queue_page)
            print(f"Retrieved {len(job_queues_in_page)} queues in current page")

            for q in job_queues_in_page:
                print(f"Retrieved distribution policy with id: {q.job_queue.id}")

        print(f"Successfully completed fetching job queues")
        # [END list_queues]

    def clean_up(self):
        connection_string = self.endpoint
        job_queue_id = self._job_queue_id

        # [START delete_queue]
        from azure.communication.jobrouter import RouterAdministrationClient

        router_admin_client = RouterAdministrationClient.from_connection_string(conn_str = connection_string)

        router_admin_client.delete_queue(queue_id = job_queue_id)

        # [END delete_queue]


if __name__ == '__main__':
    sample = JobQueueSamples()
    sample.create_queue()
    sample.update_queue()
    sample.get_queue()
    sample.get_queue_statistics()
    sample.list_queues()
    sample.clean_up()
