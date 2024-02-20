# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from devtools_testutils import recorded_by_proxy
from _router_test_case import (
    RouterRecordedTestCase
)
from _validators import JobQueueValidator
from _decorators import RouterPreparers
from azure.communication.jobrouter._shared.utils import parse_connection_str
from azure.core.exceptions import ResourceNotFoundError

from azure.communication.jobrouter import (
    JobRouterAdministrationClient,
    RoundRobinMode, DistributionPolicy, RouterQueue,
)

queue_labels = {
        'key1': "QueueKey",
        'key2': 10,
        'key3': True,
        'key4': False,
        'key5': 10.1
    }


# The test class name needs to start with "Test" to get collected by pytest
class TestJobQueue(RouterRecordedTestCase):
    def clean_up(self, **kwargs):
        # delete in live mode
        if not self.is_playback():
            router_client: JobRouterAdministrationClient = self.create_admin_client()
            if self._testMethodName in self.queue_ids \
                    and any(self.queue_ids[self._testMethodName]):
                for _id in set(self.queue_ids[self._testMethodName]):
                    router_client.delete_queue(queue_id = _id)

            if self._testMethodName in self.distribution_policy_ids \
                    and any(self.distribution_policy_ids[self._testMethodName]):
                for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                    router_client.delete_distribution_policy(distribution_policy_id = policy_id)

    def get_distribution_policy_id(self, **kwargs):
        return self._testMethodName + "_tst_dp"

    def setup_distribution_policy(self, **kwargs):
        client: JobRouterAdministrationClient = self.create_admin_client()

        distribution_policy_id = self.get_distribution_policy_id()

        policy: DistributionPolicy = DistributionPolicy(
            offer_expires_after_seconds = 10.0,
            mode = RoundRobinMode(min_concurrent_offers = 1,
                                  max_concurrent_offers = 1),
            name = distribution_policy_id,
        )

        distribution_policy = client.create_distribution_policy(
            distribution_policy_id = distribution_policy_id,
            distribution_policy = policy
        )

        # add for cleanup later
        if self._testMethodName in self.distribution_policy_ids:
            self.distribution_policy_ids[self._testMethodName] = self.distribution_policy_ids[
                self._testMethodName].append(distribution_policy_id)
        else:
            self.distribution_policy_ids[self._testMethodName] = [distribution_policy_id]

    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.after_test_execute('clean_up')
    def test_create_queue(self, **kwargs):
        dp_identifier = "tst_create_q"
        router_client: JobRouterAdministrationClient = self.create_admin_client()

        job_queue: RouterQueue = RouterQueue(
            distribution_policy_id = self.get_distribution_policy_id(),
            name = dp_identifier,
            labels = queue_labels,
        )

        job_queue = router_client.create_queue(
            queue_id = dp_identifier,
            queue = job_queue
        )

        # add for cleanup
        self.queue_ids[self._testMethodName] = [dp_identifier]

        assert job_queue is not None
        JobQueueValidator.validate_queue(
            job_queue,
            identifier = dp_identifier,
            name = dp_identifier,
            labels = queue_labels,
            distribution_policy_id = self.get_distribution_policy_id()
        )

    @pytest.mark.skip(reason = "Upsert queue not working correctly")
    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.after_test_execute('clean_up')
    def test_update_queue(self, **kwargs):
        dp_identifier = "tst_update_q"
        router_client: JobRouterAdministrationClient = self.create_admin_client()

        job_queue: RouterQueue = RouterQueue(
            distribution_policy_id = self.get_distribution_policy_id(),
            name = dp_identifier,
            labels = queue_labels,
        )

        job_queue = router_client.create_queue(
            queue_id = dp_identifier,
            queue = job_queue
        )

        # add for cleanup
        self.queue_ids[self._testMethodName] = [dp_identifier]

        assert job_queue is not None
        JobQueueValidator.validate_queue(
            job_queue,
            identifier = dp_identifier,
            name = dp_identifier,
            labels = queue_labels,
            distribution_policy_id = self.get_distribution_policy_id()
        )

        # Act
        job_queue = router_client.get_queue(identifier = dp_identifier)
        updated_queue_labels = dict(queue_labels)
        updated_queue_labels['key6'] = "Key6"

        job_queue.labels = updated_queue_labels

        update_job_queue = router_client.update_queue(
            queue_id = dp_identifier,
            queue = job_queue
        )

        assert update_job_queue is not None
        JobQueueValidator.validate_queue(
            update_job_queue,
            identifier = dp_identifier,
            name = dp_identifier,
            labels = updated_queue_labels,
            distribution_policy_id = self.get_distribution_policy_id()
        )

    @pytest.mark.skip(reason = "Upsert queue not working correctly")
    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.after_test_execute('clean_up')
    def test_update_queue_w_kwargs(self, **kwargs):
        dp_identifier = "tst_update_q_w_kwargs"
        router_client: JobRouterAdministrationClient = self.create_admin_client()

        job_queue: RouterQueue = RouterQueue(
            distribution_policy_id = self.get_distribution_policy_id(),
            name = dp_identifier,
            labels = queue_labels,
        )

        job_queue = router_client.create_queue(
            queue_id = dp_identifier,
            queue = job_queue
        )

        # add for cleanup
        self.queue_ids[self._testMethodName] = [dp_identifier]

        assert job_queue is not None
        JobQueueValidator.validate_queue(
            job_queue,
            identifier = dp_identifier,
            name = dp_identifier,
            labels = queue_labels,
            distribution_policy_id = self.get_distribution_policy_id()
        )

        # Act
        job_queue = router_client.get_queue(identifier = dp_identifier)
        updated_queue_labels = dict(queue_labels)
        updated_queue_labels['key6'] = "Key6"

        job_queue.labels = updated_queue_labels

        update_job_queue = router_client.update_queue(
            dp_identifier,
            labels = updated_queue_labels
        )

        assert update_job_queue is not None
        JobQueueValidator.validate_queue(
            update_job_queue,
            identifier = dp_identifier,
            name = dp_identifier,
            labels = updated_queue_labels,
            distribution_policy_id = self.get_distribution_policy_id()
        )

    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.after_test_execute('clean_up')
    def test_get_queue(self, **kwargs):
        dp_identifier = "tst_get_q"
        router_client: JobRouterAdministrationClient = self.create_admin_client()

        job_queue: RouterQueue = RouterQueue(
            distribution_policy_id = self.get_distribution_policy_id(),
            name = dp_identifier,
            labels = queue_labels
        )

        job_queue = router_client.create_queue(
            queue_id = dp_identifier,
            queue = job_queue
        )

        # add for cleanup
        self.queue_ids[self._testMethodName] = [dp_identifier]

        assert job_queue is not None
        JobQueueValidator.validate_queue(
            job_queue,
            identifier = dp_identifier,
            name = dp_identifier,
            labels = queue_labels,
            distribution_policy_id = self.get_distribution_policy_id()
        )

        queried_job_queue = router_client.get_queue(
            queue_id = dp_identifier
        )

        JobQueueValidator.validate_queue(
            queried_job_queue,
            identifier = dp_identifier,
            name = dp_identifier,
            labels = queue_labels,
            distribution_policy_id = self.get_distribution_policy_id()
        )

    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.after_test_execute('clean_up')
    def test_delete_queue(self, **kwargs):
        dp_identifier = "tst_delete_q"
        router_client: JobRouterAdministrationClient = self.create_admin_client()

        job_queue: RouterQueue = RouterQueue(
            distribution_policy_id = self.get_distribution_policy_id(),
            name = dp_identifier,
            labels = queue_labels
        )

        job_queue = router_client.create_queue(
            queue_id = dp_identifier,
            queue = job_queue
        )

        assert job_queue is not None
        JobQueueValidator.validate_queue(
            job_queue,
            identifier = dp_identifier,
            name = dp_identifier,
            labels = queue_labels,
            distribution_policy_id = self.get_distribution_policy_id()
        )

        router_client.delete_queue(queue_id = dp_identifier)
        with pytest.raises(ResourceNotFoundError) as nfe:
            router_client.get_queue(queue_id = dp_identifier)
        assert nfe.value.reason == "Not Found"
        assert nfe.value.status_code == 404

    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.after_test_execute('clean_up')
    def test_list_queues(self, **kwargs):
        router_client: JobRouterAdministrationClient = self.create_admin_client()
        dp_identifiers = ["tst_list_q_1", "tst_list_q_2", "tst_list_q_3"]
        created_q_response = {}
        q_count = len(dp_identifiers)
        self.queue_ids[self._testMethodName] = []

        for identifier in dp_identifiers:
            job_queue: RouterQueue = RouterQueue(
                distribution_policy_id = self.get_distribution_policy_id(),
                name = identifier,
                labels = queue_labels
            )

            job_queue = router_client.create_queue(
                queue_id = identifier,
                queue = job_queue
            )

            # add for cleanup
            self.queue_ids[self._testMethodName].append(identifier)

            assert job_queue is not None

            JobQueueValidator.validate_queue(
                job_queue,
                identifier = identifier,
                name = identifier,
                labels = queue_labels,
                distribution_policy_id = self.get_distribution_policy_id()
            )
            created_q_response[job_queue.id] = job_queue

        job_queues = router_client.list_queues(results_per_page = 2)
        for job_queue_page in job_queues.by_page():
            list_of_queues = list(job_queue_page)
            assert len(list_of_queues) <= 2

            for q_item in list_of_queues:
                response_at_creation = created_q_response.get(q_item.queue.id, None)

                if not response_at_creation:
                    continue

                JobQueueValidator.validate_queue(
                    q_item.queue,
                    identifier = response_at_creation.id,
                    name = response_at_creation.name,
                    labels = response_at_creation.labels,
                    distribution_policy_id = response_at_creation.distribution_policy_id
                )
                q_count -= 1

        # all job_queues created were listed
        assert q_count == 0
