# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: router_worker_crud_ops_async.py
DESCRIPTION:
    These samples demonstrates how to create Workers used in ACS JobRouter.
    You need a valid connection string to an Azure Communication Service to execute the sample

USAGE:
    python router_worker_crud_ops_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
"""

import os
import asyncio


class RouterWorkerSamplesAsync(object):
    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _worker_id = "sample_worker"
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

    async def setup_queues(self):
        connection_string = self.endpoint
        distribution_policy_id = self._distribution_policy_id

        from azure.communication.jobrouter.aio import JobRouterAdministrationClient
        from azure.communication.jobrouter import (
            RouterQueue
        )

        router_admin_client = JobRouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            job_queue1: RouterQueue = await router_admin_client.create_queue(
                queue_id = "worker-q-1",
                queue = RouterQueue(
                    distribution_policy_id = distribution_policy_id,
                )
            )

            job_queue2: RouterQueue = await router_admin_client.create_queue(
                queue_id = "worker-q-2",
                queue = RouterQueue(
                    distribution_policy_id = distribution_policy_id,
                )
            )

            job_queue3: RouterQueue = await router_admin_client.create_queue(
                queue_id = "worker-q-3",
                queue = RouterQueue(
                    distribution_policy_id = distribution_policy_id,
                )
            )

            print(f"Sample setup completed: Created queues")

    async def create_worker(self):
        connection_string = self.endpoint
        worker_id = self._worker_id
        # [START create_worker_async]
        from azure.communication.jobrouter.aio import JobRouterClient
        from azure.communication.jobrouter import (
            RouterWorker,
            ChannelConfiguration,
        )

        # set `connection_string` to an existing ACS endpoint
        router_client = JobRouterClient.from_connection_string(conn_str = connection_string)
        print("JobRouterClient created successfully!")

        async with router_client:
            router_worker: RouterWorker = await router_client.create_worker(
                worker_id = worker_id,
                router_worker = RouterWorker(
                    total_capacity = 100,
                    queue_assignments = {
                        "worker-q-1": {},
                        "worker-q-2": {}
                    },
                    channel_configurations = {
                        "WebChat": ChannelConfiguration(capacity_cost_per_job = 1),
                        "WebChatEscalated": ChannelConfiguration(capacity_cost_per_job = 20),
                        "Voip": ChannelConfiguration(capacity_cost_per_job = 100)
                    },
                    labels = {
                        "Location": "NA",
                        "English": 7,
                        "O365": True,
                        "Xbox_Support": False
                    },
                    tags = {
                        "Name": "John Doe",
                        "Department": "IT_HelpDesk"
                    }
                )
            )

            print(f"Router worker successfully created with id: {router_worker.id}")

        # [END create_worker_async]

    async def update_worker(self):
        connection_string = self.endpoint
        worker_id = self._worker_id
        # [START update_worker_async]
        from azure.communication.jobrouter.aio import JobRouterClient
        from azure.communication.jobrouter import (
            RouterWorker,
            ChannelConfiguration,
        )

        # set `connection_string` to an existing ACS endpoint
        router_client: JobRouterClient = JobRouterClient.from_connection_string(conn_str = connection_string)
        print("JobRouterClient created successfully!")

        # we are going to
        # 1. Assign the worker to another queue
        # 2. Modify an value of label: `O365`
        # 3. Delete label: `Xbox_Support`
        # 4. Add a new label: `Xbox_Support_EN` and set value true
        # 5. Increase capacityCostPerJob for channel `WebChatEscalated` to 50

        async with router_client:
            updated_router_worker: RouterWorker = await router_client.update_worker(
                worker_id = worker_id,
                queue_assignments = {
                    "worker-q-3": {}
                },
                channel_configurations = {
                    "WebChatEscalated": ChannelConfiguration(capacity_cost_per_job = 50)
                },
                labels = {
                    "O365": "Supported",
                    "Xbox_Support": None,
                    "Xbox_Support_EN": True
                }
            )

            print(f"Router worker successfully update with labels {updated_router_worker.labels}")
        # [END update_worker_async]

    async def get_worker(self):
        connection_string = self.endpoint
        worker_id = self._worker_id
        # [START get_worker_async]
        from azure.communication.jobrouter.aio import JobRouterClient

        router_client = JobRouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            router_worker = await router_client.get_worker(worker_id = worker_id)

            print(f"Successfully fetched router worker with id: {router_worker.id}")
        # [END get_worker_async]

    async def register_worker(self):
        connection_string = self.endpoint
        worker_id = self._worker_id
        # [START register_worker_async]
        from azure.communication.jobrouter.aio import JobRouterClient

        router_client = JobRouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            router_worker = await router_client.update_worker(
                worker_id = worker_id,
                available_for_offers = True
            )

            print(f"Successfully registered router worker with id: {router_worker.id} with status: {router_worker.state}")
        # [END register_worker_async]

    async def deregister_worker(self):
        connection_string = self.endpoint
        worker_id = self._worker_id
        # [START deregister_worker_async]
        from azure.communication.jobrouter.aio import JobRouterClient

        router_client = JobRouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            router_worker = await router_client.update_worker(
                worker_id = worker_id,
                available_for_offers = False
            )

            print(f"Successfully de-registered router worker with id: {router_worker.id} "
                  f"with status: {router_worker.state}")
        # [END deregister_worker_async]

    async def list_workers(self):
        connection_string = self.endpoint
        # [START list_workers_async]
        from azure.communication.jobrouter.aio import JobRouterClient

        router_client = JobRouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            router_worker_iterator = router_client.list_workers()

            async for w in router_worker_iterator:
                print(f"Retrieved worker with id: {w.worker.id}")

            print(f"Successfully completed fetching workers")
        # [END list_workers_async]

    async def list_workers_batched(self):
        connection_string = self.endpoint
        # [START list_workers_batched_async]
        from azure.communication.jobrouter.aio import JobRouterClient

        router_client = JobRouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            router_worker_iterator = router_client.list_workers(results_per_page = 10)

            async for worker_page in router_worker_iterator.by_page():
                workers_in_page = [i async for i in worker_page]
                print(f"Retrieved {len(workers_in_page)} workers in current page")

                for w in workers_in_page:
                    print(f"Retrieved worker with id: {w.worker.id}")

            print(f"Successfully completed fetching workers")
        # [END list_workers_batched_async]

    async def clean_up(self):
        connection_string = self.endpoint
        worker_id = self._worker_id

        # [START delete_worker_async]
        from azure.communication.jobrouter.aio import JobRouterClient

        router_client = JobRouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            await router_client.delete_worker(worker_id = worker_id)

        # [END delete_worker_async]


async def main():
    sample = RouterWorkerSamplesAsync()
    await sample.setup_distribution_policy()
    await sample.setup_queues()
    await sample.create_worker()
    await sample.update_worker()
    await sample.get_worker()
    await sample.register_worker()
    await sample.deregister_worker()
    await sample.list_workers()
    await sample.list_workers_batched()
    await sample.clean_up()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
