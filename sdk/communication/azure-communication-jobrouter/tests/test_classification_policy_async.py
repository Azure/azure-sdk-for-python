# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import ResourceNotFoundError
from _router_test_case_async import AsyncRouterRecordedTestCase
from _shared.asynctestcase import AsyncCommunicationTestCase
from _decorators_async import RouterPreparersAsync
from _validators import ClassificationPolicyValidator
from azure.communication.jobrouter._shared.utils import parse_connection_str
from azure.communication.jobrouter.aio import JobRouterAdministrationClient
from azure.communication.jobrouter import (
    RoundRobinMode,
    ClassificationPolicy,
    LabelOperator,
    RouterQueueSelector,
    StaticQueueSelectorAttachment,
    ConditionalQueueSelectorAttachment,
    RuleEngineQueueSelectorAttachment,
    PassThroughQueueSelectorAttachment,
    QueueWeightedAllocation,
    WeightedAllocationQueueSelectorAttachment,
    RouterWorkerSelector,
    StaticWorkerSelectorAttachment,
    ConditionalWorkerSelectorAttachment,
    RuleEngineWorkerSelectorAttachment,
    PassThroughWorkerSelectorAttachment,
    WorkerWeightedAllocation,
    WeightedAllocationWorkerSelectorAttachment,
    StaticRouterRule,
    ExpressionRouterRule,
    FunctionRouterRule,
    FunctionRouterRuleCredential,
    DistributionPolicy,
    RouterQueue,
)


queue_labels = {
        'key1': "QueueKey",
        'key2': 10,
        'key3': True,
        'key4': False,
        'key5': 10.1
    }

queue_selectors = [
    StaticQueueSelectorAttachment(
        queue_selector = RouterQueueSelector(
            key = "test_key", label_operator = LabelOperator.EQUAL, value = "test_value"
        )
    ),
    ConditionalQueueSelectorAttachment(
        condition = StaticRouterRule(value = True),
        queue_selectors = [
            RouterQueueSelector(
                key = "test_key", label_operator = LabelOperator.EQUAL, value = "test_value"
            )
        ]
    ),
    # ## TODO: Bugfix required
    # RuleEngineQueueSelectorAttachment(
    #     rule = StaticRouterRule(value = [
    #         RouterQueueSelector(
    #             key = "test_key", label_operator = LabelOperator.EQUAL, value = "test_value"
    #         )]
    #     )
    # ),
    PassThroughQueueSelectorAttachment(
        key = "testKey",
        label_operator = LabelOperator.EQUAL
    ),
    WeightedAllocationQueueSelectorAttachment(
        allocations = [
            QueueWeightedAllocation(
                weight = 1.0,
                queue_selectors = [
                    RouterQueueSelector(
                        key = "test_key", label_operator = LabelOperator.EQUAL, value = "test_value"
                    )
                ]
            )
        ]
    )
]

prioritization_rules = [
    StaticRouterRule(value = 1),
    ExpressionRouterRule(expression = "1"),
    FunctionRouterRule(
        function_uri = "https://fake.azurewebsites.net/fakeRule",
        credential = FunctionRouterRuleCredential(function_key = "fakeKey"))
]

worker_selectors = [
    StaticWorkerSelectorAttachment(
        worker_selector = RouterWorkerSelector(
            key = "test_key",
            label_operator = LabelOperator.EQUAL,
            value = "test_value",
            expires_after_seconds = 10.0,
            expedite = False
        )
    ),
    ConditionalWorkerSelectorAttachment(
        condition = StaticRouterRule(value = True),
        worker_selectors = [
            RouterWorkerSelector(
                key = "test_key",
                label_operator = LabelOperator.EQUAL,
                value = "test_value",
                expires_after_seconds = 10.0,
                expedite = False
            )
        ]
    ),
    # ## TODO: Bugfix required
    # RuleEngineWorkerSelectorAttachment(
    #     rule = StaticRouterRule(value = [
    #         RouterWorkerSelector(
    #             key = "test_key",
    #             label_operator = LabelOperator.EQUAL,
    #             value = "test_value",
    #             expires_after_seconds = 10.0,
    #             expedite = False
    #         )]
    #     )
    # ),
    PassThroughWorkerSelectorAttachment(
        key = "testKey",
        label_operator = LabelOperator.EQUAL
    ),
    WeightedAllocationWorkerSelectorAttachment(
        allocations = [
            WorkerWeightedAllocation(
                weight = 1.0,
                worker_selectors = [
                    RouterWorkerSelector(
                        key = "test_key",
                        label_operator = LabelOperator.EQUAL,
                        value = "test_value",
                        expires_after_seconds = 10.0,
                        expedite = False
                    )
                ]
            )
        ]
    ),
]


# The test class name needs to start with "Test" to get collected by pytest
class TestClassificationPolicyAsync(AsyncRouterRecordedTestCase):
    async def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_client: JobRouterAdministrationClient = self.create_admin_client()
            async with router_client:
                if self._testMethodName in self.classification_policy_ids \
                        and any(self.classification_policy_ids[self._testMethodName]):
                    for policy_id in set(self.classification_policy_ids[self._testMethodName]):
                        await router_client.delete_classification_policy(classification_policy_id = policy_id)

                if self._testMethodName in self.queue_ids \
                        and any(self.queue_ids[self._testMethodName]):
                    for policy_id in set(self.queue_ids[self._testMethodName]):
                        await router_client.delete_queue(queue_id = policy_id)

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
                self.distribution_policy_ids[self._testMethodName] \
                    = self.distribution_policy_ids[self._testMethodName].append(distribution_policy_id)
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
                labels = queue_labels,
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
    async def test_create_classification_policy(self):
        router_client: JobRouterAdministrationClient = self.create_admin_client()
        cp_identifier = 'tst_create_cp_async'

        async with router_client:
            for rule in prioritization_rules:
                classification_policy: ClassificationPolicy = ClassificationPolicy(
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = rule,
                    worker_selectors = worker_selectors
                )

                classification_policy = await router_client.create_classification_policy(
                    classification_policy_id = cp_identifier,
                    classification_policy = classification_policy
                )

                # add for cleanup
                self.classification_policy_ids[self._testMethodName] = [cp_identifier]

                assert classification_policy is not None

                ClassificationPolicyValidator.validate_classification_policy(
                    classification_policy,
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = rule,
                    worker_selectors = worker_selectors
                )

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_classification_policy(self):
        router_client: JobRouterAdministrationClient = self.create_admin_client()
        cp_identifier = 'tst_update_cp_async'

        async with router_client:
            for rule in prioritization_rules:
                classification_policy: ClassificationPolicy = ClassificationPolicy(
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = rule,
                    worker_selectors = worker_selectors
                )

                classification_policy = await router_client.create_classification_policy(
                    classification_policy_id = cp_identifier,
                    classification_policy = classification_policy
                )

                # add for cleanup
                self.classification_policy_ids[self._testMethodName] = [cp_identifier]

                assert classification_policy is not None

                ClassificationPolicyValidator.validate_classification_policy(
                    classification_policy,
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = rule,
                    worker_selectors = worker_selectors
                )

                updated_prioritization_rule = ExpressionRouterRule(expression = "2")
                classification_policy.prioritization_rule = updated_prioritization_rule

                updated_classification_policy = await router_client.update_classification_policy(
                    cp_identifier,
                    classification_policy
                )

                ClassificationPolicyValidator.validate_classification_policy(
                    updated_classification_policy,
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = updated_prioritization_rule,
                    worker_selectors = worker_selectors
                )

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_classification_policy_w_kwargs(self):
        router_client: JobRouterAdministrationClient = self.create_admin_client()
        cp_identifier = 'tst_update_cp_w_args_async'

        async with router_client:
            for rule in prioritization_rules:
                classification_policy: ClassificationPolicy = ClassificationPolicy(
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = rule,
                    worker_selectors = worker_selectors
                )

                classification_policy = await router_client.create_classification_policy(
                    classification_policy_id = cp_identifier,
                    classification_policy = classification_policy
                )

                # add for cleanup
                self.classification_policy_ids[self._testMethodName] = [cp_identifier]

                assert classification_policy is not None

                ClassificationPolicyValidator.validate_classification_policy(
                    classification_policy,
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = rule,
                    worker_selectors = worker_selectors
                )

                updated_prioritization_rule = ExpressionRouterRule(expression = "2")
                classification_policy.prioritization_rule = updated_prioritization_rule

                updated_classification_policy = await router_client.update_classification_policy(
                    cp_identifier,
                    prioritization_rule = updated_prioritization_rule
                )

                ClassificationPolicyValidator.validate_classification_policy(
                    updated_classification_policy,
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = updated_prioritization_rule,
                    worker_selectors = worker_selectors
                )

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_get_classification_policy(self):
        router_client: JobRouterAdministrationClient = self.create_admin_client()
        cp_identifier = 'tst_get_cp_async'

        async with router_client:
            for rule in prioritization_rules:
                classification_policy: ClassificationPolicy = ClassificationPolicy(
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = rule,
                    worker_selectors = worker_selectors
                )

                classification_policy = await router_client.create_classification_policy(
                    classification_policy_id = cp_identifier,
                    classification_policy = classification_policy
                )

                # add for cleanup
                self.classification_policy_ids[self._testMethodName] = [cp_identifier]

                assert classification_policy is not None

                ClassificationPolicyValidator.validate_classification_policy(
                    classification_policy,
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = rule,
                    worker_selectors = worker_selectors
                )

                queried_classification_policy = await router_client.get_classification_policy(
                    classification_policy_id = cp_identifier
                )

                ClassificationPolicyValidator.validate_classification_policy(
                    queried_classification_policy,
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = rule,
                    worker_selectors = worker_selectors
                )

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_list_classification_policies(self):
        router_client: JobRouterAdministrationClient = self.create_admin_client()
        cp_identifiers = ['tst_list_cp_1_async', 'tst_list_cp_2_async']
        created_cp_response = {}
        policy_count = 0
        self.classification_policy_ids[self._testMethodName] = []

        async with router_client:
            for rule in prioritization_rules:
                for _identifier in cp_identifiers:
                    classification_policy: ClassificationPolicy = ClassificationPolicy(
                        name = _identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = queue_selectors,
                        prioritization_rule = rule,
                        worker_selectors = worker_selectors
                    )

                    classification_policy = await router_client.create_classification_policy(
                        classification_policy_id = _identifier,
                        classification_policy = classification_policy
                    )

                    policy_count += 1

                    # add for cleanup
                    self.classification_policy_ids[self._testMethodName].append(_identifier)

                    assert classification_policy is not None

                    ClassificationPolicyValidator.validate_classification_policy(
                        classification_policy,
                        name = _identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = queue_selectors,
                        prioritization_rule = rule,
                        worker_selectors = worker_selectors
                    )

                    created_cp_response[classification_policy.id] = classification_policy

                policies = router_client.list_classification_policies(results_per_page = 1)
                async for policy_page in policies.by_page():

                    if policy_count == 0:
                        # all created policies have been listed
                        break

                    list_of_policies = [i async for i in policy_page]
                    assert len(list_of_policies) <= 1

                    for policy_item in list_of_policies:
                        response_at_creation = created_cp_response.get(policy_item.classification_policy.id, None)

                        if not response_at_creation:
                            continue

                        ClassificationPolicyValidator.validate_classification_policy(
                            policy_item.classification_policy,
                            name = response_at_creation.name,
                            fallback_queue_id = response_at_creation.fallback_queue_id,
                            queue_selectors = response_at_creation.queue_selectors,
                            prioritization_rule = response_at_creation.prioritization_rule,
                            worker_selectors = response_at_creation.worker_selectors
                        )
                        policy_count -= 1

    @RouterPreparersAsync.router_test_decorator_async
    @recorded_by_proxy_async
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_delete_classification_policy(self):
        router_client: JobRouterAdministrationClient = self.create_admin_client()
        cp_identifier = 'tst_delete_cp'

        async with router_client:
            for rule in prioritization_rules:
                classification_policy: ClassificationPolicy = ClassificationPolicy(
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = rule,
                    worker_selectors = worker_selectors
                )

                classification_policy = await router_client.create_classification_policy(
                    classification_policy_id = cp_identifier,
                    classification_policy = classification_policy,
                )

                # add for cleanup
                self.classification_policy_ids[self._testMethodName] = [cp_identifier]

                assert classification_policy is not None

                ClassificationPolicyValidator.validate_classification_policy(
                    classification_policy,
                    name = cp_identifier,
                    fallback_queue_id = self.get_job_queue_id(),
                    queue_selectors = queue_selectors,
                    prioritization_rule = rule,
                    worker_selectors = worker_selectors
                )

                await router_client.delete_classification_policy(
                    classification_policy_id = cp_identifier
                )

                with pytest.raises(ResourceNotFoundError) as nfe:
                    await router_client.get_classification_policy(classification_policy_id = cp_identifier)

                assert nfe.value.reason == "Not Found"
                assert nfe.value.status_code == 404
