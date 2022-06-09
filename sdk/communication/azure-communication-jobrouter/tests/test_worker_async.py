# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from _router_test_case_async import (
    AsyncRouterTestCase
)
from _shared.asynctestcase import AsyncCommunicationTestCase
from _validators import RouterWorkerValidator
from _decorators_async import RouterPreparersAsync
from azure.communication.jobrouter._shared.utils import parse_connection_str
from azure.core.exceptions import ResourceNotFoundError

from azure.communication.jobrouter.aio import RouterClient
from azure.communication.jobrouter import (
    RoundRobinMode,
    LabelCollection,
    RouterWorker,
    QueueAssignment,
    ChannelConfiguration,
)

worker_labels = LabelCollection(
    {
        'key1': "WorkerKey",
        'key2': 10,
        'key3': True
    }
)

worker_tags = LabelCollection(
    {
        'tag1': "WorkerGenericInfo",
    }
)

worker_channel_configs = {
    'fakeChannel1': ChannelConfiguration(capacity_cost_per_job = 10),
    'fakeChannel2': ChannelConfiguration(capacity_cost_per_job = 90)
}

worker_total_capacity = 100


# The test class name needs to start with "Test" to get collected by pytest
class TestRouterWorkerAsync(AsyncRouterTestCase):
    def __init__(self, method_name):
        super(TestRouterWorkerAsync, self).__init__(method_name)

        self.queue_ids = {}  # type: Dict[str, List[str]]
        self.distribution_policy_ids = {}  # type: Dict[str, List[str]]
        self.worker_ids = {}  # type: Dict[str, List[str]]

    async def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_client: RouterClient = self.create_client()
            async with router_client:
                if self._testMethodName in self.worker_ids \
                        and any(self.worker_ids[self._testMethodName]):
                    for _id in set(self.worker_ids[self._testMethodName]):
                        await router_client.delete_worker(identifier = _id)

                if self._testMethodName in self.queue_ids \
                        and any(self.queue_ids[self._testMethodName]):
                    for _id in set(self.queue_ids[self._testMethodName]):
                        await router_client.delete_queue(identifier = _id)

                if self._testMethodName in self.distribution_policy_ids \
                        and any(self.distribution_policy_ids[self._testMethodName]):
                    for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                        await router_client.delete_distribution_policy(identifier = policy_id)

    def setUp(self):
        super(TestRouterWorkerAsync, self).setUp()

        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint

    def tearDown(self):
        super(TestRouterWorkerAsync, self).tearDown()

    def get_distribution_policy_id(self):
        return self._testMethodName + "_tst_dp_async"

    async def setup_distribution_policy(self):
        client: RouterClient = self.create_client()

        async with client:
            distribution_policy_id = self.get_distribution_policy_id()
            distribution_policy = await client.create_distribution_policy(
                identifier = distribution_policy_id,
                name = distribution_policy_id,
                offer_ttl_seconds = 10.0,
                mode = RoundRobinMode(min_concurrent_offers = 1,
                                      max_concurrent_offers = 1)
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
        client: RouterClient = self.create_client()

        async with client:
            job_queue_id = self.get_job_queue_id()
            job_queue = await client.create_queue(
                identifier = job_queue_id,
                name = job_queue_id,
                labels = worker_labels,
                distribution_policy_id = self.get_distribution_policy_id()
            )

        # add for cleanup later
        if self._testMethodName in self.queue_ids:
            self.queue_ids[self._testMethodName] \
                = self.queue_ids[self._testMethodName].append(job_queue_id)
        else:
            self.queue_ids[self._testMethodName] = [job_queue_id]

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_create_worker(self):
        w_identifier = "tst_create_w_async"
        router_client: RouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): QueueAssignment()}

        async with router_client:
            router_worker = await router_client.create_worker(
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                # tags = worker_tags,  # TODO: bugfix required
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            # add for cleanup
            self.worker_ids[self._testMethodName] = [w_identifier]

            assert router_worker is not None
            RouterWorkerValidator.validate_worker(
                router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                # tags = worker_tags,  # TODO: bugfix required
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

    @pytest.mark.skip(reason = "Upsert worker not working correctly")
    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_worker(self):
        w_identifier = "tst_update_w_async"
        router_client: RouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): QueueAssignment()}

        async with router_client:
            router_worker = await router_client.create_worker(
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                # tags = worker_tags,  # TODO: bugfix required
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            # add for cleanup
            self.worker_ids[self._testMethodName] = [w_identifier]

            assert router_worker is not None
            RouterWorkerValidator.validate_worker(
                router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                # tags = worker_tags,  # TODO: bugfix required
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            # Act
            router_worker.labels['FakeKey'] = "FakeWorkerValue"
            updated_worker_labels = router_worker.labels

            update_router_worker = await router_client.update_worker(
                identifier = w_identifier,
                router_worker = router_worker
            )

            assert update_router_worker is not None
            RouterWorkerValidator.validate_worker(
                update_router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = updated_worker_labels,
                # tags = worker_tags,  # TODO: bugfix required
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_get_worker(self):
        w_identifier = "tst_get_w_async"
        router_client: RouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): QueueAssignment()}

        async with router_client:
            router_worker = await router_client.create_worker(
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                # tags = worker_tags,  # TODO: bugfix required
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            # add for cleanup
            self.worker_ids[self._testMethodName] = [w_identifier]

            assert router_worker is not None
            RouterWorkerValidator.validate_worker(
                router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                # tags = worker_tags,  # TODO: bugfix required
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            queried_router_worker = await router_client.get_worker(
                identifier = w_identifier
            )

            RouterWorkerValidator.validate_worker(
                queried_router_worker,
                identifier = w_identifier,
                total_capacity = router_worker.total_capacity,
                labels = router_worker.labels,
                # tags = router_worker.tags,  # TODO: bugfix required
                queue_assignments = router_worker.queue_assignments,
                channel_configurations = router_worker.channel_configurations,
                available_for_offers = router_worker.available_for_offers
            )

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_delete_worker(self):
        w_identifier = "tst_delete_w_async"
        router_client: RouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): QueueAssignment()}

        async with router_client:
            router_worker = await router_client.create_worker(
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                # tags = worker_tags,  # TODO: bugfix required
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            assert router_worker is not None
            RouterWorkerValidator.validate_worker(
                router_worker,
                identifier = w_identifier,
                total_capacity = worker_total_capacity,
                labels = worker_labels,
                # tags = worker_tags,  # TODO: bugfix required
                queue_assignments = worker_queue_assignments,
                channel_configurations = worker_channel_configs,
                available_for_offers = False
            )

            await router_client.delete_worker(identifier = w_identifier)
            with pytest.raises(ResourceNotFoundError) as nfe:
                await router_client.get_worker(identifier = w_identifier)
            assert nfe.value.reason == "Not Found"
            assert nfe.value.status_code == 404

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_list_workers(self):
        router_client: RouterClient = self.create_client()
        w_identifiers = ["tst_list_w_1", "tst_list_w_2", "tst_list_w_3"]
        worker_queue_assignments = {self.get_job_queue_id(): QueueAssignment()}
        created_w_response = {}
        w_count = len(w_identifiers)
        self.worker_ids[self._testMethodName] = []

        async with router_client:
            for identifier in w_identifiers:
                worker = await router_client.create_worker(
                    identifier = identifier,
                    total_capacity = worker_total_capacity,
                    labels = worker_labels,
                    # tags = worker_tags,  # TODO: bugfix required
                    queue_assignments = worker_queue_assignments,
                    channel_configurations = worker_channel_configs,
                    available_for_offers = False
                )

                # add for cleanup
                self.worker_ids[self._testMethodName].append(identifier)

                assert worker is not None

                RouterWorkerValidator.validate_worker(
                    worker,
                    identifier = identifier,
                    total_capacity = worker_total_capacity,
                    labels = worker_labels,
                    # tags = worker_tags,  # TODO: bugfix required
                    queue_assignments = worker_queue_assignments,
                    channel_configurations = worker_channel_configs,
                    available_for_offers = False
                )
                created_w_response[worker.id] = worker

            router_workers = router_client.list_workers(
                results_per_page = 2,
                status = "inactive",
                queue_id = self.get_job_queue_id(),
                channel_id = "fakeChannel1")

            async for worker_page in router_workers.by_page():
                list_of_workers = [i async for i in worker_page]
                assert len(list_of_workers) <= 2

                for w in list_of_workers:
                    response_at_creation = created_w_response.get(w.id, None)

                    if not response_at_creation:
                        continue

                    RouterWorkerValidator.validate_worker(
                        w,
                        identifier = response_at_creation.id,
                        total_capacity = response_at_creation.total_capacity,
                        labels = response_at_creation.labels,
                        # tags = response_at_creation.tags,  # TODO: bugfix required
                        queue_assignments = response_at_creation.queue_assignments,
                        channel_configurations = response_at_creation.channel_configurations,
                        available_for_offers = response_at_creation.available_for_offers
                    )
                    w_count -= 1

            # all workers created were listed
            assert w_count == 0

