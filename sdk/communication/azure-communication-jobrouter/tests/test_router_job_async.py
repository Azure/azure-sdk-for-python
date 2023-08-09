# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import datetime
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.serialization import _datetime_as_isostr  # pylint:disable=protected-access
from _router_test_case_async import (
    AsyncRouterRecordedTestCase
)
from _validators import RouterJobValidator
from _helpers import _convert_str_to_datetime
from _decorators_async import RouterPreparersAsync
from _shared.asynctestcase import AsyncCommunicationTestCase
from azure.communication.jobrouter._shared.utils import parse_connection_str
from azure.core.exceptions import ResourceNotFoundError

from azure.communication.jobrouter.aio import (
    JobRouterClient,
    JobRouterAdministrationClient,
)
from azure.communication.jobrouter import (
    RoundRobinMode,
    RouterWorker,
    ChannelConfiguration,
    RouterWorkerSelector,
    LabelOperator,
    RouterQueueSelector,
    StaticQueueSelectorAttachment,
    StaticRouterRule,
    StaticWorkerSelectorAttachment,
    RouterJobStatus,
    DistributionPolicy,
    RouterQueue,
    ClassificationPolicy,
    RouterJob,
    JobMatchingMode,
    ScheduleAndSuspendMode
)

job_labels = {
        'key1': "JobKey",
        'key2': 10,
        'key3': True
    }

job_tags = {
        'tag1': "WorkerGenericInfo",
    }

job_channel_references = ["fakeChannelRef1", "fakeChannelRef2"]

job_channel_ids = ["fakeChannelId1", "fakeChannelId2"]

job_priority = 10

job_disposition_code = "JobCancelledByUser"

job_requested_worker_selectors = [
    RouterWorkerSelector(
        key = "FakeKey1",
        label_operator = LabelOperator.EQUAL,
        value = True
    ),
    RouterWorkerSelector(
        key = "FakeKey2",
        label_operator = LabelOperator.NOT_EQUAL,
        value = False
    ),
    RouterWorkerSelector(
        key = "FakeKey3",
        label_operator = LabelOperator.LESS_THAN,
        value = 10
    ),
    RouterWorkerSelector(
        key = "FakeKey4",
        label_operator = LabelOperator.LESS_THAN_EQUAL,
        value = 10.01
    ),
    RouterWorkerSelector(
        key = "FakeKey5",
        label_operator = LabelOperator.GREATER_THAN,
        value = 10
    ),
    RouterWorkerSelector(
        key = "FakeKey6",
        label_operator = LabelOperator.GREATER_THAN_EQUAL,
        value = 10
    )
]


prioritization_rules = [
    StaticRouterRule(value = 10),
]

cp_worker_selectors = [
    StaticWorkerSelectorAttachment(
        worker_selector = RouterWorkerSelector(
            key = "FakeKeyFromCp",
            label_operator = LabelOperator.EQUAL,
            value = "FakeValue",
        )
    ),
]

expected_attached_worker_selectors = [
    RouterWorkerSelector(
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
class TestRouterJobAsync(AsyncRouterRecordedTestCase):
    async def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_client: JobRouterClient = self.create_client()
            router_admin_client: JobRouterAdministrationClient = self.create_admin_client()
            async with router_client:
                async with router_admin_client:
                    if self._testMethodName in self.job_ids \
                            and any(self.job_ids[self._testMethodName]):
                        for _id in set(self.job_ids[self._testMethodName]):
                            await self.clean_up_job(job_id = _id)

                    if self._testMethodName in self.classification_policy_ids \
                            and any(self.classification_policy_ids[self._testMethodName]):
                        for policy_id in set(self.classification_policy_ids[self._testMethodName]):
                            await router_admin_client.delete_classification_policy(classification_policy_id = policy_id)

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
                labels = job_labels,
                distribution_policy_id = self.get_distribution_policy_id()
            )

            job_queue = await client.create_queue(
                queue_id = job_queue_id,
                queue = job_queue
            )

            # add for cleanup later
            if self._testMethodName in self.queue_ids:
                self.queue_ids[self._testMethodName].append(job_queue_id)
            else:
                self.queue_ids[self._testMethodName] = [job_queue_id]

    def get_fallback_queue_id(self):
        return self._testMethodName + "_tst_flbk_q_async"  # cspell:disable-line

    async def setup_fallback_queue(self):
        client: JobRouterAdministrationClient = self.create_admin_client()

        async with client:
            job_queue_id = self.get_fallback_queue_id()

            job_queue: RouterQueue = RouterQueue(
                name = job_queue_id,
                labels = job_labels,
                distribution_policy_id = self.get_distribution_policy_id()
            )

            job_queue = await client.create_queue(
                queue_id = job_queue_id,
                queue = job_queue
            )

            # add for cleanup later
            if self._testMethodName in self.queue_ids:
                self.queue_ids[self._testMethodName].append(job_queue_id)
            else:
                self.queue_ids[self._testMethodName] = [job_queue_id]

    def get_classification_policy_id(self):
        return self._testMethodName + "_tst_cp"

    async def setup_classification_policy(self):
        client: JobRouterAdministrationClient = self.create_admin_client()

        async with client:
            cp_queue_selectors = [
                StaticQueueSelectorAttachment(
                    queue_selector = RouterQueueSelector(
                        key = "Id", label_operator = LabelOperator.EQUAL, value = self.get_job_queue_id()
                    )
                ),
            ]

            cp_id = self.get_classification_policy_id()

            classification_policy: ClassificationPolicy = ClassificationPolicy(
                name = cp_id,
                fallback_queue_id = self.get_fallback_queue_id(),
                queue_selectors = cp_queue_selectors,
                prioritization_rule = prioritization_rules[0],
                worker_selectors = cp_worker_selectors
            )

            cp = await client.create_classification_policy(
                classification_policy_id = cp_id,
                classification_policy = classification_policy
            )

            # add for cleanup later
            if self._testMethodName in self.classification_policy_ids:
                self.classification_policy_ids[self._testMethodName].append(cp_id)
            else:
                self.classification_policy_ids[self._testMethodName] = [cp_id]

    async def validate_job_is_queued(
            self,
            identifier,  # type: str
            **kwargs,  # type: Any
    ):
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job = await router_client.get_job(job_id = identifier)
            assert router_job.status == RouterJobStatus.QUEUED

    async def validate_job_is_scheduled(
            self,
            identifier,
            **kwargs
    ):
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job = await router_client.get_job(job_id = identifier)
            assert router_job.status == RouterJobStatus.SCHEDULED


    async def validate_job_is_cancelled(
            self,
            identifier,
            **kwargs
    ):
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job = await router_client.get_job(job_id = identifier)
            assert router_job.status == RouterJobStatus.CANCELLED

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_create_job_direct_q(self):
        job_identifier = "tst_create_job_man_async"
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job: RouterJob = RouterJob(
                channel_reference = job_channel_references[0],
                channel_id = job_channel_ids[0],
                queue_id = self.get_job_queue_id(),
                priority = job_priority,
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes
            )

            router_job = await router_client.create_job(
                job_id = job_identifier,
                router_job = router_job
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

            assert router_job.status == RouterJobStatus.CREATED

            await self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                job_identifier)

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_create_scheduled_job(self, **kwargs):
        recorded_variables = kwargs.pop('variables', {})
        scheduled_time = datetime.datetime.utcnow() + datetime.timedelta(0, 30)
        scheduled_time_utc = recorded_variables.setdefault("scheduled_time_utc", _datetime_as_isostr(scheduled_time))

        matching_mode = JobMatchingMode(
            schedule_and_suspend_mode = ScheduleAndSuspendMode(
                schedule_at = recorded_variables["scheduled_time_utc"]))

        job_identifier = "tst_create_sch_job_async"
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job: RouterJob = RouterJob(
                channel_id = job_channel_ids[0],
                channel_reference = job_channel_references[0],
                queue_id = self.get_job_queue_id(),
                priority = job_priority,
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes,
                matching_mode = matching_mode
            )

            router_job = await router_client.create_job(
                job_id = job_identifier,
                router_job = router_job
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
                notes = job_notes,
                matching_mode = matching_mode
            )

            assert router_job.status == RouterJobStatus.PENDING_SCHEDULE

            await self._poll_until_no_exception(
                self.validate_job_is_scheduled,
                Exception,
                job_identifier)

            return recorded_variables

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_job_direct_q(self):
        job_identifier = "tst_update_job_man_async"
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job: RouterJob = RouterJob(
                channel_reference = job_channel_references[0],
                channel_id = job_channel_ids[0],
                queue_id = self.get_job_queue_id(),
                priority = job_priority,
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes
            )

            router_job = await router_client.create_job(
                job_id = job_identifier,
                router_job = router_job
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

            await self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                job_identifier)

            # Act
            router_job.labels['FakeKey'] = "FakeWorkerValue"
            updated_job_labels = router_job.labels

            update_router_job = await router_client.update_job(
                job_identifier,
                router_job
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
            assert update_router_job.status == RouterJobStatus.QUEUED

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_job_direct_q_w_kwargs(self):
        job_identifier = "tst_update_job_man_w_kwargs_async"
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job: RouterJob = RouterJob(
                channel_reference = job_channel_references[0],
                channel_id = job_channel_ids[0],
                queue_id = self.get_job_queue_id(),
                priority = job_priority,
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes
            )

            router_job = await router_client.create_job(
                job_id = job_identifier,
                router_job = router_job
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

            await self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                job_identifier)

            # Act
            router_job.labels['FakeKey'] = "FakeWorkerValue"
            updated_job_labels = router_job.labels

            update_router_job = await router_client.update_job(
                job_id = job_identifier,
                labels = updated_job_labels
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
            assert update_router_job.status == RouterJobStatus.QUEUED

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_get_job_direct_q(self):
        job_identifier = "tst_get_job_man_async"
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job: RouterJob = RouterJob(
                channel_reference = job_channel_references[0],
                channel_id = job_channel_ids[0],
                queue_id = self.get_job_queue_id(),
                priority = job_priority,
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes
            )

            router_job = await router_client.create_job(
                job_id = job_identifier,
                router_job = router_job
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

            assert router_job.status == RouterJobStatus.CREATED

            await self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                job_identifier)

            queried_router_job = await router_client.get_job(
                job_id = job_identifier
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

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_fallback_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_classification_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_create_job_w_cp(self):
        job_identifier = "tst_create_job_cp_async"
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job: RouterJob = RouterJob(
                channel_reference = job_channel_references[0],
                channel_id = job_channel_ids[0],
                classification_policy_id = self.get_classification_policy_id(),
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes
            )

            router_job = await router_client.create_job(
                job_id = job_identifier,
                router_job = router_job
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

            assert router_job.status == RouterJobStatus.PENDING_CLASSIFICATION

            await self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                job_identifier)

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_fallback_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_classification_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_job_w_cp(self):
        job_identifier = "tst_update_job_cp_async"
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job: RouterJob = RouterJob(
                channel_reference = job_channel_references[0],
                channel_id = job_channel_ids[0],
                classification_policy_id = self.get_classification_policy_id(),
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes
            )

            router_job = await router_client.create_job(
                job_id = job_identifier,
                router_job = router_job
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

            assert router_job.status == RouterJobStatus.PENDING_CLASSIFICATION

            await self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                job_identifier)

            # Act
            router_job.labels['FakeKey'] = "FakeWorkerValue"
            updated_job_labels = router_job.labels

            update_router_job = await router_client.update_job(
                job_identifier,
                router_job
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
            assert update_router_job.status == RouterJobStatus.PENDING_CLASSIFICATION

            await self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                job_identifier)

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_fallback_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_classification_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_job_w_cp_w_kwargs(self):
        job_identifier = "tst_update_job_cp_w_kwargs_async"
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job: RouterJob = RouterJob(
                channel_reference = job_channel_references[0],
                channel_id = job_channel_ids[0],
                classification_policy_id = self.get_classification_policy_id(),
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes
            )

            router_job = await router_client.create_job(
                job_id = job_identifier,
                router_job = router_job
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

            assert router_job.status == RouterJobStatus.PENDING_CLASSIFICATION

            await self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                job_identifier)

            # Act
            router_job.labels['FakeKey'] = "FakeWorkerValue"
            updated_job_labels = router_job.labels

            update_router_job = await router_client.update_job(
                job_identifier,
                labels = updated_job_labels
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
            assert update_router_job.status == RouterJobStatus.PENDING_CLASSIFICATION

            await self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                job_identifier)

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_fallback_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_classification_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_get_job_w_cp(self):
        job_identifier = "tst_get_job_cp_async"
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job: RouterJob = RouterJob(
                channel_reference = job_channel_references[0],
                channel_id = job_channel_ids[0],
                classification_policy_id = self.get_classification_policy_id(),
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes
            )

            router_job = await router_client.create_job(
                job_id = job_identifier,
                router_job = router_job
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

            assert router_job.status == RouterJobStatus.PENDING_CLASSIFICATION

            await self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                job_identifier)

            queried_router_job = await router_client.get_job(
                job_id = job_identifier
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

            assert queried_router_job.status == RouterJobStatus.QUEUED

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_delete_job(self):
        job_identifier = "tst_del_job_man_async"
        router_client: JobRouterClient = self.create_client()

        async with router_client:
            router_job: RouterJob = RouterJob(
                channel_reference = job_channel_references[0],
                channel_id = job_channel_ids[0],
                queue_id = self.get_job_queue_id(),
                priority = job_priority,
                requested_worker_selectors = job_requested_worker_selectors,
                labels = job_labels,
                tags = job_tags,
                notes = job_notes
            )

            router_job = await router_client.create_job(
                job_id = job_identifier,
                router_job = router_job
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

            assert router_job.status == RouterJobStatus.CREATED

            await self._poll_until_no_exception(
                self.validate_job_is_queued,
                Exception,
                job_identifier)

            # job needs to be in a termination state before it can be deleted
            await router_client.cancel_job(job_id = job_identifier)
            await router_client.delete_job(job_id = job_identifier)
            with pytest.raises(ResourceNotFoundError) as nfe:
                await router_client.get_job(job_id = job_identifier)
                self.job_ids.pop(self._testMethodName, None)
            assert nfe.value.reason == "Not Found"
            assert nfe.value.status_code == 404

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_list_jobs(self):
        router_client: JobRouterClient = self.create_client()
        job_identifiers = ["tst_list_job_1_async", "tst_list_job_2_async", "tst_list_job_3_async"]

        created_job_response = {}
        job_count = len(job_identifiers)
        self.job_ids[self._testMethodName] = []

        async with router_client:
            for identifier in job_identifiers:
                router_job: RouterJob = RouterJob(
                    channel_reference = job_channel_references[0],
                    channel_id = job_channel_ids[0],
                    queue_id = self.get_job_queue_id(),
                    priority = job_priority,
                    requested_worker_selectors = job_requested_worker_selectors,
                    labels = job_labels,
                    tags = job_tags,
                    notes = job_notes
                )

                router_job = await router_client.create_job(
                    job_id = identifier,
                    router_job = router_job
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

                await self._poll_until_no_exception(
                    self.validate_job_is_queued,
                    Exception,
                    identifier)

                created_job_response[router_job.id] = router_job

            router_jobs = router_client.list_jobs(
                results_per_page = 3,
                status = RouterJobStatus.QUEUED,
                queue_id = self.get_job_queue_id(),
                channel_id = job_channel_ids[0]
            )

            async for router_job_page in router_jobs.by_page():
                list_of_jobs = [i async for i in router_job_page]
                assert len(list_of_jobs) <= 3

                for j_item in list_of_jobs:
                    response_at_creation = created_job_response.get(j_item.job.id, None)

                    if not response_at_creation:
                        continue

                    RouterJobValidator.validate_job(
                        j_item.job,
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

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_list_sch_jobs(self, **kwargs):
        recorded_variables = kwargs.pop('variables', {})
        scheduled_time = datetime.datetime.utcnow() + datetime.timedelta(0, 30)
        scheduled_time_utc = recorded_variables.setdefault("scheduled_time_utc", _datetime_as_isostr(scheduled_time))

        matching_mode = JobMatchingMode(
            schedule_and_suspend_mode = ScheduleAndSuspendMode(
                schedule_at = recorded_variables["scheduled_time_utc"]))

        router_client: JobRouterClient = self.create_client()
        job_identifiers = ["tst_list_sch_job_1_async", "tst_list_sch_job_2_async"]

        created_job_response = {}
        job_count = len(job_identifiers)
        self.job_ids[self._testMethodName] = []

        async with router_client:
            for identifier in job_identifiers:
                router_job: RouterJob = RouterJob(
                    channel_reference = job_channel_references[0],
                    channel_id = job_channel_ids[0],
                    queue_id = self.get_job_queue_id(),
                    priority = job_priority,
                    requested_worker_selectors = job_requested_worker_selectors,
                    labels = job_labels,
                    tags = job_tags,
                    notes = job_notes,
                    matching_mode = matching_mode
                )

                router_job = await router_client.create_job(
                    job_id = identifier,
                    router_job = router_job
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
                    notes = job_notes,
                    matching_mode = matching_mode
                )

                await self._poll_until_no_exception(
                    self.validate_job_is_scheduled,
                    Exception,
                    identifier)

                created_job_response[router_job.id] = router_job

            router_jobs = router_client.list_jobs(
                results_per_page = 2,
                status = RouterJobStatus.SCHEDULED,
                queue_id = self.get_job_queue_id(),
                scheduled_before = recorded_variables["scheduled_time_utc"],
                channel_id = job_channel_ids[0],
            )

            async for router_job_page in router_jobs.by_page():
                list_of_jobs = [i async for i in router_job_page]
                assert len(list_of_jobs) <= 2

                for j_item in list_of_jobs:
                    response_at_creation = created_job_response.get(j_item.job.id, None)

                    if not response_at_creation:
                        continue

                    RouterJobValidator.validate_job(
                        j_item.job,
                        identifier = response_at_creation.id,
                        channel_reference = response_at_creation.channel_reference,
                        channel_id = response_at_creation.channel_id,
                        queue_id = response_at_creation.queue_id,
                        priority = response_at_creation.priority,
                        requested_worker_selectors = response_at_creation.requested_worker_selectors,
                        labels = response_at_creation.labels,
                        tags = response_at_creation.tags,
                        notes = response_at_creation.notes,
                        matching_mode = response_at_creation.matching_mode
                    )
                    job_count -= 1

            # all job_queues created were listed
            assert job_count == 0
            return recorded_variables

