# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: router_job_crud_ops_async.py
DESCRIPTION:
    These samples demonstrates how to create Job used in ACS JobRouter.
    You need a valid connection string to an Azure Communication Service to execute the sample

USAGE:
    python router_job_crud_ops_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_COMMUNICATION_SERVICE_ENDPOINT - Communication Service endpoint url
"""

import os
import asyncio


class RouterJobSamplesAsync(object):
    endpoint = os.environ.get("AZURE_COMMUNICATION_SERVICE_ENDPOINT", None)
    if not endpoint:
        raise ValueError("Set AZURE_COMMUNICATION_SERVICE_ENDPOINT env before run this sample.")

    _job_id = "sample_job"
    _job_w_cp_id = "sample_job_w_cp"
    _distribution_policy_id = "sample_distribution_policy"
    _classification_policy_id = "sample_classification_policy"
    _queue_id = "sample_queue"
    _worker_id = "sample_worker"

    async def setup_distribution_policy(self):
        connection_string = self.endpoint
        distribution_policy_id = self._distribution_policy_id

        from azure.communication.jobrouter.aio import RouterAdministrationClient
        from azure.communication.jobrouter import (
            LongestIdleMode
        )

        router_admin_client = RouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("RouterAdministrationClient created successfully!")

        async with router_admin_client:
            dist_policy = await router_admin_client.create_distribution_policy(
                distribution_policy_id = distribution_policy_id,
                offer_ttl_seconds = 10 * 60,
                mode = LongestIdleMode(
                    min_concurrent_offers = 1,
                    max_concurrent_offers = 1
                )
            )

    async def setup_queue(self):
        connection_string = self.endpoint
        queue_id = self._queue_id
        from azure.communication.jobrouter.aio import RouterAdministrationClient
        from azure.communication.jobrouter import (
            JobQueue
        )

        router_admin_client = RouterAdministrationClient.from_connection_string(conn_str = connection_string)

        async with router_admin_client:
            job_queue: JobQueue = await router_admin_client.create_queue(
                queue_id = queue_id,
                distribution_policy_id = self._distribution_policy_id
            )

    async def setup_classification_policy(self):
        connection_string = self.endpoint
        classification_policy_id = self._distribution_policy_id

        from azure.communication.jobrouter.aio import RouterAdministrationClient
        from azure.communication.jobrouter import (
            StaticRule,
            StaticQueueSelectorAttachment,
            QueueSelector,
            LabelOperator
        )

        router_admin_client = RouterAdministrationClient.from_connection_string(conn_str = connection_string)
        print("RouterAdministrationClient created successfully!")

        async with router_admin_client:
            classification_policy = await router_admin_client.create_classification_policy(
                classification_policy_id = classification_policy_id,
                prioritization_rule = StaticRule(value = 10),
                queue_selectors = [
                    StaticQueueSelectorAttachment(
                        label_selector = QueueSelector(
                            key = "Id",
                            label_operator = LabelOperator.EQUAL,
                            value = self._queue_id)
                    )
                ]
            )

    async def setup_worker(self):
        connection_string = self.endpoint
        worker_id = self._worker_id
        queue_id = self._queue_id

        from azure.communication.jobrouter.aio import RouterClient
        from azure.communication.jobrouter import (
            ChannelConfiguration,
            QueueAssignment
        )

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            router_worker = await router_client.create_worker(
                worker_id = worker_id,
                total_capacity = 100,
                available_for_offers = True,
                channel_configurations = {
                    "general": ChannelConfiguration(capacity_cost_per_job = 100)
                },
                queue_assignments = {
                    queue_id: QueueAssignment()
                }
            )

    async def create_job(self):
        connection_string = self.endpoint
        job_id = self._job_id
        job_w_cp_id = self._job_w_cp_id
        queue_id = self._queue_id
        classification_policy_id = self._classification_policy_id

        # [START create_job_async]
        from azure.communication.jobrouter.aio import (
            RouterClient,
        )

        # set `connection_string` to an existing ACS endpoint
        router_client = RouterClient.from_connection_string(conn_str = connection_string)
        print("RouterAdministrationClient created successfully!")

        async with router_client:
            # We need to create a distribution policy + queue as a pre-requisite to start creating job
            router_job = await router_client.create_job(
                job_id = job_id,
                channel_id = "general",
                queue_id = queue_id,
                priority = 10,
                channel_reference = "12345"
            )

            print(f"Job has been successfully created with status: {router_job.job_status}")

            # Alternatively, a job can also be created while specifying a classification policy
            # As a pre-requisite, we would need to create a classification policy first
            router_job_with_cp = await router_client.create_job(
                job_id = job_w_cp_id,
                channel_id = "general",
                classification_policy_id = classification_policy_id,
                channel_reference = "12345"
            )
            print(f"Job has been successfully created with status: {router_job_with_cp.job_status}")

        # [END create_job_async]

    async def update_job(self):
        connection_string = self.endpoint
        job_id = self._job_id
        # [START update_job_async]
        from azure.communication.jobrouter.aio import (
            RouterClient,
        )

        # set `connection_string` to an existing ACS endpoint
        router_client: RouterClient = RouterClient.from_connection_string(conn_str = connection_string)
        print("RouterAdministrationClient created successfully!")

        async with router_client:
            update_job = await router_client.update_job(
                job_id = job_id,
                channel_reference = "45678"
            )

            print(f"Job has been successfully update with channel reference: {update_job.channel_reference}")
        # [END update_job_async]

    async def get_job(self):
        connection_string = self.endpoint
        job_id = self._job_id
        # [START get_job_async]
        from azure.communication.jobrouter.aio import RouterClient

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            router_job = await router_client.get_job(job_id = job_id)

            print(f"Successfully fetched router worker with id: {router_job.id}")
        # [END get_job_async]

    async def get_job_position(self):
        connection_string = self.endpoint
        job_id = self._job_id
        # [START get_job_position_async]
        from azure.communication.jobrouter.aio import RouterClient

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            router_job_position = await router_client.get_queue_position(job_id = job_id)

            print(f"Successfully fetched router job position: {router_job_position.position}")
        # [END get_job_position_async]

    async def reclassify_job(self):
        connection_string = self.endpoint
        job_id = self._job_w_cp_id
        # [START reclassify_job_async]
        from azure.communication.jobrouter.aio import RouterClient

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            reclassify_job_result = await router_client.reclassify_job(job_id = job_id)

            print(f"Successfully re-classified router")
        # [END reclassify_job_async]

    async def accept_job_offer(self):
        connection_string = self.endpoint
        job_id = self._job_id
        worker_id = self._worker_id

        from azure.communication.jobrouter.aio import RouterClient
        from azure.communication.jobrouter import (
            JobOffer
        )

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            while any(
                    [offer for offer in (await router_client.get_worker(worker_id = worker_id)).offers if
                     offer.job_id != job_id]):
                await asyncio.sleep(delay = 1)

            queried_worker = await router_client.get_worker(worker_id = worker_id)
            issued_offer: JobOffer = [offer for offer in queried_worker.offers if offer.job_id == job_id][0]
            offer_id = issued_offer.id

            # [START accept_job_offer_async]
            from azure.communication.jobrouter import (
                RouterJob,
                AcceptJobOfferResult
            )

            accept_job_offer_result: AcceptJobOfferResult = await router_client.accept_job_offer(
                worker_id = worker_id,
                offer_id = offer_id
            )

            queried_job: RouterJob = await router_client.get_job(job_id = job_id)

            print(f"Job has been successfully assigned to worker. Current job status: {queried_job.job_status}")
            print(f"Job has been successfully assigned with a worker with assignment "
                  f"id: {accept_job_offer_result.assignment_id}")
            # [END accept_job_offer_async]

            try:
                # [START decline_job_offer_async]
                decline_job_offer_result = await router_client.decline_job_offer(
                    worker_id = worker_id,
                    offer_id = offer_id
                )
                # [END decline_job_offer_async]
            except Exception:
                print(f"Error encountered")

    async def complete_and_close_job(self):
        connection_string = self.endpoint
        job_id = self._job_id

        # [START complete_job_async]
        from azure.communication.jobrouter.aio import RouterClient
        from azure.communication.jobrouter import (
            RouterJob,
            CompleteJobResult,
            CloseJobResult
        )

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            queried_job: RouterJob = await router_client.get_job(job_id = job_id)

            assignment_id = [k for k, v in queried_job.assignments.items()][0]

            complete_job_result: CompleteJobResult = await router_client.complete_job(
                job_id = job_id,
                assignment_id = assignment_id
            )

            queried_job: RouterJob = await router_client.get_job(job_id = job_id)

            print(f"Job has been successfully completed. Current status: {queried_job.job_status}")
        # [END complete_job_async]

        # [START close_job_async]
            close_job_result: CloseJobResult = await router_client.close_job(
                job_id = job_id,
                assignment_id = assignment_id
            )

            queried_job: RouterJob = await router_client.get_job(job_id = job_id)

            print(f"Job has been successfully closed. Current status: {queried_job.job_status}")

        # [END close_job_async]

    async def list_jobs(self):
        connection_string = self.endpoint
        # [START list_jobs_async]
        from azure.communication.jobrouter.aio import RouterClient

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            router_job_iterator = router_client.list_jobs(results_per_page = 10)

            async for job_page in router_job_iterator.by_page():
                jobs_in_page = [i async for i in job_page]
                print(f"Retrieved {len(jobs_in_page)} jobs in current page")

                for j in jobs_in_page:
                    print(f"Retrieved job with id: {j.router_job.id}")

            print(f"Successfully completed fetching jobs")
        # [END list_jobs_async]

    async def cancel_job(self):
        connection_string = self.endpoint
        job_id = self._job_w_cp_id

        # [START cancel_job_async]
        from azure.communication.jobrouter.aio import RouterClient

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            await router_client.delete_job(job_id = job_id)

        # [END cancel_job_async]

    async def clean_up(self):
        connection_string = self.endpoint
        job_id = self._job_id

        # [START delete_job_async]
        from azure.communication.jobrouter.aio import RouterClient

        router_client = RouterClient.from_connection_string(conn_str = connection_string)

        async with router_client:
            await router_client.delete_job(job_id = job_id)

        # [END delete_job_async]


async def main():
    sample = RouterJobSamplesAsync()
    await sample.setup_distribution_policy()
    await sample.setup_queue()
    await sample.setup_classification_policy()
    await sample.setup_worker()
    await sample.create_job()
    await sample.get_job()
    await sample.get_job_position()
    await sample.update_job()
    await sample.reclassify_job()
    await sample.accept_job_offer()
    await sample.complete_and_close_job()
    await sample.list_jobs()
    await sample.clean_up()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
