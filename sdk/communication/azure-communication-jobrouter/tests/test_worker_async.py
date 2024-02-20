# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from _router_test_case_async import (
    AsyncRouterRecordedTestCase
)
from _shared.asynctestcase import AsyncCommunicationTestCase
from _validators import RouterWorkerValidator
from _decorators_async import RouterPreparersAsync
from azure.communication.jobrouter._shared.utils import parse_connection_str
from azure.core.exceptions import ResourceNotFoundError

from azure.communication.jobrouter.aio import (
    JobRouterClient,
    JobRouterAdministrationClient
)
from azure.communication.jobrouter import (
    RoundRobinMode,
    RouterWorker,
    ChannelConfiguration, DistributionPolicy, RouterQueue,
)

worker_labels = {
        'key1': "WorkerKey",
        'key2': 10,
        'key3': True
    }

worker_tags = {
        'tag1': "WorkerGenericInfo",
    }

worker_channel_configs = {
    'fakeChannel1': ChannelConfiguration(capacity_cost_per_job = 10),
    'fakeChannel2': ChannelConfiguration(capacity_cost_per_job = 90)
}

worker_total_capacity = 100


# The test class name needs to start with "Test" to get collected by pytest
class TestRouterWorkerAsync(AsyncRouterRecordedTestCase):
    async def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_client: JobRouterClient = self.create_client()
            router_admin_client: JobRouterAdministrationClient = self.create_admin_client()
            async with router_client:
                async with router_admin_client:
                    if self._testMethodName in self.worker_ids \
                            and any(self.worker_ids[self._testMethodName]):
                        for _id in set(self.worker_ids[self._testMethodName]):
                            await router_client.delete_worker(worker_id = _id)

                    if self._testMethodName in self.queue_ids \
                            and any(self.queue_ids[self._testMethodName]):
                        for _id in set(self.queue_ids[self._testMethodName]):
                            await router_admin_client.delete_queue(queue_id = _id)

                    if self._testMethodName in self.distribution_policy_ids \
                            and any(self.distribution_policy_ids[self._testMethodName]):
                        for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                            await router_admin_client.delete_distribution_policy(distribution_policy_id = policy_id)

    def get_distribution_policy_id(self):
        return self._testMethodName + "_tst_dp_async"

    async def setup_distribution_policy(self):
        client: JobRouterAdministrationClient = self.create_admin_client()

        async with client:
            distribution_policy_id = self.get_distribution_policy_id()

            policy: DistributionPolicy = DistributionPolicy(
                name = distribution_policy_id,
                offer_expires_after_seconds = 10.0,
                mode = RoundRobinMode(min_concurrent_offers = 1,
                                      max_concurrent_offers = 1)
            )

            distribution_policy = await client.create_distribution_policy(
                distribution_policy_id = distribution_policy_id,
                distribution_policy = policy
            )

            # add for cleanup later
            if self._testMethodName in self.distribution_policy_ids:
                self.distribution_policy_ids[self._testMethodName] = self.distribution_policy_ids[
                    self._testMethodName].append(distribution_policy_id)
            else:
                self.distribution_policy_ids[self._testMethodName] = [distribution_policy_id]

    def get_job_queue_id(self):
        return self._testMethodName + "_tst_q_async"

    async def setup_job_queue(self):
        client: JobRouterAdministrationClient = self.create_admin_client()

        async with client:
            job_queue_id = self.get_job_queue_id()

            job_queue: RouterQueue = RouterQueue(
                name = job_queue_id,
                labels = worker_labels,
                distribution_policy_id = self.get_distribution_policy_id()
            )

            job_queue = await client.create_queue(
                queue_id = job_queue_id,
                queue = job_queue
            )

            # add for cleanup later
            if self._testMethodName in self.queue_ids:
                self.queue_ids[self._testMethodName] \
                    = self.queue_ids[self._testMethodName].append(job_queue_id)
            else:
                self.queue_ids[self._testMethodName] = [job_queue_id]

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_create_worker(self):
        w_identifier = "tst_create_w_async"
        router_client: JobRouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): {}}

        async with router_client:
            router_worker: RouterWorker = RouterWorker(
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            router_worker = await router_client.create_worker(
                worker_id = w_identifier,
                router_worker = router_worker
            )

            # add for cleanup
            self.worker_ids[self._testMethodName] = [w_identifier]

            assert router_worker is not None
            RouterWorkerValidator.validate_worker(
                router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

    @pytest.mark.skip(reason = "Upsert worker not working correctly")
    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_worker(self):
        w_identifier = "tst_update_w_async"
        router_client: JobRouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): {}}

        async with router_client:
            router_worker: RouterWorker = RouterWorker(
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            router_worker = await router_client.create_worker(
                worker_id = w_identifier,
                router_worker = router_worker
            )

            # add for cleanup
            self.worker_ids[self._testMethodName] = [w_identifier]

            assert router_worker is not None
            RouterWorkerValidator.validate_worker(
                router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            # Act
            router_worker.labels['FakeKey'] = "FakeWorkerValue"
            updated_worker_labels = router_worker.labels

            update_router_worker = await router_client.update_worker(
                worker_id = w_identifier,
                router_worker = router_worker
            )

            assert update_router_worker is not None
            RouterWorkerValidator.validate_worker(
                update_router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = updated_worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

    @pytest.mark.skip(reason = "Upsert worker not working correctly")
    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_worker_w_kwargs(self):
        w_identifier = "tst_update_w_kwargs_async"
        router_client: JobRouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): {}}

        async with router_client:
            router_worker: RouterWorker = RouterWorker(
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            router_worker = await router_client.create_worker(
                worker_id = w_identifier,
                router_worker = router_worker
            )

            # add for cleanup
            self.worker_ids[self._testMethodName] = [w_identifier]

            assert router_worker is not None
            RouterWorkerValidator.validate_worker(
                router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            # Act
            router_worker.labels['FakeKey'] = "FakeWorkerValue"
            updated_worker_labels = router_worker.labels

            update_router_worker = await router_client.update_worker(
                worker_id = w_identifier,
                labels = updated_worker_labels
            )

            assert update_router_worker is not None
            RouterWorkerValidator.validate_worker(
                update_router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = updated_worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_get_worker(self):
        w_identifier = "tst_get_w_async"
        router_client: JobRouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): {}}

        async with router_client:
            router_worker: RouterWorker = RouterWorker(
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            router_worker = await router_client.create_worker(
                worker_id = w_identifier,
                router_worker = router_worker
            )

            # add for cleanup
            self.worker_ids[self._testMethodName] = [w_identifier]

            assert router_worker is not None
            RouterWorkerValidator.validate_worker(
                router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            queried_router_worker = await router_client.get_worker(
                worker_id = w_identifier
            )

            RouterWorkerValidator.validate_worker(
                queried_router_worker,
                identifier = w_identifier,
                total_capacity = router_worker.total_capacity,
                labels = router_worker.labels,
                tags = router_worker.tags,
                queue_assignments = router_worker.queue_assignments,
                channel_configurations = router_worker.channel_configurations,
                available_for_offers = router_worker.available_for_offers
            )

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_delete_worker(self):
        w_identifier = "tst_delete_w_async"
        router_client: JobRouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): {}}

        async with router_client:
            router_worker: RouterWorker = RouterWorker(
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            router_worker = await router_client.create_worker(
                worker_id = w_identifier,
                router_worker = router_worker
            )

            assert router_worker is not None
            RouterWorkerValidator.validate_worker(
                router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                tags = worker_tags,
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            await router_client.delete_worker(worker_id = w_identifier)
            with pytest.raises(ResourceNotFoundError) as nfe:
                await router_client.get_worker(worker_id = w_identifier)
            assert nfe.value.reason == "Not Found"
            assert nfe.value.status_code == 404

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_list_workers(self):
        router_client: JobRouterClient = self.create_client()
        w_identifiers = ["tst_list_w_1", "tst_list_w_2", "tst_list_w_3"]
        worker_queue_assignments = {self.get_job_queue_id(): {}}
        created_w_response = {}
        w_count = len(w_identifiers)
        self.worker_ids[self._testMethodName] = []

        async with router_client:
            for identifier in w_identifiers:
                router_worker: RouterWorker = RouterWorker(
                    total_capacity = worker_total_capacity,
                    labels = worker_labels,
                    tags = worker_tags,
                    queue_assignments = worker_queue_assignments,
                    channel_configurations = worker_channel_configs,
                    available_for_offers = False
                )

                worker = await router_client.create_worker(
                    worker_id = identifier,
                    router_worker = router_worker
                )

                # add for cleanup
                self.worker_ids[self._testMethodName].append(identifier)

                assert worker is not None

                RouterWorkerValidator.validate_worker(
                    worker,
                    identifier = identifier,
                    total_capacity = worker_total_capacity,
                    labels = worker_labels,
                    tags = worker_tags,
                    queue_assignments = worker_queue_assignments,
                    channel_configurations = worker_channel_configs,
                    available_for_offers = False
                )
                created_w_response[worker.id] = worker

            router_workers = router_client.list_workers(
                results_per_page = 3,
                state = "inactive",
                queue_id = self.get_job_queue_id(),
                channel_id = "fakeChannel1")

            async for worker_page in router_workers.by_page():
                list_of_workers = [i async for i in worker_page]
                assert len(list_of_workers) <= 3

                for w_item in list_of_workers:
                    response_at_creation = created_w_response.get(w_item.worker.id, None)

                    if not response_at_creation:
                        continue

                    RouterWorkerValidator.validate_worker(
                        w_item.worker,
                        identifier = response_at_creation.id,
                        total_capacity = response_at_creation.total_capacity,
                        labels = response_at_creation.labels,
                        tags = response_at_creation.tags,
                        queue_assignments = response_at_creation.queue_assignments,
                        channel_configurations = response_at_creation.channel_configurations,
                        available_for_offers = response_at_creation.available_for_offers
                    )
                    w_count -= 1

            # all workers created were listed
            assert w_count == 0

