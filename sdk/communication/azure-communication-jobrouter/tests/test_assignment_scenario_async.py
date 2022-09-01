# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import (
    HttpResponseError,
)
from _router_test_case_async import AsyncRouterTestCase
from _shared.asynctestcase import AsyncCommunicationTestCase

from _decorators_async import RouterPreparersAsync
from azure.communication.jobrouter._shared.utils import parse_connection_str

from azure.communication.jobrouter.aio import (
    RouterAdministrationClient,
    RouterClient,
)
from azure.communication.jobrouter import (
    LongestIdleMode,
    QueueAssignment,
    ChannelConfiguration,
    RouterJobStatus,
    RouterWorker,
    JobOffer,
    AcceptJobOfferResult,
    CompleteJobResult,
    CloseJobResult,
    RouterJob,
    JobAssignment,
    JobRouterError,
    RouterWorkerState,
)


channel_id = 'fakeChannel1'


# The test class name needs to start with "Test" to get collected by pytest
class TestAssignmentScenarioAsync(AsyncRouterTestCase):
    def __init__(self, method_name):
        super(TestAssignmentScenarioAsync, self).__init__(method_name)
        self.distribution_policy_ids = {}  # type: Dict[str, List[str]]
        self.queue_ids = {}  # type: Dict[str, List[str]]
        self.classification_policy_ids = {}  # type: Dict[str, List[str]]
        self.worker_ids = {}  # type: Dict[str, List[str]]
        self.job_ids = {}  # type: Dict[str, List[str]]

    async def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_admin_client: RouterAdministrationClient = self.create_admin_client()
            router_client: RouterClient = self.create_client()

            async with router_client:
                async with router_admin_client:
                    if self._testMethodName in self.job_ids \
                            and any(self.job_ids[self._testMethodName]):
                        for _id in set(self.job_ids[self._testMethodName]):
                            await self.clean_up_job(job_id = _id)

                    if self._testMethodName in self.worker_ids \
                            and any(self.worker_ids[self._testMethodName]):
                        for _id in set(self.worker_ids[self._testMethodName]):
                            # de-register worker
                            await router_client.update_worker(worker_id = _id, available_for_offers = False)

                            await self._poll_until_no_exception(
                                self.validate_worker_deregistration,  # cSpell:disable-line
                                Exception,
                                _id)
                            # delete worker
                            await router_client.delete_worker(worker_id = _id)

                    if self._testMethodName in self.classification_policy_ids \
                            and any(self.classification_policy_ids[self._testMethodName]):
                        for policy_id in set(self.classification_policy_ids[self._testMethodName]):
                            await router_admin_client.delete_classification_policy(classification_policy_id = policy_id)

                    if self._testMethodName in self.queue_ids \
                            and any(self.queue_ids[self._testMethodName]):
                        for policy_id in set(self.queue_ids[self._testMethodName]):
                            await router_admin_client.delete_queue(queue_id = policy_id)

                    if self._testMethodName in self.distribution_policy_ids \
                            and any(self.distribution_policy_ids[self._testMethodName]):
                        for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                            await router_admin_client.delete_distribution_policy(distribution_policy_id = policy_id)

    def setUp(self):
        super(TestAssignmentScenarioAsync, self).setUp()

        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint

    def tearDown(self):
        super(TestAssignmentScenarioAsync, self).tearDown()

    def get_distribution_policy_id(self):
        return self._testMethodName + "_tst_dp_async"

    async def setup_distribution_policy(self):
        client: RouterAdministrationClient = self.create_admin_client()

        async with client:
            distribution_policy_id = self.get_distribution_policy_id()
            distribution_policy = await client.create_distribution_policy(
                distribution_policy_id = distribution_policy_id,
                name = "test",
                offer_ttl_seconds = 10.0 * 60,
                mode = LongestIdleMode(
                    min_concurrent_offers = 1,
                    max_concurrent_offers = 1)
            )

            # add for cleanup later
            if self._testMethodName in self.distribution_policy_ids:
                self.distribution_policy_ids[self._testMethodName] \
                    = self.distribution_policy_ids[self._testMethodName].append(distribution_policy_id)
            else:
                self.distribution_policy_ids[self._testMethodName] = [distribution_policy_id]

    def get_job_queue_id(self):
        return self._testMethodName + "_tst_q_async"

    async def setup_job_queue(self):
        client: RouterAdministrationClient = self.create_admin_client()

        async with client:
            job_queue_id = self.get_job_queue_id()
            job_queue = await client.create_queue(
                queue_id = job_queue_id,
                name = "test",
                distribution_policy_id = self.get_distribution_policy_id()
            )

            # add for cleanup later
            if self._testMethodName in self.queue_ids:
                self.queue_ids[self._testMethodName] \
                    = self.queue_ids[self._testMethodName].append(job_queue_id)
            else:
                self.queue_ids[self._testMethodName] = [job_queue_id]

    def get_router_worker_id(self):
        return self._testMethodName + "_tst_w"

    async def setup_router_worker(self):
        w_identifier = self.get_router_worker_id()
        router_client: RouterClient = self.create_client()

        async with router_client:
            worker_queue_assignments = {self.get_job_queue_id(): QueueAssignment()}
            worker_channel_configs = {
                channel_id: ChannelConfiguration(capacity_cost_per_job = 1)
            }

            router_worker = await router_client.create_worker(
                worker_id = w_identifier,
                total_capacity = 1,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = True
            )

            # add for cleanup
            self.worker_ids[self._testMethodName] = [w_identifier]

    async def validate_job_is_queued(
            self,
            identifier,
            **kwargs
    ):
        router_client: RouterClient = self.create_client()

        async with router_client:
            router_job = await router_client.get_job(job_id = identifier)
            assert router_job.job_status == RouterJobStatus.QUEUED

    async def validate_worker_has_offer(
            self,
            worker_id,  # type: str
            job_id,  # type: str
            **kwargs,  # type: Any
    ):
        router_client: RouterClient = self.create_client()

        async with router_client:
            router_worker: RouterWorker = await router_client.get_worker(worker_id = worker_id)
            offer_for_jobs = [job_offer for job_offer in router_worker.offers if job_offer.job_id == job_id]
            assigned_jobs = [assigned_job for assigned_job in router_worker.assigned_jobs if assigned_job.job_id == job_id]
            assert any(offer_for_jobs) or any(assigned_jobs)

    async def validate_worker_deregistration(  # cSpell:disable-line
            self,
            worker_id,  # type: str
            **kwargs,  # type: Any
    ):
        router_client: RouterClient = self.create_client()

        async with router_client:
            router_worker: RouterWorker = await router_client.get_worker(worker_id = worker_id)
            assert router_worker.state == RouterWorkerState.INACTIVE

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_router_worker')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_assignment_scenario(self):
        router_client: RouterClient = self.create_client()

        async with router_client:
            # create job
            job_identifier = f"assignment_scenario_job_id"
            router_job: RouterJob = await router_client.create_job(
                job_id = job_identifier,
                channel_id = channel_id,
                queue_id = self.get_job_queue_id(),
                priority = 1,
            )

            # add for cleanup
            self.job_ids[self._testMethodName] = [job_identifier]

            assert router_job is not None

            await self._poll_until_no_exception(
                self.validate_worker_has_offer,
                AssertionError,
                self.get_router_worker_id(),
                job_identifier
            )

            router_worker = await router_client.get_worker(worker_id = self.get_router_worker_id())
            job_offers = [job_offer for job_offer in router_worker.offers if job_offer.job_id == job_identifier]

            assert len(job_offers) == 1
            job_offer: JobOffer = job_offers[0]
            assert job_offer.capacity_cost == 1
            assert job_offer.offer_time_utc is not None
            assert job_offer.expiry_time_utc is not None

            # accept job offer
            offer_id = job_offer.id
            accept_job_offer_result: AcceptJobOfferResult = await router_client.accept_job_offer(
                worker_id = self.get_router_worker_id(),
                offer_id = offer_id
            )

            assert accept_job_offer_result.job_id == job_identifier
            assert accept_job_offer_result.worker_id == self.get_router_worker_id()

            assignment_id = accept_job_offer_result.assignment_id

            with pytest.raises(HttpResponseError) as sre:
                await router_client.decline_job_offer(
                    worker_id = self.get_router_worker_id(),
                    offer_id = offer_id
                )
            assert sre is not None

            # complete job
            complete_job_result: CompleteJobResult = await router_client.complete_job(
                job_id = job_identifier,
                assignment_id = assignment_id
            )

            # close job
            close_job_result: CloseJobResult = await router_client.close_job(
                job_id = job_identifier,
                assignment_id = assignment_id
            )

            # validate post closure job details
            queried_job: RouterJob = await router_client.get_job(job_id = job_identifier)

            job_assignment: JobAssignment = queried_job.assignments[assignment_id]
            assert job_assignment.assign_time is not None
            assert job_assignment.worker_id == self.get_router_worker_id()
            assert job_assignment.complete_time is not None
            assert job_assignment.close_time is not None
