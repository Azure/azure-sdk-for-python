# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import ResourceNotFoundError
from _router_test_case import RouterTestCase
from _decorators import RouterPreparers
from _validators import ClassificationPolicyValidator
from azure.communication.jobrouter._shared.utils import parse_connection_str

from azure.communication.jobrouter import (
    RouterClient,
    RoundRobinMode,
    ClassificationPolicy,
    LabelOperator,
    QueueSelector,
    StaticQueueSelector,
    ConditionalQueueSelector,
    RuleEngineQueueSelector,
    PassThroughQueueSelector,
    QueueWeightedAllocation,
    WeightedAllocationQueueSelector,
    WorkerSelector,
    StaticWorkerSelector,
    ConditionalWorkerSelector,
    RuleEngineWorkerSelector,
    PassThroughWorkerSelector,
    WorkerWeightedAllocation,
    WeightedAllocationWorkerSelector,
    StaticRule,
    ExpressionRule,
    AzureFunctionRule,
    AzureFunctionRuleCredential,
    LabelCollection
)


queue_labels = LabelCollection(
    {
        'key1': "QueueKey",
        'key2': 10,
        'key3': True,
        'key4': False,
        'key5': 10.1
    }
)

queue_selectors = [
    StaticQueueSelector(
        label_selector = QueueSelector(
            key = "test_key", label_operator = LabelOperator.EQUAL, value = "test_value"
        )
    ),
    ConditionalQueueSelector(
        condition = StaticRule(value = True),
        label_selectors = [
            QueueSelector(
                key = "test_key", label_operator = LabelOperator.EQUAL, value = "test_value"
            )
        ]
    ),
    ## TODO: Bugfix required
    # RuleEngineQueueSelector(
    #     rule = StaticRule(value = QueueSelector(
    #             key = "test_key", label_operator = LabelOperator.EQUAL, value = "test_value"
    #         ))
    # ),
    PassThroughQueueSelector(
        key = "testKey",
        label_operator = LabelOperator.EQUAL
    ),
    WeightedAllocationQueueSelector(
        allocations = [
            QueueWeightedAllocation(
                weight = 1.0,
                label_selectors = [
                    QueueSelector(
                        key = "test_key", label_operator = LabelOperator.EQUAL, value = "test_value"
                    )
                ]
            )
        ]
    )
]

prioritization_rules = [
    StaticRule(value = 1),
    ExpressionRule(expression = "1"),
    AzureFunctionRule(function_url = "https://fake.azurewebsites.net/fakeRule"),
    AzureFunctionRule(
        function_url = "https://fake.azurewebsites.net/fakeRule",
        credential = AzureFunctionRuleCredential(function_key = "fakeKey"))
]

worker_selectors = [
    StaticWorkerSelector(
        label_selector = WorkerSelector(
            key = "test_key",
            label_operator = LabelOperator.EQUAL,
            value = "test_value",
            ttl_seconds = 10.0,
            expedite = False
        )
    ),
    ConditionalWorkerSelector(
        condition = StaticRule(value = True),
        label_selectors = [
            WorkerSelector(
                key = "test_key",
                label_operator = LabelOperator.EQUAL,
                value = "test_value",
                ttl_seconds = 10.0,
                expedite = False
            )
        ]
    ),
    ## TODO: Bugfix required
    # RuleEngineWorkerSelector(
    #     rule = StaticRule(value = [
    #         WorkerSelector(
    #             key = "test_key",
    #             label_operator = LabelOperator.EQUAL,
    #             value = "test_value",
    #             ttl_seconds = 10.0,
    #             expedite = False
    #         )]
    #     )
    # ),
    PassThroughWorkerSelector(
        key = "testKey",
        label_operator = LabelOperator.EQUAL
    ),
    WeightedAllocationWorkerSelector(
        allocations = [
            WorkerWeightedAllocation(
                weight = 1.0,
                label_selectors = [
                    WorkerSelector(
                        key = "test_key",
                        label_operator = LabelOperator.EQUAL,
                        value = "test_value",
                        ttl_seconds = 10.0,
                        expedite = False
                    )
                ]
            )
        ]
    ),
]


# The test class name needs to start with "Test" to get collected by pytest
class TestClassificationPolicy(RouterTestCase):
    def __init__(self, method_name):
        super(TestClassificationPolicy, self).__init__(method_name)
        self.distribution_policy_ids = {}  # type: Dict[str, List[str]]
        self.queue_ids = {}  # type: Dict[str, List[str]]
        self.classification_policy_ids = {}  # type: Dict[str, List[str]]

    def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_client: RouterClient = self.create_client()
            if self._testMethodName in self.classification_policy_ids \
                    and any(self.classification_policy_ids[self._testMethodName]):
                for policy_id in set(self.classification_policy_ids[self._testMethodName]):
                    router_client.delete_classification_policy(identifier = policy_id)

            if self._testMethodName in self.queue_ids \
                    and any(self.queue_ids[self._testMethodName]):
                for policy_id in set(self.queue_ids[self._testMethodName]):
                    router_client.delete_queue(identifier = policy_id)

            if self._testMethodName in self.distribution_policy_ids \
                    and any(self.distribution_policy_ids[self._testMethodName]):
                for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                    router_client.delete_distribution_policy(identifier = policy_id)

    def setUp(self):
        super(TestClassificationPolicy, self).setUp()

        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint

    def tearDown(self):
        super(TestClassificationPolicy, self).tearDown()

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
            self.distribution_policy_ids[self._testMethodName] \
                = self.distribution_policy_ids[self._testMethodName].append(distribution_policy_id)
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
            labels = queue_labels,
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
    def test_create_classification_policy(self):
        router_client: RouterClient = self.create_client()
        cp_identifier = 'tst_create_cp'

        for qs in queue_selectors:
            for rule in prioritization_rules:
                for ws in worker_selectors:
                    classification_policy = router_client.create_classification_policy(
                        identifier = cp_identifier,
                        name = cp_identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = [qs],
                        prioritization_rule = rule,
                        worker_selectors = [ws]
                    )

                    # add for cleanup
                    self.classification_policy_ids[self._testMethodName] = [cp_identifier]

                    assert classification_policy is not None

                    ClassificationPolicyValidator.validate_classification_policy(
                        classification_policy,
                        name = cp_identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = [qs],
                        prioritization_rule = rule,
                        worker_selectors = [ws]
                    )
        self.clean_up()

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_update_classification_policy(self):
        router_client: RouterClient = self.create_client()
        cp_identifier = 'tst_update_cp'

        for qs in queue_selectors:
            for rule in prioritization_rules:
                for ws in worker_selectors:
                    classification_policy = router_client.create_classification_policy(
                        identifier = cp_identifier,
                        name = cp_identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = [qs],
                        prioritization_rule = rule,
                        worker_selectors = [ws]
                    )

                    # add for cleanup
                    self.classification_policy_ids[self._testMethodName] = [cp_identifier]

                    assert classification_policy is not None

                    ClassificationPolicyValidator.validate_classification_policy(
                        classification_policy,
                        name = cp_identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = [qs],
                        prioritization_rule = rule,
                        worker_selectors = [ws]
                    )

                    updated_prioritization_rule = ExpressionRule(expression = "2")
                    classification_policy.prioritization_rule = updated_prioritization_rule

                    updated_classification_policy = router_client.update_classification_policy(
                        identifier = cp_identifier,
                        classification_policy = classification_policy
                    )

                    ClassificationPolicyValidator.validate_classification_policy(
                        updated_classification_policy,
                        name = cp_identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = [qs],
                        prioritization_rule = updated_prioritization_rule,
                        worker_selectors = [ws]
                    )

        self.clean_up()

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_get_classification_policy(self):
        router_client: RouterClient = self.create_client()
        cp_identifier = 'tst_get_cp'

        for qs in queue_selectors:
            for rule in prioritization_rules:
                for ws in worker_selectors:
                    classification_policy = router_client.create_classification_policy(
                        identifier = cp_identifier,
                        name = cp_identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = [qs],
                        prioritization_rule = rule,
                        worker_selectors = [ws]
                    )

                    # add for cleanup
                    self.classification_policy_ids[self._testMethodName] = [cp_identifier]

                    assert classification_policy is not None

                    ClassificationPolicyValidator.validate_classification_policy(
                        classification_policy,
                        name = cp_identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = [qs],
                        prioritization_rule = rule,
                        worker_selectors = [ws]
                    )

                    queried_classification_policy = router_client.get_classification_policy(
                        identifier = cp_identifier
                    )

                    ClassificationPolicyValidator.validate_classification_policy(
                        queried_classification_policy,
                        name = cp_identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = [qs],
                        prioritization_rule = rule,
                        worker_selectors = [ws]
                    )

        self.clean_up()

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_list_classification_policies(self):
        router_client: RouterClient = self.create_client()
        cp_identifiers = ['tst_list_cp_1', 'tst_list_cp_2', 'tst_list_cp_3']
        created_cp_response = {}
        policy_count = 0
        self.classification_policy_ids[self._testMethodName] = []

        for qs in queue_selectors:
            for rule in prioritization_rules:
                for ws in worker_selectors:
                    for _identifier in cp_identifiers:
                        classification_policy = router_client.create_classification_policy(
                            identifier = _identifier,
                            name = _identifier,
                            fallback_queue_id = self.get_job_queue_id(),
                            queue_selectors = [qs],
                            prioritization_rule = rule,
                            worker_selectors = [ws]
                        )

                        policy_count += 1

                        # add for cleanup
                        self.classification_policy_ids[self._testMethodName].append(_identifier)

                        assert classification_policy is not None

                        ClassificationPolicyValidator.validate_classification_policy(
                            classification_policy,
                            name = _identifier,
                            fallback_queue_id = self.get_job_queue_id(),
                            queue_selectors = [qs],
                            prioritization_rule = rule,
                            worker_selectors = [ws]
                        )

                        created_cp_response[classification_policy.id] = classification_policy

                    policies = router_client.list_classification_policies(results_per_page = 2)
                    for policy_page in policies.by_page():
                        list_of_policies = list(policy_page)
                        assert len(list_of_policies) <= 2

                        for policy in list_of_policies:
                            response_at_creation = created_cp_response.get(policy.id, None)

                            if not response_at_creation:
                                continue

                            ClassificationPolicyValidator.validate_classification_policy(
                                policy,
                                name = response_at_creation.name,
                                fallback_queue_id = response_at_creation.fallback_queue_id,
                                queue_selectors = response_at_creation.queue_selectors,
                                prioritization_rule = response_at_creation.prioritization_rule,
                                worker_selectors = response_at_creation.worker_selectors
                            )
                            policy_count -= 1

                    # all policies created were listed
                    assert policy_count == 0

        self.clean_up()

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    def test_delete_classification_policy(self):
        router_client: RouterClient = self.create_client()
        cp_identifier = 'tst_delete_cp'

        for qs in queue_selectors:
            for rule in prioritization_rules:
                for ws in worker_selectors:
                    classification_policy = router_client.create_classification_policy(
                        identifier = cp_identifier,
                        name = cp_identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = [qs],
                        prioritization_rule = rule,
                        worker_selectors = [ws]
                    )

                    # add for cleanup
                    self.classification_policy_ids[self._testMethodName] = [cp_identifier]

                    assert classification_policy is not None

                    ClassificationPolicyValidator.validate_classification_policy(
                        classification_policy,
                        name = cp_identifier,
                        fallback_queue_id = self.get_job_queue_id(),
                        queue_selectors = [qs],
                        prioritization_rule = rule,
                        worker_selectors = [ws]
                    )

                    router_client.delete_classification_policy(
                        identifier = cp_identifier
                    )

                    with pytest.raises(ResourceNotFoundError) as nfe:
                        router_client.get_classification_policy(identifier = cp_identifier)

                    assert nfe.value.reason == "Not Found"
                    assert nfe.value.status_code == 404

        self.clean_up()
