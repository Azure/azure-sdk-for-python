# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from _router_test_case import (
    RouterTestCase
)
from _validators import RouterWorkerValidator
from _decorators import RouterPreparers
from azure.communication.jobrouter._shared.utils import parse_connection_str
from azure.core.exceptions import ResourceNotFoundError

from azure.communication.jobrouter import (
    RouterClient,
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
class TestRouterWorker(RouterTestCase):
    def __init__(self, method_name):
        super(TestRouterWorker, self).__init__(method_name)

        self.queue_ids = {}  # type: Dict[str, List[str]]
        self.distribution_policy_ids = {}  # type: Dict[str, List[str]]
        self.worker_ids = {}  # type: Dict[str, List[str]]

    def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_client: RouterClient = self.create_client()
            if self._testMethodName in self.worker_ids \
                    and any(self.worker_ids[self._testMethodName]):
                for _id in set(self.worker_ids[self._testMethodName]):
                    router_client.delete_worker(identifier = _id)

            if self._testMethodName in self.queue_ids \
                    and any(self.queue_ids[self._testMethodName]):
                for _id in set(self.queue_ids[self._testMethodName]):
                    router_client.delete_queue(identifier = _id)

            if self._testMethodName in self.distribution_policy_ids \
                    and any(self.distribution_policy_ids[self._testMethodName]):
                for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                    router_client.delete_distribution_policy(identifier = policy_id)

    def setUp(self):
        super(TestRouterWorker, self).setUp()

        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint

    def tearDown(self):
        super(TestRouterWorker, self).tearDown()

    def get_distribution_policy_id(self):
        return self._testMethodName + "_tst_dp"

    def setup_distribution_policy(self):
        client: RouterClient = self.create_client()

        distribution_policy_id = self.get_distribution_policy_id()
        distribution_policy = client.create_distribution_policy(
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
        return self._testMethodName + "_tst_q"

    def setup_job_queue(self):
        client: RouterClient = self.create_client()
        job_queue_id = self.get_job_queue_id()
        job_queue = client.create_queue(
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

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_create_worker(self):
        w_identifier = "tst_create_w"
        router_client: RouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): QueueAssignment()}

        router_worker = router_client.create_worker(
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
    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_update_worker(self):
        w_identifier = "tst_update_w"
        router_client: RouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): QueueAssignment()}

        router_worker = router_client.create_worker(
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

        update_router_worker = router_client.update_worker(
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

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_get_worker(self):
        w_identifier = "tst_get_w"
        router_client: RouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): QueueAssignment()}

        router_worker = router_client.create_worker(
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

        queried_router_worker = router_client.get_worker(
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

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_delete_worker(self):
        w_identifier = "tst_delete_w"
        router_client: RouterClient = self.create_client()
        worker_queue_assignments = {self.get_job_queue_id(): QueueAssignment()}

        router_worker = router_client.create_worker(
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

        router_client.delete_worker(identifier = w_identifier)
        with pytest.raises(ResourceNotFoundError) as nfe:
            router_client.get_worker(identifier = w_identifier)
        assert nfe.value.reason == "Not Found"
        assert nfe.value.status_code == 404

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_list_workers(self):
        router_client: RouterClient = self.create_client()
        w_identifiers = ["tst_list_w_1", "tst_list_w_2", "tst_list_w_3"]
        worker_queue_assignments = {self.get_job_queue_id(): QueueAssignment()}
        created_w_response = {}
        w_count = len(w_identifiers)
        self.worker_ids[self._testMethodName] = []

        for identifier in w_identifiers:
            worker = router_client.create_worker(
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

        for worker_page in router_workers.by_page():
            list_of_workers = list(worker_page)
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

        # all job_queues created were listed
        assert w_count == 0

