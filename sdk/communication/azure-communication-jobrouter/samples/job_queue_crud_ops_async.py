# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: job_queue_crud_ops_async.py
DESCRIPTION:
    These samples demonstrates how to create Job Queues used in ACS JobRouter.
    You need a valid connection string to an Azure Communication Service to execute the sample

USAGE:
    python job_queue_crud_ops_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
"""

import os
import asyncio


class JobQueueSamplesAsync(object):
    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _job_queue_id = "sample_q_policy"
    _distribution_policy_id = "sample_dp_policy"

    async def setup_distribution_policy(self):
        connection_string = self.endpoint
        distribution_policy_id = self._distribution_policy_id

        from azure.communication.jobrouter.aio import JobRouterAdministrationClient
        from azure.communication.jobrouter import (
            LongestIdleMode,
            DistributionPolicy
        )
        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
        async with router_admin_client:
            distribution_policy = await router_admin_client.create_distribution_policy(
                distribution_policy_id = distribution_policy_id,
                distribution_policy = DistributionPolicy(
                    offer_expires_after_seconds = 10 * 60,
                    mode = LongestIdleMode(
                        min_concurrent_offers = 1,
                        max_concurrent_offers = 1
                    )
                )
            )
            print(f"Sample setup completed: Created distribution policy")

    async def create_queue(self):
        connection_string = self.endpoint
        job_queue_id = self._job_queue_id
        distribution_policy_id = self._distribution_policy_id
        # [START create_queue_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient
        from azure.communication.jobrouter import (
            RouterQueue,
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("JobRouterAdministrationClient created successfully!")

        async with router_admin_client:
            job_queue: RouterQueue = await router_admin_client.create_queue(
                queue_id = job_queue_id,
                queue = RouterQueue(
                    distribution_policy_id = distribution_policy_id,
                    name = "My job queue"
                )
            )

            print(f"Job queue successfully created with id: {job_queue.id}")

        # [END create_queue_async]

    async def update_queue(self):
        connection_string = self.endpoint
        job_queue_id = self._job_queue_id
        # [START update_queue_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient
        from azure.communication.jobrouter import (
            RouterQueue,
        )

        # set `connection_string` to an existing ACS endpoint
        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("JobRouterAdministrationClient created successfully!")

        async with router_admin_client:
            updated_job_queue: RouterQueue = await router_admin_client.update_queue(
                queue_id = job_queue_id,
                labels = {
                    "Additional-Queue-Label": "ChatQueue"
                }
            )

            print(f"Router queue successfully update with labels {updated_job_queue.labels}")
        # [END update_queue_async]

    async def get_queue(self):
        connection_string = self.endpoint
        job_queue_id = self._job_queue_id
        # [START get_queue_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            job_queue = await router_admin_client.get_queue(queue_id = job_queue_id)

            print(f"Successfully fetched router queue with id: {job_queue.id}")
        # [END get_queue_async]

    async def get_queue_statistics(self):
        connection_string = self.endpoint
        job_queue_id = self._job_queue_id

        # [START get_queue_statistics_async]
        from azure.communication.jobrouter.aio import JobRouterClient
        from azure.communication.jobrouter import (
            RouterQueueStatistics
        )

        router_client: JobRouterClient = JobRouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            job_queue_statistics: RouterQueueStatistics = await router_client.get_queue_statistics(queue_id = job_queue_id)

            print(f"Successfully fetched queue statistics router queue: {job_queue_statistics}")
        # [END get_queue_statistics_async]

    async def list_queues(self):
        connection_string = self.endpoint
        # [START list_queues_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            job_queue_iterator = router_admin_client.list_queues()

            async for q in job_queue_iterator:
                print(f"Retrieved queue policy with id: {q.queue.id}")

            print(f"Successfully completed fetching job queues")
        # [END list_queues_async]

    async def list_queues_batched(self):
        connection_string = self.endpoint
        # [START list_queues_batched_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            job_queue_iterator = router_admin_client.list_queues(results_per_page = 10)

            async for queue_page in job_queue_iterator.by_page():
                job_queues_in_page = [i async for i in queue_page]
                print(f"Retrieved {len(job_queues_in_page)} queues in current page")

                for q in job_queues_in_page:
                    print(f"Retrieved queue policy with id: {q.queue.id}")

            print(f"Successfully completed fetching job queues")
        # [END list_queues_batched_async]

    async def clean_up(self):
        connection_string = self.endpoint
        job_queue_id = self._job_queue_id

        # [START delete_queue_async]
        from azure.communication.jobrouter.aio import JobRouterAdministrationClient

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            await router_admin_client.delete_queue(queue_id = job_queue_id)

        # [END delete_queue_async]


async def main():
    sample = JobQueueSamplesAsync()
    await sample.setup_distribution_policy()
    await sample.create_queue()
    # await sample.update_queue()
    await sample.get_queue()
    await sample.get_queue_statistics()
    await sample.list_queues()
    await sample.list_queues_batched()
    await sample.clean_up()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
