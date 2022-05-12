# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING
import itertools
from collections import Counter
if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union, Tuple

from azure.communication.jobrouter import (
    BestWorkerMode,
    LongestIdleMode,
    RoundRobinMode,
    LabelCollection,
    ExceptionRule,
    ExceptionPolicy,
    QueueLengthExceptionTrigger,
    WaitTimeExceptionTrigger,
    ReclassifyExceptionAction,
    ManualReclassifyExceptionAction,
    CancelExceptionAction,
    QueueAssignment,
    ChannelConfiguration,
    RouterWorker,
    RouterWorkerState
)


class DistributionPolicyValidator(object):
    @staticmethod
    def validate_id(
            distribution_policy,
            id,
            **kwargs
    ):
        assert distribution_policy.id == id

    @staticmethod
    def validate_name(
            distribution_policy,
            name,
            **kwargs
    ):
        assert distribution_policy.name == name

    @staticmethod
    def validate_offer_ttl(
            distribution_policy,
            offer_ttl_seconds,
            **kwargs
    ):
        assert distribution_policy.offer_ttl_seconds == offer_ttl_seconds

    @staticmethod
    def validate_longest_idle_mode(distribution_policy, mode, **kwargs):
        assert distribution_policy.mode.kind == "longest-idle"

    @staticmethod
    def validate_round_robin_mode(distribution_policy, mode, **kwargs):
        assert distribution_policy.mode.kind == "round-robin"

    @staticmethod
    def validate_best_worker_mode(distribution_policy, mode, **kwargs):
        assert distribution_policy.mode.kind == "best-worker"
        # TODO: Add more validations for best worker mode

    @staticmethod
    def validate_distribution_mode(
            distribution_policy,
            mode,
            **kwargs
    ):
        assert isinstance(distribution_policy.mode, type(mode)) is True
        assert distribution_policy.mode.min_concurrent_offers == mode.min_concurrent_offers
        assert distribution_policy.mode.max_concurrent_offers == mode.max_concurrent_offers

        if isinstance(mode, LongestIdleMode):
            DistributionPolicyValidator.validate_longest_idle_mode(distribution_policy, mode)
        elif isinstance(mode, RoundRobinMode):
            DistributionPolicyValidator.validate_round_robin_mode(distribution_policy, mode)
        elif isinstance(mode, BestWorkerMode):
            DistributionPolicyValidator.validate_best_worker_mode(distribution_policy, mode)
        else:
            raise AssertionError("Unable to determine mode type")

    @staticmethod
    def validate_distribution_policy(distribution_policy, **kwargs):

        if not kwargs.get("identifier", None):
            DistributionPolicyValidator.validate_id(distribution_policy, kwargs.pop("identifier"))

        if not kwargs.get("name", None):
            DistributionPolicyValidator.validate_name(distribution_policy, kwargs.pop("name"))

        if not kwargs.get("offer_ttl_seconds", None):
            DistributionPolicyValidator.validate_offer_ttl(distribution_policy, kwargs.pop("offer_ttl_seconds"))

        if not kwargs.get("mode", None):
            DistributionPolicyValidator.validate_distribution_mode(distribution_policy, kwargs.pop("mode"))


class JobQueueValidator(object):
    @staticmethod
    def validate_id(
            entity,
            identifier,
            **kwargs
    ):
        assert entity.id == identifier

    @staticmethod
    def validate_name(
            entity,
            name,
            **kwargs
    ):
        assert entity.name == name

    @staticmethod
    def validate_distribution_policy_id(
            entity,
            distribution_policy_id,
            **kwargs
    ):
        assert entity.distribution_policy_id == distribution_policy_id

    @staticmethod
    def validate_exception_policy_id(
            entity,
            exception_policy_id,
            **kwargs
    ):
        assert entity.exception_policy_id == exception_policy_id

    @staticmethod
    def validate_queue_labels(
            entity,
            label_collection,  # type: LabelCollection
            **kwargs
    ):
        assert isinstance(entity.labels, LabelCollection) is True
        assert 'Id' in entity.labels
        assert entity.labels['Id'] == entity.id

        updated_label_collection = dict(label_collection)
        updated_label_collection['Id'] = entity.id
        assert entity.labels == updated_label_collection

    @staticmethod
    def validate_queue(
            job_queue,
            **kwargs
    ):
        if 'identifier' in kwargs:
            JobQueueValidator.validate_id(job_queue, kwargs.pop("identifier"))

        if 'name' in kwargs:
            JobQueueValidator.validate_name(job_queue, kwargs.pop("name"))

        if 'distribution_policy_id' in kwargs:
            JobQueueValidator.validate_distribution_policy_id(job_queue, kwargs.pop("distribution_policy_id"))

        if 'exception_policy_id' in kwargs:
            JobQueueValidator.validate_exception_policy_id(job_queue, kwargs.pop("exception_policy_id"))

        if 'labels' in kwargs:
            JobQueueValidator.validate_queue_labels(job_queue, kwargs.pop("labels"))


class ClassificationPolicyValidator(object):
    @staticmethod
    def validate_id(
            entity,
            identifier,
            **kwargs
    ):
        assert entity.id == identifier

    @staticmethod
    def validate_name(
            entity,
            name,
            **kwargs
    ):
        assert entity.name == name

    @staticmethod
    def validate_fallback_queue_id(
            entity,
            fallback_queue_id,
            **kwargs
    ):
        assert entity.fallback_queue_id == fallback_queue_id

    @staticmethod
    def validate_queue_selectors(
            entity,
            queue_selectors,
            **kwargs
    ):
        assert len(entity.queue_selectors) == len(queue_selectors)

        for actual, expected in zip(entity.queue_selectors, queue_selectors):
            assert type(actual) == type(expected)
            assert actual == expected

    @staticmethod
    def validate_prioritization_rule(
            entity,
            prioritization_rule,
            **kwargs
    ):
        assert type(entity.prioritization_rule) == type(prioritization_rule)
        assert entity.prioritization_rule == prioritization_rule

    @staticmethod
    def validate_worker_selectors(
            entity,
            worker_selectors,
            **kwargs
    ):
        assert len(entity.worker_selectors) == len(worker_selectors)

        for actual, expected in zip(entity.worker_selectors, worker_selectors):
            assert type(actual) == type(expected)
            assert actual == expected

    @staticmethod
    def validate_classification_policy(
            classification_policy,
            **kwargs
    ):
        if 'identifier' in kwargs:
            ClassificationPolicyValidator.validate_id(classification_policy, kwargs.pop("identifier"))

        if 'name' in kwargs:
            ClassificationPolicyValidator.validate_name(classification_policy, kwargs.pop("name"))

        if 'fallback_queue_id' in kwargs:
            ClassificationPolicyValidator.validate_fallback_queue_id(classification_policy, kwargs.pop("fallback_queue_id"))

        if 'queue_selectors' in kwargs:
            ClassificationPolicyValidator.validate_queue_selectors(classification_policy, kwargs.pop("queue_selectors"))

        if 'prioritization_rule' in kwargs:
            ClassificationPolicyValidator.validate_prioritization_rule(classification_policy, kwargs.pop("prioritization_rule"))

        if 'worker_selectors' in kwargs:
            ClassificationPolicyValidator.validate_worker_selectors(classification_policy, kwargs.pop("worker_selectors"))


class ExceptionPolicyValidator(object):
    @staticmethod
    def validate_id(
            entity,
            identifier,
            **kwargs
    ):
        assert entity.id == identifier

    @staticmethod
    def validate_name(
            entity,
            name,
            **kwargs
    ):
        assert entity.name == name

    @staticmethod
    def validate_exception_trigger(
            actual,  # type: Union[QueueLengthExceptionTrigger, WaitTimeExceptionTrigger]
            expected,  # type: Union[QueueLengthExceptionTrigger, WaitTimeExceptionTrigger]
            **kwargs,  # type: Any
    ):
        assert isinstance(actual, type(expected))
        assert actual == expected

    @staticmethod
    def validate_exception_actions(
            actual,  # type: Dict[str, Union[ReclassifyExceptionAction, ManualReclassifyExceptionAction, CancelExceptionAction]]
            expected,  # type: Dict[str, Union[ReclassifyExceptionAction, ManualReclassifyExceptionAction, CancelExceptionAction]]
            **kwargs,  # type: Any
    ):
        assert len(actual) == len(expected)

        for a, e in zip(actual.items(), expected.items()):
            assert a[0] == e[0]
            assert isinstance(a[1], type(e[1])) is True
            actual_exception_action = a[1]
            expected_exception_action = e[1]

            if isinstance(actual_exception_action, ManualReclassifyExceptionAction):
                assert actual_exception_action.queue_id == expected_exception_action.queue_id
                assert actual_exception_action.priority == expected_exception_action.priority

                if expected_exception_action.worker_selectors is not None:
                    assert len(actual_exception_action.worker_selectors) \
                           == len(expected_exception_action.worker_selectors)
                    for aws, ews in zip(actual_exception_action.worker_selectors,
                                        expected_exception_action.worker_selectors):
                        assert aws == ews
                else:
                    assert len(actual_exception_action.worker_selectors) == 0

            elif isinstance(actual_exception_action, ReclassifyExceptionAction):
                assert actual_exception_action.classification_policy_id == \
                       expected_exception_action.classification_policy_id

                if actual_exception_action.labels_to_upsert is not None:
                    assert Counter(actual_exception_action.labels_to_upsert) == \
                           Counter(expected_exception_action.labels_to_upsert)

            elif isinstance(actual_exception_action, CancelExceptionAction):
                assert actual_exception_action == expected_exception_action

            else:
                raise AssertionError("Unable to determine ExceptionAction type")

    @staticmethod
    def validate_exception_rules(
            entity,  # type: ExceptionPolicy
            exception_rules,  # type: Dict[str, ExceptionRule]
            **kwargs
    ):
        for k, v in exception_rules.items():
            if k in entity.exception_rules:
                assert isinstance(entity.exception_rules[k], type(exception_rules[k])) is True
                actual_rule = entity.exception_rules[k]
                expected_rule = v

                assert isinstance(actual_rule, ExceptionRule) is True
                assert isinstance(expected_rule, ExceptionRule) is True

                ExceptionPolicyValidator.validate_exception_trigger(actual_rule.trigger,
                                                                    expected_rule.trigger)
                assert any(actual_rule.actions) is True
                assert any(expected_rule.actions) is True

                ExceptionPolicyValidator.validate_exception_actions(actual_rule.actions,
                                                                    expected_rule.actions)

            else:
                # key is not present in policy hence was set to None for request
                assert exception_rules[k] is None

    @staticmethod
    def validate_exception_policy(
            exception_policy,
            **kwargs
    ):
        if 'identifier' in kwargs:
            ExceptionPolicyValidator.validate_id(exception_policy, kwargs.pop("identifier"))

        if 'name' in kwargs:
            ExceptionPolicyValidator.validate_name(exception_policy, kwargs.pop("name"))

        if 'exception_rules' in kwargs:
            ExceptionPolicyValidator.validate_exception_rules(exception_policy, kwargs.pop("exception_rules"))


class RouterWorkerValidator(object):

    @staticmethod
    def validate_id(
            entity,
            identifier,
            **kwargs
    ):
        assert entity.id == identifier

    @staticmethod
    def validate_total_capacity(
            entity,
            total_capacity,
            **kwargs
    ):
        assert entity.total_capacity == total_capacity

    @staticmethod
    def validate_labels(
            entity,
            label_collection,
            **kwargs
    ):
        assert isinstance(entity.labels, LabelCollection) is True
        assert 'Id' in entity.labels
        assert entity.labels['Id'] == entity.id

        updated_label_collection = dict(label_collection)
        updated_label_collection['Id'] = entity.id
        assert entity.labels == updated_label_collection

    @staticmethod
    def validate_tags(
            entity,
            tag_collection,
            **kwargs
    ):
        assert isinstance(entity.tags, LabelCollection) is True
        assert entity.tags == tag_collection

    @staticmethod
    def validate_queue_assignment(
            entity,
            queue_assignments,  # type: dict[str, QueueAssignment]
            **kwargs
    ):
        assert len(entity.queue_assignments) == len(queue_assignments)
        for k, v in queue_assignments.items():
            assert k in entity.queue_assignments

    @staticmethod
    def validate_channel_configurations(
            entity,  # type: RouterWorker
            channel_configurations,  # type: dict[str, ChannelConfiguration]
            **kwargs
    ):
        assert len(entity.channel_configurations) == len(channel_configurations)
        for k, v in channel_configurations.items():
            assert k in entity.channel_configurations
            assert entity.channel_configurations[k] == v

    @staticmethod
    def validate_worker_availability(
            entity,  # type: RouterWorker
            available_for_offers,  # type: bool
            **kwargs,  # type: Any
    ):
        assert entity.available_for_offers == available_for_offers
        if entity.available_for_offers is True:
            assert entity.state == RouterWorkerState.ACTIVE
        else:
            assert entity.state == RouterWorkerState.DRAINING \
                   or entity.state == RouterWorkerState.INACTIVE

    @staticmethod
    def validate_worker(
            worker,
            **kwargs
    ):
        if 'identifier' in kwargs:
            RouterWorkerValidator.validate_id(worker, kwargs.pop("identifier"))

        if 'total_capacity' in kwargs:
            RouterWorkerValidator.validate_total_capacity(worker, kwargs.pop("total_capacity"))

        if 'labels' in kwargs:
            RouterWorkerValidator.validate_labels(worker, kwargs.pop("labels"))

        if 'tags' in kwargs:
            RouterWorkerValidator.validate_tags(worker, kwargs.pop("tags"))

        if 'queue_assignments' in kwargs:
            RouterWorkerValidator.validate_queue_assignment(worker, kwargs.pop("queue_assignments"))

        if 'channel_configurations' in kwargs:
            RouterWorkerValidator.validate_channel_configurations(worker, kwargs.pop("channel_configurations"))

        if 'available_for_offers' in kwargs:
            RouterWorkerValidator.validate_worker_availability(worker, kwargs.pop("available_for_offers"))
