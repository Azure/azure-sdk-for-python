# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from _router_test_case import RouterTestCase
from _decorators import RouterPreparers
from _validators import ExceptionPolicyValidator
from azure.communication.jobrouter._shared.utils import parse_connection_str  # pylint:disable=protected-access
from azure.core.exceptions import ResourceNotFoundError

from azure.communication.jobrouter import (
    RouterClient,
    ExceptionPolicy,
    ExceptionRule,
    QueueLengthExceptionTrigger,
    WaitTimeExceptionTrigger,
    ReclassifyExceptionAction,
    ManualReclassifyExceptionAction,
    CancelExceptionAction,
    LabelCollection,
    RoundRobinMode
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


exception_triggers = [
    QueueLengthExceptionTrigger(threshold = 1),
    WaitTimeExceptionTrigger(threshold = "PT1H")
]

exception_actions = [
    # ManualReclassifyExceptionAction() - is to be added to list inside every test
    # since queue will need to be created as a prerequisite
    CancelExceptionAction(),
    # ReclassifyExceptionAction() - is to be added to list inside every test
    # since classification policy will need to be created as a prerequisite
]


# The test class name needs to start with "Test" to get collected by pytest
class TestExceptionPolicy(RouterTestCase):
    def __init__(self, method_name):
        super(TestExceptionPolicy, self).__init__(method_name)
        self.exception_policy_ids = {}  # type: Dict[str, List[str]]
        self.queue_ids = {}  # type: Dict[str, List[str]]
        self.distribution_policy_ids = {}  # type: Dict[str, List[str]]
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

            if self._testMethodName in self.exception_policy_ids \
                    and any(self.exception_policy_ids[self._testMethodName]):
                for policy_id in set(self.exception_policy_ids[self._testMethodName]):
                    router_client.delete_exception_policy(identifier = policy_id)

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

    def get_classification_policy_id(self):
        return self._testMethodName + "_tst_cp"

    def setup_classification_policy(self):
        client: RouterClient = self.create_client()
        cp_id = self.get_classification_policy_id()
        classification_policy = client.create_classification_policy(
            identifier = cp_id,
            name = cp_id,
            fallback_queue_id = self.get_job_queue_id(),
        )

        # add for cleanup later
        if self._testMethodName in self.classification_policy_ids:
            self.classification_policy_ids[self._testMethodName] \
                = self.classification_policy_ids[self._testMethodName].append(cp_id)
        else:
            self.classification_policy_ids[self._testMethodName] = [cp_id]

    def setUp(self):
        super(TestExceptionPolicy, self).setUp()

        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint

    def tearDown(self):
        super(TestExceptionPolicy, self).tearDown()

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    @RouterPreparers.before_test_execute('setup_classification_policy')
    def test_create_exception_policy(self):
        ep_identifier = "tst_create_ep"
        router_client: RouterClient = self.create_client()

        updated_exception_actions = []
        updated_exception_actions.extend(exception_actions)
        updated_exception_actions.append(
            ManualReclassifyExceptionAction(
                queue_id = self.get_job_queue_id(),
                priority = 1,
            )
        )
        updated_exception_actions.append((
            ReclassifyExceptionAction(
                classification_policy_id = self.get_classification_policy_id()
            )
        ))

        for trigger in exception_triggers:
            for action in updated_exception_actions:

                exception_rules = {
                    "fakeExceptionRuleId": ExceptionRule(
                        trigger = trigger,
                        actions = {
                            "fakeExceptionActionId": action
                        }
                    )
                }

                exception_policy = router_client.create_exception_policy(
                    identifier = ep_identifier,
                    name = ep_identifier,
                    exception_rules = exception_rules
                )

                # add for cleanup
                self.exception_policy_ids[self._testMethodName] = [ep_identifier]

                assert exception_policy is not None
                ExceptionPolicyValidator.validate_exception_policy(
                    exception_policy,
                    identifier = ep_identifier,
                    name = ep_identifier,
                    exception_rules = exception_rules
                )

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    @RouterPreparers.before_test_execute('setup_classification_policy')
    def test_update_exception_policy(self):
        ep_identifier = "tst_update_ep"
        router_client: RouterClient = self.create_client()

        updated_exception_actions = []
        updated_exception_actions.extend(exception_actions)
        updated_exception_actions.append(
            ManualReclassifyExceptionAction(
                queue_id = self.get_job_queue_id(),
                priority = 1,
            )
        )
        updated_exception_actions.append((
            ReclassifyExceptionAction(
                classification_policy_id = self.get_classification_policy_id()
            )
        ))

        for trigger in exception_triggers:
            for action in updated_exception_actions:
                exception_rules = {
                    "fakeExceptionRuleId": ExceptionRule(
                        trigger = trigger,
                        actions = {
                            "fakeExceptionActionId": action
                        }
                    )
                }

                exception_policy = router_client.create_exception_policy(
                    identifier = ep_identifier,
                    name = ep_identifier,
                    exception_rules = exception_rules
                )

                # add for cleanup
                self.exception_policy_ids[self._testMethodName] = [ep_identifier]

                assert exception_policy is not None
                ExceptionPolicyValidator.validate_exception_policy(
                    exception_policy,
                    identifier = ep_identifier,
                    name = ep_identifier,
                    exception_rules = exception_rules
                )

                updated_exception_rules = {
                    "fakeExceptionRuleId": None,  # existing rule is set to delete
                    "fakeExceptionRuleId2": ExceptionRule(
                        trigger = trigger,
                        actions = {
                            "fakeExceptionActionId": action
                        }
                    )
                }

                exception_policy = router_client.update_exception_policy(
                    identifier = ep_identifier,
                    name = ep_identifier,
                    exception_rules = updated_exception_rules
                )

                assert exception_policy is not None
                ExceptionPolicyValidator.validate_exception_policy(
                    exception_policy,
                    identifier = ep_identifier,
                    name = ep_identifier,
                    exception_rules = updated_exception_rules
                )

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    @RouterPreparers.before_test_execute('setup_classification_policy')
    def test_get_exception_policy(self):
        ep_identifier = "tst_get_ep"
        router_client: RouterClient = self.create_client()

        updated_exception_actions = []
        updated_exception_actions.extend(exception_actions)
        updated_exception_actions.append(
            ManualReclassifyExceptionAction(
                queue_id = self.get_job_queue_id(),
                priority = 1,
            )
        )
        updated_exception_actions.append((
            ReclassifyExceptionAction(
                classification_policy_id = self.get_classification_policy_id()
            )
        ))

        for trigger in exception_triggers:
            for action in updated_exception_actions:
                exception_rules = {
                    "fakeExceptionRuleId": ExceptionRule(
                        trigger = trigger,
                        actions = {
                            "fakeExceptionActionId": action
                        }
                    )
                }

                exception_policy = router_client.create_exception_policy(
                    identifier = ep_identifier,
                    name = ep_identifier,
                    exception_rules = exception_rules
                )

                # add for cleanup
                self.exception_policy_ids[self._testMethodName] = [ep_identifier]

                assert exception_policy is not None
                ExceptionPolicyValidator.validate_exception_policy(
                    exception_policy,
                    identifier = ep_identifier,
                    name = ep_identifier,
                    exception_rules = exception_rules
                )

                queried_exception_policy = router_client.get_exception_policy(
                    identifier = ep_identifier
                )

                assert queried_exception_policy is not None
                ExceptionPolicyValidator.validate_exception_policy(
                    queried_exception_policy,
                    identifier = ep_identifier,
                    name = ep_identifier,
                    exception_rules = exception_rules
                )

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    @RouterPreparers.before_test_execute('setup_classification_policy')
    def test_delete_exception_policy(self):
        ep_identifier = "tst_delete_ep"
        router_client: RouterClient = self.create_client()

        updated_exception_actions = []
        updated_exception_actions.extend(exception_actions)
        updated_exception_actions.append(
            ManualReclassifyExceptionAction(
                queue_id = self.get_job_queue_id(),
                priority = 1,
            )
        )
        updated_exception_actions.append((
            ReclassifyExceptionAction(
                classification_policy_id = self.get_classification_policy_id()
            )
        ))

        for trigger in exception_triggers:
            for action in updated_exception_actions:
                exception_rules = {
                    "fakeExceptionRuleId": ExceptionRule(
                        trigger = trigger,
                        actions = {
                            "fakeExceptionActionId": action
                        }
                    )
                }

                exception_policy = router_client.create_exception_policy(
                    identifier = ep_identifier,
                    name = ep_identifier,
                    exception_rules = exception_rules
                )

                # add for cleanup
                self.exception_policy_ids[self._testMethodName] = [ep_identifier]

                assert exception_policy is not None
                ExceptionPolicyValidator.validate_exception_policy(
                    exception_policy,
                    identifier = ep_identifier,
                    name = ep_identifier,
                    exception_rules = exception_rules
                )

                router_client.delete_exception_policy(identifier = ep_identifier)
                with pytest.raises(ResourceNotFoundError) as nfe:
                    router_client.get_exception_policy(identifier = ep_identifier)
                assert nfe.value.reason == "Not Found"
                assert nfe.value.status_code == 404

    @RouterPreparers.before_test_execute('setup_distribution_policy')
    @RouterPreparers.before_test_execute('setup_job_queue')
    @RouterPreparers.before_test_execute('setup_classification_policy')
    def test_list_exception_policies(self):
        ep_identifiers = ["tst_list_ep_1", "tst_list_ep_2", "tst_list_ep_3"]
        created_ep_response = {}
        policy_count = 0
        router_client: RouterClient = self.create_client()
        self.exception_policy_ids[self._testMethodName] = []

        updated_exception_actions = []
        updated_exception_actions.extend(exception_actions)
        updated_exception_actions.append(
            ManualReclassifyExceptionAction(
                queue_id = self.get_job_queue_id(),
                priority = 1,
            )
        )
        updated_exception_actions.append((
            ReclassifyExceptionAction(
                classification_policy_id = self.get_classification_policy_id()
            )
        ))

        for trigger in exception_triggers:
            for action in updated_exception_actions:
                for identifier in ep_identifiers:
                    exception_rules = {
                        "fakeExceptionRuleId": ExceptionRule(
                            trigger = trigger,
                            actions = {
                                "fakeExceptionActionId": action
                            }
                        )
                    }

                    exception_policy = router_client.create_exception_policy(
                        identifier = identifier,
                        name = identifier,
                        exception_rules = exception_rules
                    )

                    policy_count += 1

                    # add for cleanup
                    self.exception_policy_ids[self._testMethodName].append(identifier)

                    assert exception_policy is not None
                    ExceptionPolicyValidator.validate_exception_policy(
                        exception_policy,
                        identifier = identifier,
                        name = identifier,
                        exception_rules = exception_rules
                    )

                    created_ep_response[exception_policy.id] = exception_policy

                policies = router_client.list_exception_policies(results_per_page = 2)
                for policy_page in policies.by_page():
                    list_of_policies = list(policy_page)
                    assert len(list_of_policies) <= 2

                    for policy in list_of_policies:
                        response_at_creation = created_ep_response.get(policy.id, None)

                        if not response_at_creation:
                            continue

                        ExceptionPolicyValidator.validate_exception_policy(
                            policy,
                            identifier = response_at_creation.id,
                            name = response_at_creation.name,
                            exception_rules = response_at_creation.exception_rules,
                        )
                        policy_count -= 1

                # all policies created were listed
                assert policy_count == 0
