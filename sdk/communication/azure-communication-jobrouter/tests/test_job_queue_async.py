# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
from typing import Callable, Any, Coroutine, Awaitable

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from _decorators_async import RouterPreparersAsync
from _validators import JobQueueValidator
from _router_test_case_async import AsyncRouterRecordedTestCase
from _shared.asynctestcase import AsyncCommunicationTestCase
from azure.communication.jobrouter._shared.utils import parse_connection_str
from azure.core.exceptions import ResourceNotFoundError

from azure.communication.jobrouter.aio import JobRouterAdministrationClient
from azure.communication.jobrouter import (
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
class TestJobQueueAsync(AsyncRouterRecordedTestCase):
    async def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_client: JobRouterAdministrationClient = self.create_admin_client()
            async with router_client:
                if self._testMethodName in self.queue_ids \
                        and any(self.queue_ids[self._testMethodName]):
                    for _id in set(self.queue_ids[self._testMethodName]):
                        await router_client.delete_queue(queue_id = _id)

                if self._testMethodName in self.distribution_policy_ids \
                        and any(self.distribution_policy_ids[self._testMethodName]):
                    for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                        await router_client.delete_distribution_policy(distribution_policy_id = policy_id)

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

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_create_queue(self):
        dp_identifier = "test_create_q_async"
        router_client: JobRouterAdministrationClient = self.create_admin_client()

        async with router_client:
            job_queue: RouterQueue = RouterQueue(
                name = dp_identifier,
                labels = queue_labels,
                distribution_policy_id = self.get_distribution_policy_id()
            )

            job_queue = await router_client.create_queue(
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
    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_queue(self):
        dp_identifier = "tst_updated_q_async"
        router_client: JobRouterAdministrationClient = self.create_admin_client()

        async with router_client:
            job_queue: RouterQueue = RouterQueue(
                name = dp_identifier,
                labels = queue_labels,
                distribution_policy_id = self.get_distribution_policy_id()
            )

            job_queue = await router_client.create_queue(
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
            job_queue = await router_client.get_queue(identifier = dp_identifier)
            updated_queue_labels = dict(job_queue.labels)
            updated_queue_labels['key6'] = "Key6"

            job_queue.labels = updated_queue_labels

            update_job_queue = await router_client.update_queue(
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
    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_queue_w_kwargs(self):
        dp_identifier = "tst_updated_q_w_kwargs_async"
        router_client: JobRouterAdministrationClient = self.create_admin_client()

        async with router_client:
            job_queue: RouterQueue = RouterQueue(
                name = dp_identifier,
                labels = queue_labels,
                distribution_policy_id = self.get_distribution_policy_id()
            )

            job_queue = await router_client.create_queue(
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
            job_queue = await router_client.get_queue(identifier = dp_identifier)
            updated_queue_labels = dict(job_queue.labels)
            updated_queue_labels['key6'] = "Key6"

            job_queue.labels = updated_queue_labels

            update_job_queue = await router_client.update_queue(
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

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_get_queue(self):
        dp_identifier = "test_get_q_async"
        router_client: JobRouterAdministrationClient = self.create_admin_client()

        async with router_client:
            job_queue: RouterQueue = RouterQueue(
                name = dp_identifier,
                labels = queue_labels,
                distribution_policy_id = self.get_distribution_policy_id()
            )

            job_queue = await router_client.create_queue(
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

            queried_job_queue = await router_client.get_queue(
                queue_id = dp_identifier
            )

            JobQueueValidator.validate_queue(
                queried_job_queue,
                identifier = dp_identifier,
                name = dp_identifier,
                labels = queue_labels,
                distribution_policy_id = self.get_distribution_policy_id()
            )

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_delete_queue(self):
        dp_identifier = "test_delete_q_async"
        router_client: JobRouterAdministrationClient = self.create_admin_client()

        job_queue: RouterQueue = RouterQueue(
            name = dp_identifier,
            labels = queue_labels,
            distribution_policy_id = self.get_distribution_policy_id()
        )

        job_queue = await router_client.create_queue(
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

        await router_client.delete_queue(queue_id = dp_identifier)
        with pytest.raises(ResourceNotFoundError) as nfe:
            await router_client.get_queue(queue_id = dp_identifier)
        assert nfe.value.reason == "Not Found"
        assert nfe.value.status_code == 404

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_list_queues(self):
        router_client: JobRouterAdministrationClient = self.create_admin_client()
        dp_identifiers = ["test_list_q_1_async", "test_list_q_2_async", "test_list_q_3_async"]
        created_q_response = {}
        q_count = len(dp_identifiers)
        self.queue_ids[self._testMethodName] = []

        async with router_client:
            for identifier in dp_identifiers:
                job_queue: RouterQueue = RouterQueue(
                    name = identifier,
                    labels = queue_labels,
                    distribution_policy_id = self.get_distribution_policy_id()
                )

                job_queue = await router_client.create_queue(
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

            async for job_queue_page in job_queues.by_page():
                list_of_queues = [i async for i in job_queue_page]
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
