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
from _validators import RouterJobValidator
from _helpers import _convert_str_to_datetime
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
    WorkerSelector,
    LabelOperator,
    QueueSelector,
    StaticQueueSelector,
    StaticRule,
    StaticWorkerSelector,
    JobStatus,
    JobStateSelector
)

job_labels = LabelCollection(
    {
        'key1': "JobKey",
        'key2': 10,
        'key3': True
    }
)

job_tags = LabelCollection(
    {
        'tag1': "WorkerGenericInfo",
    }
)

job_channel_references = ["fakeChannelRef1", "fakeChannelRef2"]

job_channel_ids = ["fakeChannelId1", "fakeChannelId2"]

job_priority = 10

job_disposition_code = "JobCancelledByUser"

job_requested_worker_selectors = [
    WorkerSelector(
        key = "FakeKey1",
        label_operator = LabelOperator.EQUAL,
        value = True
    ),
    WorkerSelector(
        key = "FakeKey2",
        label_operator = LabelOperator.NOT_EQUAL,
        value = False
    ),
    WorkerSelector(
        key = "FakeKey3",
        label_operator = LabelOperator.LESS_THAN,
        value = 10
    ),
    WorkerSelector(
        key = "FakeKey4",
        label_operator = LabelOperator.LESS_THAN_EQUAL,
        value = 10.01
    ),
    WorkerSelector(
        key = "FakeKey5",
        label_operator = LabelOperator.GREATER_THAN,
        value = 10
    ),
    WorkerSelector(
        key = "FakeKey6",
        label_operator = LabelOperator.GREATER_THAN_EQUAL,
        value = 10
    )
]


prioritization_rules = [
    StaticRule(value = 10),
]

cp_worker_selectors = [
    StaticWorkerSelector(
        label_selector = WorkerSelector(
            key = "FakeKeyFromCp",
            label_operator = LabelOperator.EQUAL,
            value = "FakeValue",
        )
    ),
]

expected_attached_worker_selectors = [
    WorkerSelector(
        key = "FakeKeyFromCp",
        label_operator = LabelOperator.EQUAL,
        value = "FakeValue",
    ),
]

test_timestamp = _convert_str_to_datetime("2022-05-13T23:59:04.5311999+07:00")
job_notes = {
    test_timestamp: "Fake notes attached to job"
}


# The test class name needs to start with "Test" to get collected by pytest
class TestRouterJob(RouterTestCase):
    def __init__(self, method_name):
        super(TestRouterJob, self).__init__(method_name)

        self.queue_ids = {}  # type: Dict[str, List[str]]
        self.distribution_policy_ids = {}  # type: Dict[str, List[str]]
        self.classification_policy_ids = {}  # type: Dict[str, List[str]]
        self.job_ids = {}  # type: Dict[str, List[str]]

    def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_client: RouterClient = self.create_client()
            if self._testMethodName in self.job_ids \
                    and any(self.job_ids[self._testMethodName]):
                for _id in set(self.job_ids[self._testMethodName]):
                    router_client.cancel_job_action(
                        identifier = _id,
                        disposition_code = "JobCancelledAsPartOfTestCleanUp",
                        note = f"Cancelling job after test cleanup after: {self._testMethodName}")
                    router_client.delete_job(identifier = _id)

            if self._testMethodName in self.classification_policy_ids \
                    and any(self.classification_policy_ids[self._testMethodName]):
                for policy_id in set(self.classification_policy_ids[self._testMethodName]):
                    router_client.delete_classification_policy(identifier = policy_id)

            if self._testMethodName in self.queue_ids \
                    and any(self.queue_ids[self._testMethodName]):
                for _id in set(self.queue_ids[self._testMethodName]):
                    router_client.delete_queue(identifier = _id)

            if self._testMethodName in self.distribution_policy_ids \
                    and any(self.distribution_policy_ids[self._testMethodName]):
                for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                    router_client.delete_distribution_policy(identifier = policy_id)

    def setUp(self):
        super(TestRouterJob, self).setUp()

        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint

    def tearDown(self):
        super(TestRouterJob, self).tearDown()

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
            labels = job_labels,
            distribution_policy_id = self.get_distribution_policy_id()
        )

        # add for cleanup later
        if self._testMethodName in self.queue_ids:
            self.queue_ids[self._testMethodName].append(job_queue_id)
        else:
            self.queue_ids[self._testMethodName] = [job_queue_id]

    def get_fallback_queue_id(self):
        return self._testMethodName + "_tst_flbk_q"  # cspell:disable-line

    def setup_fallback_queue(self):
        client: RouterClient = self.create_client()
        job_queue_id = self.get_fallback_queue_id()
        job_queue = client.create_queue(
            identifier = job_queue_id,
            name = job_queue_id,
            labels = job_labels,
            distribution_policy_id = self.get_distribution_policy_id()
        )

        # add for cleanup later
        if self._testMethodName in self.queue_ids:
            self.queue_ids[self._testMethodName].append(job_queue_id)
        else:
            self.queue_ids[self._testMethodName] = [job_queue_id]

    def get_classification_policy_id(self):
        return self._testMethodName + "_tst_cp"

    def setup_classification_policy(self):
        client: RouterClient = self.create_client()

        cp_queue_selectors = [
            StaticQueueSelector(
                label_selector = QueueSelector(
                    key = "Id", label_operator = LabelOperator.EQUAL, value = self.get_job_queue_id()
                )
            ),
        ]

        cp_id = self.get_classification_policy_id()
        job_queue = client.create_classification_policy(
            identifier = cp_id,
            name = cp_id,
            fallback_queue_id = self.get_fallback_queue_id(),
            queue_selectors = cp_queue_selectors,
            prioritization_rule = prioritization_rules[0],
            worker_selectors = cp_worker_selectors
        )

        # add for cleanup later
        if self._testMethodName in self.classification_policy_ids:
            self.classification_policy_ids[self._testMethodName].append(cp_id)
        else:
            self.classification_policy_ids[self._testMethodName] = [cp_id]

    def validate_job_is_queued(
            self,
            identifier,
            **kwargs
    ):
        router_client: RouterClient = self.create_client()
        router_job = router_client.get_job(identifier = identifier)
        assert router_job.job_status == JobStatus.QUEUED

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_create_job_direct_q(self):
        job_identifier = "tst_create_job_man"
        router_client: RouterClient = self.create_client()

        router_job = router_client.create_job(
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            queue_id = self.get_job_queue_id(),
            priority = job_priority,
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        # add for cleanup
        self.job_ids[self._testMethodName] = [job_identifier]

        assert router_job is not None
        RouterJobValidator.validate_job(
            router_job,
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            queue_id = self.get_job_queue_id(),
            priority = job_priority,
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        assert router_job.job_status == JobStatus.CREATED

        self._poll_until_no_exception(
            self.validate_job_is_queued,
            Exception,
            job_identifier)

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_update_job_direct_q(self):
        job_identifier = "tst_update_job_man"
        router_client: RouterClient = self.create_client()

        router_job = router_client.create_job(
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            queue_id = self.get_job_queue_id(),
            priority = job_priority,
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        # add for cleanup
        self.job_ids[self._testMethodName] = [job_identifier]

        assert router_job is not None
        RouterJobValidator.validate_job(
            router_job,
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            queue_id = self.get_job_queue_id(),
            priority = job_priority,
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        assert router_job.job_status == JobStatus.CREATED

        self._poll_until_no_exception(
            self.validate_job_is_queued,
            Exception,
            job_identifier)

        # Act
        router_job.labels['FakeKey'] = "FakeWorkerValue"
        updated_job_labels = router_job.labels

        update_router_job = router_client.update_job(
            identifier = job_identifier,
            router_job = router_job
        )

        assert update_router_job is not None
        RouterJobValidator.validate_job(
            update_router_job,
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            queue_id = self.get_job_queue_id(),
            priority = job_priority,
            requested_worker_selectors = job_requested_worker_selectors,
            labels = updated_job_labels,
            tags = job_tags,
            notes = job_notes
        )

        # updating labels does not change job status
        assert update_router_job.job_status == JobStatus.QUEUED

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_get_job_direct_q(self):
        job_identifier = "tst_get_job_man"
        router_client: RouterClient = self.create_client()

        router_job = router_client.create_job(
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            queue_id = self.get_job_queue_id(),
            priority = job_priority,
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        # add for cleanup
        self.job_ids[self._testMethodName] = [job_identifier]

        assert router_job is not None
        RouterJobValidator.validate_job(
            router_job,
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            queue_id = self.get_job_queue_id(),
            priority = job_priority,
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        assert router_job.job_status == JobStatus.CREATED

        self._poll_until_no_exception(
            self.validate_job_is_queued,
            Exception,
            job_identifier)

        queried_router_job = router_client.get_job(
            identifier = job_identifier
        )

        RouterJobValidator.validate_job(
            queried_router_job,
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            queue_id = self.get_job_queue_id(),
            priority = job_priority,
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    @RouterPreparers.before_test_execute('setup_fallback_queue')
    @RouterPreparers.before_test_execute('setup_classification_policy')
    def test_create_job_w_cp(self):
        job_identifier = "tst_create_job_cp"
        router_client: RouterClient = self.create_client()

        router_job = router_client.create_job(
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            classification_policy_id = self.get_classification_policy_id(),
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        # add for cleanup
        self.job_ids[self._testMethodName] = [job_identifier]

        assert router_job is not None
        RouterJobValidator.validate_job(
            router_job,
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            classification_policy_id = self.get_classification_policy_id(),
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        assert router_job.job_status == JobStatus.PENDING_CLASSIFICATION

        self._poll_until_no_exception(
            self.validate_job_is_queued,
            Exception,
            job_identifier)

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    @RouterPreparers.before_test_execute('setup_fallback_queue')
    @RouterPreparers.before_test_execute('setup_classification_policy')
    def test_update_job_w_cp(self):
        job_identifier = "tst_update_job_cp"
        router_client: RouterClient = self.create_client()

        router_job = router_client.create_job(
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            classification_policy_id = self.get_classification_policy_id(),
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        # add for cleanup
        self.job_ids[self._testMethodName] = [job_identifier]

        assert router_job is not None
        RouterJobValidator.validate_job(
            router_job,
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            classification_policy_id = self.get_classification_policy_id(),
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        assert router_job.job_status == JobStatus.PENDING_CLASSIFICATION

        self._poll_until_no_exception(
            self.validate_job_is_queued,
            Exception,
            job_identifier)

        # Act
        router_job.labels['FakeKey'] = "FakeWorkerValue"
        updated_job_labels = router_job.labels

        update_router_job = router_client.update_job(
            identifier = job_identifier,
            router_job = router_job
        )

        assert update_router_job is not None
        RouterJobValidator.validate_job(
            update_router_job,
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            classification_policy_id = self.get_classification_policy_id(),
            requested_worker_selectors = job_requested_worker_selectors,
            labels = updated_job_labels,
            tags = job_tags,
            notes = job_notes
        )

        # updating labels reverts job status to pending classification
        assert update_router_job.job_status == JobStatus.PENDING_CLASSIFICATION

        self._poll_until_no_exception(
            self.validate_job_is_queued,
            Exception,
            job_identifier)

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    @RouterPreparers.before_test_execute('setup_fallback_queue')
    @RouterPreparers.before_test_execute('setup_classification_policy')
    def test_get_job_w_cp(self):
        job_identifier = "tst_get_job_cp"
        router_client: RouterClient = self.create_client()

        router_job = router_client.create_job(
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            classification_policy_id = self.get_classification_policy_id(),
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        # add for cleanup
        self.job_ids[self._testMethodName] = [job_identifier]

        assert router_job is not None
        RouterJobValidator.validate_job(
            router_job,
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            classification_policy_id = self.get_classification_policy_id(),
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        assert router_job.job_status == JobStatus.PENDING_CLASSIFICATION

        self._poll_until_no_exception(
            self.validate_job_is_queued,
            Exception,
            job_identifier)

        queried_router_job = router_client.get_job(
            identifier = job_identifier
        )

        RouterJobValidator.validate_job(
            queried_router_job,
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            queue_id = self.get_job_queue_id(),
            priority = job_priority,
            requested_worker_selectors = job_requested_worker_selectors,
            attached_worker_selectors = expected_attached_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        assert queried_router_job.job_status == JobStatus.QUEUED

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_delete_job(self):
        job_identifier = "tst_del_job_man"
        router_client: RouterClient = self.create_client()

        router_job = router_client.create_job(
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            queue_id = self.get_job_queue_id(),
            priority = job_priority,
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        assert router_job is not None
        RouterJobValidator.validate_job(
            router_job,
            identifier = job_identifier,
            channel_reference = job_channel_references[0],
            channel_id = job_channel_ids[0],
            queue_id = self.get_job_queue_id(),
            priority = job_priority,
            requested_worker_selectors = job_requested_worker_selectors,
            labels = job_labels,
            tags = job_tags,
            notes = job_notes
        )

        assert router_job.job_status == JobStatus.CREATED

        self._poll_until_no_exception(
            self.validate_job_is_queued,
            Exception,
            job_identifier)

        # job needs to be in a termination state before it can be deleted
        router_client.cancel_job_action(identifier = job_identifier)
        router_client.delete_job(identifier = job_identifier)
        with pytest.raises(ResourceNotFoundError) as nfe:
            router_client.get_job(identifier = job_identifier)
            self.job_ids.pop(self._testMethodName, None)
        assert nfe.value.reason == "Not Found"
        assert nfe.value.status_code == 404

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_list_jobs(self):
        router_client: RouterClient = self.create_client()
        job_identifiers = ["tst_list_job_1", "tst_list_job_2", "tst_list_job_3"]

        created_job_response = {}
        job_count = len(job_identifiers)
        self.job_ids[self._testMethodName] = []

        for identifier in job_identifiers:
            router_job = router_client.create_job(
                identifier = identifier,
                channel_reference = job_channel_references[0],
                channel_id = job_channel_ids[0],
                queue_id = self.get_job_queue_id(),
                priority = job_priority,
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes
            )

            # add for cleanup
            self.job_ids[self._testMethodName].append(identifier)

            assert router_job is not None

            RouterJobValidator.validate_job(
                router_job,
                identifier = identifier,
                channel_reference = job_channel_references[0],
                channel_id = job_channel_ids[0],
                queue_id = self.get_job_queue_id(),
                priority = job_priority,
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes
            )

            assert router_job.job_status == JobStatus.CREATED

            self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                identifier)

            created_job_response[router_job.id] = router_job

        router_jobs = router_client.list_jobs(
            results_per_page = 2,
            status = JobStateSelector.QUEUED,
            queue_id = self.get_job_queue_id(),
            channel_id = job_channel_ids[0]
        )

        for router_job_page in router_jobs.by_page():
            list_of_jobs = list(router_job_page)
            assert len(list_of_jobs) <= 2

            for j in list_of_jobs:
                response_at_creation = created_job_response.get(j.id, None)

                if not response_at_creation:
                    continue

                RouterJobValidator.validate_job(
                    j,
                    identifier = response_at_creation.id,
                    channel_reference = response_at_creation.channel_reference,
                    channel_id = response_at_creation.channel_id,
                    queue_id = response_at_creation.queue_id,
                    priority = response_at_creation.priority,
                    requested_worker_selectors = response_at_creation.requested_worker_selectors,
                    labels = response_at_creation.labels,
                    tags = response_at_creation.tags,
                    notes = response_at_creation.notes,
                )
                job_count -= 1

        # all job_queues created were listed
        assert job_count == 0

