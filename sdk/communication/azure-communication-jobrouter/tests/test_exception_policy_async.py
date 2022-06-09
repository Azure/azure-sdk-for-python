# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from _router_test_case_async import AsyncRouterTestCase
from _decorators_async import RouterPreparersAsync
from _validators import ExceptionPolicyValidator
from _shared.asynctestcase import AsyncCommunicationTestCase
from azure.communication.jobrouter._shared.utils import parse_connection_str  # pylint:disable=protected-access
from azure.core.exceptions import ResourceNotFoundError

from azure.communication.jobrouter.aio import RouterClient
from azure.communication.jobrouter import (
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
class TestExceptionPolicyAsync(AsyncRouterTestCase):
    def __init__(self, method_name):
        super(TestExceptionPolicyAsync, self).__init__(method_name)
        self.exception_policy_ids = {}  # type: Dict[str, List[str]]
        self.queue_ids = {}  # type: Dict[str, List[str]]
        self.distribution_policy_ids = {}  # type: Dict[str, List[str]]
        self.classification_policy_ids = {}  # type: Dict[str, List[str]]

    async def clean_up(self):
        # delete in live mode
        if not self.is_playback():
            router_client: RouterClient = self.create_client()
            async with router_client:
                if self._testMethodName in self.classification_policy_ids \
                        and any(self.classification_policy_ids[self._testMethodName]):
                    for policy_id in set(self.classification_policy_ids[self._testMethodName]):
                        await router_client.delete_classification_policy(identifier = policy_id)

                if self._testMethodName in self.queue_ids \
                        and any(self.queue_ids[self._testMethodName]):
                    for policy_id in set(self.queue_ids[self._testMethodName]):
                        await router_client.delete_queue(identifier = policy_id)

                if self._testMethodName in self.distribution_policy_ids \
                        and any(self.distribution_policy_ids[self._testMethodName]):
                    for policy_id in set(self.distribution_policy_ids[self._testMethodName]):
                        await router_client.delete_distribution_policy(identifier = policy_id)

                if self._testMethodName in self.exception_policy_ids \
                        and any(self.exception_policy_ids[self._testMethodName]):
                    for policy_id in set(self.exception_policy_ids[self._testMethodName]):
                        await router_client.delete_exception_policy(identifier = policy_id)

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
            self.distribution_policy_ids[self._testMethodName] \
                = self.distribution_policy_ids[self._testMethodName].append(distribution_policy_id)
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
        return self._testMethodName + "_tst_cp_async"

    async def setup_classification_policy(self):
        client: RouterClient = self.create_client()

        async with client:
            cp_id = self.get_classification_policy_id()
            classification_policy = await client.create_classification_policy(
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
        super(TestExceptionPolicyAsync, self).setUp()

        endpoint, _ = parse_connection_str(self.connection_str)
        self.endpoint = endpoint

    def tearDown(self):
        super(TestExceptionPolicyAsync, self).tearDown()

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_classification_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_create_exception_policy(self):
        ep_identifier = "tst_create_ep_async"
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

        async with router_client:
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

                    exception_policy = await router_client.create_exception_policy(
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

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_classification_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_update_exception_policy(self):
        ep_identifier = "tst_update_ep_async"
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

        async with router_client:
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

                    exception_policy = await router_client.create_exception_policy(
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
                        "fakeExceptionRuleId": None,
                        "fakeExceptionRuleId2": ExceptionRule(
                            trigger = trigger,
                            actions = {
                                "fakeExceptionActionId": action
                            }
                        )
                    }

                    exception_policy = await router_client.update_exception_policy(
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

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_classification_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_get_exception_policy(self):
        ep_identifier = "tst_get_ep_async"
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

        async with router_client:
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

                    exception_policy = await router_client.create_exception_policy(
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

                    queried_exception_policy = await router_client.get_exception_policy(
                        identifier = ep_identifier
                    )

                    assert queried_exception_policy is not None
                    ExceptionPolicyValidator.validate_exception_policy(
                        queried_exception_policy,
                        identifier = ep_identifier,
                        name = ep_identifier,
                        exception_rules = exception_rules
                    )

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_classification_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_delete_exception_policy(self):
        ep_identifier = "tst_delete_ep_async"
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

        async with router_client:
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

                    exception_policy = await router_client.create_exception_policy(
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

                    await router_client.delete_exception_policy(identifier = ep_identifier)
                    with pytest.raises(ResourceNotFoundError) as nfe:
                        await router_client.get_exception_policy(identifier = ep_identifier)
                    assert nfe.value.reason == "Not Found"
                    assert nfe.value.status_code == 404

    @AsyncCommunicationTestCase.await_prepared_test
    @RouterPreparersAsync.before_test_execute_async('setup_distribution_policy')
    @RouterPreparersAsync.before_test_execute_async('setup_job_queue')
    @RouterPreparersAsync.before_test_execute_async('setup_classification_policy')
    @RouterPreparersAsync.after_test_execute_async('clean_up')
    async def test_list_exception_policies(self):
        ep_identifiers = ["tst_list_ep_1_async", "tst_list_ep_2_async", "tst_list_ep_3_async"]
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

        async with router_client:
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

                        exception_policy = await router_client.create_exception_policy(
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
                    async for policy_page in policies.by_page():
                        list_of_policies = [i async for i in  policy_page]
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
