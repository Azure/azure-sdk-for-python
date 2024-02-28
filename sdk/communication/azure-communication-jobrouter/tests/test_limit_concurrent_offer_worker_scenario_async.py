# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import (
    HttpResponseError,
)
from _router_test_case_async import AsyncRouterRecordedTestCase

from _decorators_async import RouterPreparersAsync
from azure.communication.jobrouter._shared.utils import parse_connection_str

from azure.communication.jobrouter.aio import (
    JobRouterAdministrationClient,
    JobRouterClient,
)
from azure.communication.jobrouter.models import (
    LongestIdleMode,
    RouterChannel,
    RouterJobStatus,
    RouterWorker,
    RouterJobOffer,
    AcceptJobOfferResult,
    UnassignJobResult,
    RouterJob,
    RouterJobAssignment,
    RouterWorkerState,
    DistributionPolicy,
    RouterQueue,
    CancelJobOptions,
    CompleteJobOptions,
    CloseJobOptions,
    DeclineJobOfferOptions,
)


channel_id = "fakeChannel2_async"


# The test class name needs to start with "Test" to get collected by pytest
class TestLimitConcurrentOffersToWorkerScenarioAsync(AsyncRouterRecordedTestCase):
    async def clean_up(self, **kwargs):
        # delete in live mode
        if not self.is_playback():
            router_admin_client: JobRouterAdministrationClient = self.create_admin_client()
            router_client: JobRouterClient = self.create_client()

            async with router_client:
                async with router_admin_client:
                    if self._testMethodName in self.job_ids and any(self.job_ids[self._testMethodName]):
                        for _id in set(self.job_ids[self._testMethodName]):
                            await self.clean_up_job(job_id=_id, suppress_errors=True)

                    if self._testMethodName in self.worker_ids and any(self.worker_ids[self._testMethodName]):
                        for _id in set(self.worker_ids[self._testMethodName]):
                            # delete worker
                            await router_client.delete_worker(_id)

                    if self._testMethodName in self.classification_policy_ids and any(
                        self.classification_policy_ids[self._testMethodName]
                    ):
                        for policy_id in set(self.classification_policy_ids[self._testMethodName]):
                            await router_admin_client.delete_classification_policy(policy_id)

                    if self._testMethodName in self.queue_ids and any(self.queue_ids[self._testMethodName]):
                        for policy_id in set(self.queue_ids[self._testMethodName]):
                            await router_admin_client.delete_queue(policy_id)

                    if self._testMethodName in self.distribution_policy_ids and any(
                        self.distribution_policy_ids[self._testMethodName]
                    ):
                        for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                            await router_admin_client.delete_distribution_policy(policy_id)

    def get_distribution_policy_id(self, **kwargs):
        return self._testMethodName + "_tst_dp_async"

    async def setup_distribution_policy(self, **kwargs):
        client: JobRouterAdministrationClient = self.create_admin_client()

        async with client:
            distribution_policy_id = self.get_distribution_policy_id()

            policy: DistributionPolicy = DistributionPolicy(
                name="test",
                offer_expires_after_seconds=10.0 * 60,
                mode=LongestIdleMode(min_concurrent_offers=1, max_concurrent_offers=1),
            )

            distribution_policy = await client.upsert_distribution_policy(distribution_policy_id, policy)

            # add for cleanup later
            if self._testMethodName in self.distribution_policy_ids:
                self.distribution_policy_ids[self._testMethodName] = self.distribution_policy_ids[
                    self._testMethodName
                ].append(distribution_policy_id)
            else:
                self.distribution_policy_ids[self._testMethodName] = [distribution_policy_id]

    def get_job_queue_id(self, **kwargs):
        return self._testMethodName + "_tst_q_async"

    async def setup_job_queue(self, **kwargs):
        client: JobRouterAdministrationClient = self.create_admin_client()

        async with client:
            job_queue_id = self.get_job_queue_id()

            job_queue: RouterQueue = RouterQueue(name="test", distribution_policy_id=self.get_distribution_policy_id())

            job_queue = await client.upsert_queue(job_queue_id, job_queue)

            # add for cleanup later
            if self._testMethodName in self.queue_ids:
                self.queue_ids[self._testMethodName] = self.queue_ids[self._testMethodName].append(job_queue_id)
            else:
                self.queue_ids[self._testMethodName] = [job_queue_id]

    def get_router_worker_id(self, **kwargs):
        return self._testMethodName + "_tst_w_async"

    async def setup_router_worker(self, **kwargs):
        w_identifier = self.get_router_worker_id()
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            worker_queues = [self.get_job_queue_id()]
            worker_channels = [RouterChannel(channel_id=channel_id, capacity_cost_per_job=1)]

            worker: RouterWorker = RouterWorker(
                capacity=10,
                queues=worker_queues,
                channels=worker_channels,
                available_for_offers=True,
                max_concurrent_offers=1,
            )

            router_worker = await router_client.upsert_worker(w_identifier, worker)

            # add for cleanup
            self.worker_ids[self._testMethodName] = [w_identifier]

    async def validate_job_is_queued(self, identifier, **kwargs):
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job = await router_client.get_job(identifier)
            assert router_job.status == RouterJobStatus.QUEUED

    async def validate_worker_has_offer(
        self,
        worker_id,  # type: str
        job_ids,  # type: List[str]
        **kwargs,  # type: Any
    ):
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_worker: RouterWorker = await router_client.get_worker(worker_id)
            offer_for_jobs = [job_offer for job_offer in router_worker.offers if job_offer.job_id in job_ids]
            assert any(offer_for_jobs)

    async def validate_worker_deregistration(  # cSpell:disable-line
        self,
        worker_id,  # type: str
        **kwargs,  # type: Any
    ):
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_worker: RouterWorker = await router_client.get_worker(worker_id)
            assert router_worker.state == RouterWorkerState.INACTIVE

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async("setup_distribution_policy")
    @RouterPreparersAsync.before_test_execute_async("setup_job_queue")
    @RouterPreparersAsync.before_test_execute_async("setup_router_worker")
    @RouterPreparersAsync.after_test_execute_async("clean_up")
    async def test_limit_concurrent_offer_to_worker_scenario(self, **kwargs):
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            # create job
            job_identifier_1 = f"concurrent_offer_worker_scenario_job_id_1_async"
            job_identifier_2 = f"concurrent_offer_worker_scenario_job_id_2_async"
            job_ids = [job_identifier_1, job_identifier_2]

            router_job_1: RouterJob = RouterJob(
                channel_id=channel_id,
                queue_id=self.get_job_queue_id(),
                priority=1,
            )

            router_job_1: RouterJob = await router_client.upsert_job(job_identifier_1, router_job_1)

            # add for cleanup
            self.job_ids[self._testMethodName] = [job_identifier_1]

            assert router_job_1 is not None

            # validate there are offers made
            await self._poll_until_no_exception(
                self.validate_worker_has_offer, AssertionError, self.get_router_worker_id(), job_ids
            )

            router_job_2: RouterJob = RouterJob(
                channel_id=channel_id,
                queue_id=self.get_job_queue_id(),
                priority=1,
            )
            router_job_2: RouterJob = await router_client.upsert_job(job_identifier_2, router_job_2)

            # add for cleanup
            self.job_ids[self._testMethodName].append(job_identifier_2)

            # validate there are still offers
            await self._poll_until_no_exception(
                self.validate_worker_has_offer, AssertionError, self.get_router_worker_id(), job_ids
            )

            router_worker = await router_client.get_worker(self.get_router_worker_id())
            job_offers = [job_offer for job_offer in router_worker.offers if job_offer.job_id in job_ids]

            assert len(job_offers) == 1
            job_offer_1: RouterJobOffer = job_offers[0]
            assert job_offer_1.capacity_cost == 1
            assert job_offer_1.offered_at is not None
            assert job_offer_1.expires_at is not None
            job_without_offer: str = job_identifier_2 if job_offer_1.job_id == job_identifier_1 else job_identifier_1

            # accept job offer
            offer_id_1: str = job_offer_1.offer_id
            accept_job_offer_result_1: AcceptJobOfferResult = await router_client.accept_job_offer(
                worker_id=self.get_router_worker_id(), offer_id=offer_id_1
            )

            assert accept_job_offer_result_1.job_id == job_offer_1.job_id
            assert accept_job_offer_result_1.worker_id == self.get_router_worker_id()

            # check for new offers sent to worker now that previous offer has been accepted
            await self._poll_until_no_exception(
                self.validate_worker_has_offer, AssertionError, self.get_router_worker_id(), [job_without_offer]
            )

            router_worker = await router_client.get_worker(self.get_router_worker_id())
            job_offers = [job_offer for job_offer in router_worker.offers if job_offer.job_id == job_without_offer]

            assert len(job_offers) == 1
            job_offer_2: RouterJobOffer = job_offers[0]
            assert job_offer_2.capacity_cost == 1
            assert job_offer_2.offered_at is not None
            assert job_offer_2.expires_at is not None

            # accept job offer
            offer_id_2 = job_offer_2.offer_id
            accept_job_offer_result_2: AcceptJobOfferResult = await router_client.accept_job_offer(
                worker_id=self.get_router_worker_id(), offer_id=offer_id_2
            )

            assert accept_job_offer_result_2.job_id == job_without_offer
            assert accept_job_offer_result_2.worker_id == self.get_router_worker_id()

            # complete both jobs
            await router_client.complete_job(accept_job_offer_result_1.job_id, accept_job_offer_result_1.assignment_id)
            await router_client.complete_job(accept_job_offer_result_2.job_id, accept_job_offer_result_2.assignment_id)

            # close both jobs
            await router_client.close_job(accept_job_offer_result_1.job_id, accept_job_offer_result_1.assignment_id)
            await router_client.close_job(accept_job_offer_result_2.job_id, accept_job_offer_result_2.assignment_id)

            # validate post closure job details
            queried_job_1: RouterJob = await router_client.get_job(job_identifier_1)
            queried_job_2: RouterJob = await router_client.get_job(job_identifier_2)

            assignment_id_for_job_1 = (
                accept_job_offer_result_1.assignment_id
                if accept_job_offer_result_1.job_id == job_identifier_1
                else accept_job_offer_result_2.assignment_id
            )
            assignment_id_for_job_2 = (
                accept_job_offer_result_1.assignment_id
                if accept_job_offer_result_1.job_id == job_identifier_2
                else accept_job_offer_result_2.assignment_id
            )

            job_assignment_1: RouterJobAssignment = queried_job_1.assignments[assignment_id_for_job_1]
            assert job_assignment_1.assigned_at is not None
            assert job_assignment_1.worker_id == self.get_router_worker_id()
            assert job_assignment_1.completed_at is not None
            assert job_assignment_1.closed_at is not None

            job_assignment_2: RouterJobAssignment = queried_job_2.assignments[assignment_id_for_job_2]
            assert job_assignment_2.assigned_at is not None
            assert job_assignment_2.worker_id == self.get_router_worker_id()
            assert job_assignment_2.completed_at is not None
            assert job_assignment_2.closed_at is not None
