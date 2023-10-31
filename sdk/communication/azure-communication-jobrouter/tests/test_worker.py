# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from devtools_testutils import recorded_by_proxy
from _router_test_case import RouterRecordedTestCase
from _validators import RouterWorkerValidator
from _decorators import RouterPreparers
from azure.communication.jobrouter._shared.utils import parse_connection_str
from azure.core.exceptions import ResourceNotFoundError
from azure.communication.jobrouter import (
    JobRouterClient,
    JobRouterAdministrationClient,
)
from azure.communication.jobrouter.models import (
    RoundRobinMode,
    RouterWorker,
    RouterChannel,
    DistributionPolicy,
    RouterQueue,
)

worker_labels = {"key1": "WorkerKey", "key2": 10, "key3": True}

worker_tags = {
    "tag1": "WorkerGenericInfo",
}

worker_channel_configs = [
    RouterChannel(channel_id = "fakeChannel1", capacity_cost_per_job=10, max_number_of_jobs=10),
    RouterChannel(channel_id = "fakeChannel2", capacity_cost_per_job=90, max_number_of_jobs=1),
]

worker_capacity = 100


# The test class name needs to start with "Test" to get collected by pytest
class TestRouterWorker(RouterRecordedTestCase):
    def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_client: JobRouterClient = self.create_client()
            router_admin_client: JobRouterAdministrationClient = self.create_admin_client()
            if self._testMethodName in self.worker_ids and any(self.worker_ids[self._testMethodName]):
                for _id in set(self.worker_ids[self._testMethodName]):
                    router_client.delete_worker(worker_id=_id)

            if self._testMethodName in self.queue_ids and any(self.queue_ids[self._testMethodName]):
                for _id in set(self.queue_ids[self._testMethodName]):
                    router_admin_client.delete_queue(id=_id)

            if self._testMethodName in self.distribution_policy_ids and any(
                self.distribution_policy_ids[self._testMethodName]
            ):
                for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                    router_admin_client.delete_distribution_policy(id=policy_id)

    def get_distribution_policy_id(self):
        return self._testMethodName + "_tst_dp"

    def setup_distribution_policy(self):
        client: JobRouterAdministrationClient = self.create_admin_client()

        distribution_policy_id = self.get_distribution_policy_id()

        policy: DistributionPolicy = DistributionPolicy(
            offer_expires_after_seconds=10.0,
            mode=RoundRobinMode(min_concurrent_offers=1, max_concurrent_offers=1),
            name=distribution_policy_id,
        )

        distribution_policy = client.upsert_distribution_policy(distribution_policy_id, policy)

        # add for cleanup later
        if self._testMethodName in self.distribution_policy_ids:
            self.distribution_policy_ids[self._testMethodName] = self.distribution_policy_ids[
                self._testMethodName
            ].append(distribution_policy_id)
        else:
            self.distribution_policy_ids[self._testMethodName] = [distribution_policy_id]

    def get_job_queue_id(self):
        return self._testMethodName + "_tst_q"

    def setup_job_queue(self):
        client: JobRouterAdministrationClient = self.create_admin_client()
        job_queue_id = self.get_job_queue_id()

        job_queue: RouterQueue = RouterQueue(
            distribution_policy_id=self.get_distribution_policy_id(), name=job_queue_id, labels=worker_labels
        )

        job_queue = client.upsert_queue(job_queue_id, job_queue)

        # add for cleanup later
        if self._testMethodName in self.queue_ids:
            self.queue_ids[self._testMethodName] = self.queue_ids[self._testMethodName].append(job_queue_id)
        else:
            self.queue_ids[self._testMethodName] = [job_queue_id]

    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute("setup_distribution_policy")
    @RouterPreparers.before_test_execute("setup_job_queue")
    @RouterPreparers.after_test_execute("clean_up")
    def test_create_worker(self):
        w_identifier = "tst_create_w"
        router_client: JobRouterClient = self.create_client()
        worker_queues = [self.get_job_queue_id()]

        router_worker: RouterWorker = RouterWorker(
            capacity=worker_capacity,
            labels=worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

        router_worker = router_client.upsert_worker(w_identifier, router_worker)

        # add for cleanup
        self.worker_ids[self._testMethodName] = [w_identifier]

        assert router_worker is not None
        RouterWorkerValidator.validate_worker(
            router_worker,
            identifier=w_identifier,
            capacity=worker_capacity,
            labels=worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute("setup_distribution_policy")
    @RouterPreparers.before_test_execute("setup_job_queue")
    @RouterPreparers.after_test_execute("clean_up")
    def test_update_worker(self):
        w_identifier = "tst_update_w"
        router_client: JobRouterClient = self.create_client()
        worker_queues = [self.get_job_queue_id()]

        router_worker: RouterWorker = RouterWorker(
            capacity=worker_capacity,
            labels=worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

        router_worker = router_client.upsert_worker(w_identifier, router_worker)

        # add for cleanup
        self.worker_ids[self._testMethodName] = [w_identifier]

        assert router_worker is not None
        RouterWorkerValidator.validate_worker(
            router_worker,
            identifier=w_identifier,
            capacity=worker_capacity,
            labels=worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

        # Act
        router_worker.labels["FakeKey"] = "FakeWorkerValue"
        updated_worker_labels = router_worker.labels

        update_router_worker = router_client.upsert_worker(w_identifier, router_worker)

        assert update_router_worker is not None
        RouterWorkerValidator.validate_worker(
            update_router_worker,
            identifier=w_identifier,
            capacity=worker_capacity,
            labels=updated_worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute("setup_distribution_policy")
    @RouterPreparers.before_test_execute("setup_job_queue")
    @RouterPreparers.after_test_execute("clean_up")
    def test_update_worker_w_kwargs(self):
        w_identifier = "tst_update_w_kwargs"
        router_client: JobRouterClient = self.create_client()
        worker_queues = [self.get_job_queue_id()]

        router_worker: RouterWorker = RouterWorker(
            capacity=worker_capacity,
            labels=worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

        router_worker = router_client.upsert_worker(w_identifier, router_worker)

        # add for cleanup
        self.worker_ids[self._testMethodName] = [w_identifier]

        assert router_worker is not None
        RouterWorkerValidator.validate_worker(
            router_worker,
            identifier=w_identifier,
            capacity=worker_capacity,
            labels=worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

        # Act
        router_worker.labels["FakeKey"] = "FakeWorkerValue"
        updated_worker_labels = router_worker.labels

        update_router_worker = router_client.upsert_worker(w_identifier, labels=updated_worker_labels)

        assert update_router_worker is not None
        RouterWorkerValidator.validate_worker(
            update_router_worker,
            identifier=w_identifier,
            capacity=worker_capacity,
            labels=updated_worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute("setup_distribution_policy")
    @RouterPreparers.before_test_execute("setup_job_queue")
    @RouterPreparers.after_test_execute("clean_up")
    def test_get_worker(self):
        w_identifier = "tst_get_w"
        router_client: JobRouterClient = self.create_client()
        worker_queues = [self.get_job_queue_id()]

        router_worker: RouterWorker = RouterWorker(
            capacity=worker_capacity,
            labels=worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

        router_worker = router_client.upsert_worker(w_identifier, router_worker)

        # add for cleanup
        self.worker_ids[self._testMethodName] = [w_identifier]

        assert router_worker is not None
        RouterWorkerValidator.validate_worker(
            router_worker,
            identifier=w_identifier,
            capacity=worker_capacity,
            labels=worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

        queried_router_worker = router_client.get_worker(worker_id=w_identifier)

        RouterWorkerValidator.validate_worker(
            queried_router_worker,
            identifier=w_identifier,
            capacity=router_worker.capacity,
            labels=router_worker.labels,
            tags=router_worker.tags,
            queues=router_worker.queues,
            channels=router_worker.channels,
            available_for_offers=router_worker.available_for_offers,
        )

    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute("setup_distribution_policy")
    @RouterPreparers.before_test_execute("setup_job_queue")
    @RouterPreparers.after_test_execute("clean_up")
    def test_delete_worker(self):
        w_identifier = "tst_delete_w"
        router_client: JobRouterClient = self.create_client()
        worker_queues = [self.get_job_queue_id()]

        router_worker: RouterWorker = RouterWorker(
            capacity=worker_capacity,
            labels=worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

        router_worker = router_client.upsert_worker(w_identifier, router_worker)

        assert router_worker is not None
        RouterWorkerValidator.validate_worker(
            router_worker,
            identifier=w_identifier,
            capacity=worker_capacity,
            labels=worker_labels,
            tags=worker_tags,
            queues=worker_queues,
            channels=worker_channel_configs,
            available_for_offers=False,
        )

        router_client.delete_worker(worker_id=w_identifier)
        with pytest.raises(ResourceNotFoundError) as nfe:
            router_client.get_worker(worker_id=w_identifier)
        assert nfe.value.reason == "Not Found"
        assert nfe.value.status_code == 404

    @RouterPreparers.router_test_decorator
    @recorded_by_proxy
    @RouterPreparers.before_test_execute("setup_distribution_policy")
    @RouterPreparers.before_test_execute("setup_job_queue")
    @RouterPreparers.after_test_execute("clean_up")
    def test_list_workers(self):
        router_client: JobRouterClient = self.create_client()
        w_identifiers = ["tst_list_w_1", "tst_list_w_2", "tst_list_w_3"]
        worker_queues = [self.get_job_queue_id()]
        created_w_response = {}
        w_count = len(w_identifiers)
        self.worker_ids[self._testMethodName] = []

        for identifier in w_identifiers:
            router_worker: RouterWorker = RouterWorker(
                capacity=worker_capacity,
                labels=worker_labels,
                tags=worker_tags,
                queues=worker_queues,
                channels=worker_channel_configs,
                available_for_offers=False,
            )

            worker = router_client.upsert_worker(identifier, router_worker)

            # add for cleanup
            self.worker_ids[self._testMethodName].append(identifier)

            assert worker is not None

            RouterWorkerValidator.validate_worker(
                worker,
                identifier=identifier,
                capacity=worker_capacity,
                labels=worker_labels,
                tags=worker_tags,
                queues=worker_queues,
                channels=worker_channel_configs,
                available_for_offers=False,
            )
            created_w_response[worker.id] = worker

        router_workers = router_client.list_workers(
            results_per_page=2, state="inactive", queue_id=self.get_job_queue_id(), channel_id="fakeChannel1"
        )

        for worker_page in router_workers.by_page():
            list_of_workers = list(worker_page)
            assert len(list_of_workers) <= 2

            for w_item in list_of_workers:
                response_at_creation = created_w_response.get(w_item.id, None)

                if not response_at_creation:
                    continue

                RouterWorkerValidator.validate_worker(
                    w_item,
                    identifier=response_at_creation.id,
                    capacity=response_at_creation.capacity,
                    labels=response_at_creation.labels,
                    tags=response_at_creation.tags,
                    queues=response_at_creation.queues,
                    channels=response_at_creation.channels,
                    available_for_offers=response_at_creation.available_for_offers,
                )
                w_count -= 1

        # all job_queues created were listed
        assert w_count == 0
