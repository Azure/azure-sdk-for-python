# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime
from azure.communication.jobrouter._model_base import _deserialize_datetime as _convert_str_to_datetime
from collections import Counter
from typing import Any, Dict, List, Union

from router_test_constants import SANITIZED, FAKE_FUNCTION_URI
from azure.communication.jobrouter.models import (
    BestWorkerMode,
    LongestIdleMode,
    RoundRobinMode,
    ExceptionRule,
    ExceptionPolicy,
    QueueLengthExceptionTrigger,
    WaitTimeExceptionTrigger,
    ReclassifyExceptionAction,
    ManualReclassifyExceptionAction,
    CancelExceptionAction,
    RouterChannel,
    RouterWorker,
    RouterWorkerState,
    RouterJob,
    StaticWorkerSelectorAttachment,
    ConditionalWorkerSelectorAttachment,
    RuleEngineWorkerSelectorAttachment,
    PassThroughWorkerSelectorAttachment,
    WorkerWeightedAllocation,
    WeightedAllocationWorkerSelectorAttachment,
    StaticQueueSelectorAttachment,
    ConditionalQueueSelectorAttachment,
    RuleEngineQueueSelectorAttachment,
    PassThroughQueueSelectorAttachment,
    QueueWeightedAllocation,
    WeightedAllocationQueueSelectorAttachment,
    RouterWorkerSelector,
    FunctionRouterRule,
    FunctionRouterRuleCredential,
    StaticRouterRule,
    RouterQueueSelector,
    ExpressionRouterRule,
    LabelOperator,
    RouterJobNote,
    RouterRuleKind,
    DistributionModeKind,
    ExceptionTriggerKind,
    ExceptionActionKind,
    QueueSelectorAttachmentKind,
    WorkerSelectorAttachmentKind,
    JobMatchingModeKind,
)


class DistributionPolicyValidator(object):
    @staticmethod
    def validate_id(distribution_policy, id, **kwargs):
        assert distribution_policy.id == id

    @staticmethod
    def validate_name(distribution_policy, name, **kwargs):
        assert distribution_policy.name == name

    @staticmethod
    def validate_offer_ttl(distribution_policy, offer_ttl_seconds, **kwargs):
        assert distribution_policy.offer_expires_after_seconds == offer_ttl_seconds

    @staticmethod
    def validate_longest_idle_mode(distribution_policy, mode, **kwargs):
        assert distribution_policy.mode.kind == DistributionModeKind.LONGEST_IDLE

    @staticmethod
    def validate_round_robin_mode(distribution_policy, mode, **kwargs):
        assert distribution_policy.mode.kind == DistributionModeKind.ROUND_ROBIN

    @staticmethod
    def validate_best_worker_mode(distribution_policy, mode, **kwargs):
        assert distribution_policy.mode.kind == DistributionModeKind.BEST_WORKER
        # TODO: Add more validations for best worker mode

    @staticmethod
    def validate_distribution_mode(distribution_policy, mode, **kwargs):
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

        if kwargs.get("identifier", None) is not None:
            DistributionPolicyValidator.validate_id(distribution_policy, kwargs.pop("identifier"))

        if kwargs.get("name", None) is not None:
            DistributionPolicyValidator.validate_name(distribution_policy, kwargs.pop("name"))

        if kwargs.get("offer_expires_after_seconds", None) is not None:
            DistributionPolicyValidator.validate_offer_ttl(
                distribution_policy, kwargs.pop("offer_expires_after_seconds")
            )

        if kwargs.get("mode", None) is not None:
            DistributionPolicyValidator.validate_distribution_mode(distribution_policy, kwargs.pop("mode"))


class JobQueueValidator(object):
    @staticmethod
    def validate_id(entity, identifier, **kwargs):
        assert entity.id == identifier

    @staticmethod
    def validate_name(entity, name, **kwargs):
        assert entity.name == name

    @staticmethod
    def validate_distribution_policy_id(entity, distribution_policy_id, **kwargs):
        assert entity.distribution_policy_id == distribution_policy_id

    @staticmethod
    def validate_exception_policy_id(entity, exception_policy_id, **kwargs):
        assert entity.exception_policy_id == exception_policy_id

    @staticmethod
    def validate_queue_labels(
        entity,
        label_collection,  # type: Dict[str, Union[int, float, str, bool]]
        **kwargs,
    ):
        assert isinstance(entity.labels, dict) is True
        assert "Id" in entity.labels
        assert entity.labels["Id"] == entity.id

        updated_label_collection = dict(label_collection)
        updated_label_collection["Id"] = entity.id
        assert entity.labels == updated_label_collection

    @staticmethod
    def validate_queue(job_queue, **kwargs):
        if "identifier" in kwargs:
            JobQueueValidator.validate_id(job_queue, kwargs.pop("identifier"))

        if "name" in kwargs:
            JobQueueValidator.validate_name(job_queue, kwargs.pop("name"))

        if "distribution_policy_id" in kwargs:
            JobQueueValidator.validate_distribution_policy_id(job_queue, kwargs.pop("distribution_policy_id"))

        if "exception_policy_id" in kwargs:
            JobQueueValidator.validate_exception_policy_id(job_queue, kwargs.pop("exception_policy_id"))

        if "labels" in kwargs:
            JobQueueValidator.validate_queue_labels(job_queue, kwargs.pop("labels"))


class WorkerSelectorValidator(object):
    @staticmethod
    def validate_worker_selector(
        actual,  # type: RouterWorkerSelector
        expected,  # type: RouterWorkerSelector
        **kwargs,  # type: Any
    ):
        LabelOperatorValidator.validate_label_operator(actual.label_operator, expected.label_operator)
        assert actual.key == expected.key
        assert actual.value == expected.value
        assert actual.expires_at == expected.expires_at

        if expected.expedite is None:
            assert actual.expedite is False
        else:
            assert actual.expedite == expected.expedite


class QueueSelectorValidator(object):
    @staticmethod
    def validate_queue_selector(
        actual,  # type: QueueSelector
        expected,  # type: QueueSelector
        **kwargs,  # type: Any
    ):
        LabelOperatorValidator.validate_label_operator(actual.label_operator, expected.label_operator)
        assert actual.key == expected.key
        assert actual.value == expected.value


class RouterRuleValidator(object):
    @staticmethod
    def validate_function_rule(actual: FunctionRouterRule, expected: FunctionRouterRule, **kwargs: Any):
        assert actual.kind == expected.kind
        assert actual.function_uri == expected.function_uri or actual.function_uri == FAKE_FUNCTION_URI
        if actual.credential:
            assert expected.credential is not None

            actual_credential: FunctionRouterRuleCredential = actual.credential
            if actual_credential.function_key:
                assert (
                    actual_credential.function_key == actual.credential.function_key
                    or actual_credential.function_key == SANITIZED
                )
            if actual_credential.app_key:
                assert actual_credential.app_key == actual.credential.app_key or actual_credential.app_key == SANITIZED
            if actual_credential.client_id:
                assert (
                    actual_credential.client_id == actual.credential.client_id
                    or actual_credential.client_id == SANITIZED
                )

    @staticmethod
    def validate_static_rule(actual: StaticRouterRule, expected: StaticRouterRule, **kwargs: Any):
        assert actual.kind == expected.kind
        if type(actual.value) == list:
            for i, j in zip(actual.value, expected.value):
                if type(i) == RouterWorkerSelector:
                    WorkerSelectorValidator.validate_worker_selector(i, j)
                if type(i) == RouterQueueSelector:
                    QueueSelectorValidator.validate_queue_selector(i, j)

    @staticmethod
    def validate_expression_rule(actual: ExpressionRouterRule, expected: ExpressionRouterRule, **kwargs: Any):
        assert actual.kind == expected.kind
        assert actual.expression == expected.expression

    @staticmethod
    def validate_router_rule(actual, expected, **kwargs: Any):
        assert type(actual) == type(expected)

        if type(actual) == FunctionRouterRule:
            RouterRuleValidator.validate_function_rule(actual, expected)
        elif type(actual) == StaticRouterRule:
            RouterRuleValidator.validate_static_rule(actual, expected)
        elif type(actual) == ExpressionRouterRule:
            RouterRuleValidator.validate_expression_rule(actual, expected)
        else:
            assert actual == expected


class ClassificationPolicyValidator(object):
    @staticmethod
    def validate_id(entity, identifier, **kwargs):
        assert entity.id == identifier

    @staticmethod
    def validate_name(entity, name, **kwargs):
        assert entity.name == name

    @staticmethod
    def validate_fallback_queue_id(entity, fallback_queue_id, **kwargs):
        assert entity.fallback_queue_id == fallback_queue_id

    @staticmethod
    def validate_queue_selectors(entity, queue_selector_attachments, **kwargs):
        def validate_static_queue_selector_attachment(
            actual,  # type: StaticQueueSelectorAttachment
            expected,  # type: StaticQueueSelectorAttachment
            **kwargs,
        ):
            QueueSelectorValidator.validate_queue_selector(actual.queue_selector, expected.queue_selector)

        def validate_conditional_queue_selector_attachment(
            actual,  # type: ConditionalQueueSelectorAttachment
            expected,  # type: ConditionalQueueSelectorAttachment
            **kwargs,  # type: Any
        ):
            RouterRuleValidator.validate_router_rule(actual.condition, expected.condition)

            for i, j in zip(actual.queue_selectors, expected.queue_selectors):
                QueueSelectorValidator.validate_queue_selector(i, j)

        def validate_rule_engine_selector_attachment(
            actual,  # type: RuleEngineQueueSelectorAttachment
            expected,  # type: RuleEngineQueueSelectorAttachment
            **kwargs,  # type: Any
        ):
            RouterRuleValidator.validate_router_rule(actual.rule, expected.rule)

        def validate_weighted_allocation_selector_attachment(
            actual,  # type: WeightedAllocationQueueSelectorAttachment
            expected,  # type: WeightedAllocationQueueSelectorAttachment
            **kwargs,  # type: Any
        ):
            for i, j in zip(actual.allocations, expected.allocations):
                assert i.weight == j.weight
                for ac_qs, ex_qs in zip(i.queue_selectors, j.queue_selectors):
                    QueueSelectorValidator.validate_queue_selector(ac_qs, ex_qs)

        def validate_passthrough_attachment(
            actual,  # type: PassThroughQueueSelectorAttachment
            expected,  # type: PassThroughQueueSelectorAttachment
            **kwargs,  # type: Any
        ):
            assert actual.kind == expected.kind
            assert actual.key == expected.key
            LabelOperatorValidator.validate_label_operator(actual.label_operator, expected.label_operator)

        assert len(entity.queue_selector_attachments) == len(queue_selector_attachments)

        for actual, expected in zip(entity.queue_selector_attachments, queue_selector_attachments):
            assert type(actual) == type(expected)

            if type(actual) == StaticQueueSelectorAttachment:
                validate_static_queue_selector_attachment(actual, expected)
            elif type(actual) == ConditionalQueueSelectorAttachment:
                validate_conditional_queue_selector_attachment(actual, expected)
            elif type(actual) == WeightedAllocationQueueSelectorAttachment:
                validate_weighted_allocation_selector_attachment(actual, expected)
            elif type(actual) == RuleEngineQueueSelectorAttachment:
                validate_rule_engine_selector_attachment(actual, expected)
            elif type(actual) == PassThroughQueueSelectorAttachment:
                validate_passthrough_attachment(actual, expected)
            else:
                assert actual == expected

    @staticmethod
    def validate_prioritization_rule(entity, prioritization_rule, **kwargs):
        assert type(entity.prioritization_rule) == type(prioritization_rule)
        RouterRuleValidator.validate_router_rule(entity.prioritization_rule, prioritization_rule)

    @staticmethod
    def validate_worker_selectors(entity, worker_selector_attachments, **kwargs):
        def validate_static_worker_selector_attachment(
            actual,  # type: StaticWorkerSelectorAttachment
            expected,  # type: StaticWorkerSelectorAttachment
            **kwargs,
        ):
            WorkerSelectorValidator.validate_worker_selector(actual.worker_selector, expected.worker_selector)

        def validate_conditional_worker_selector_attachment(
            actual,  # type: ConditionalWorkerSelectorAttachment
            expected,  # type: ConditionalWorkerSelectorAttachment
            **kwargs,  # type: Any
        ):
            RouterRuleValidator.validate_router_rule(actual.condition, expected.condition)

            for i, j in zip(actual.worker_selectors, expected.worker_selectors):
                WorkerSelectorValidator.validate_worker_selector(i, j)

        def validate_rule_engine_selector_attachment(
            actual,  # type: RuleEngineWorkerSelectorAttachment
            expected,  # type: RuleEngineWorkerSelectorAttachment
            **kwargs,  # type: Any
        ):
            RouterRuleValidator.validate_router_rule(actual.rule, expected.rule)

        def validate_weighted_allocation_selector_attachment(
            actual,  # type: WeightedAllocationWorkerSelectorAttachment
            expected,  # type: WeightedAllocationWorkerSelectorAttachment
            **kwargs,  # type: Any
        ):
            for i, j in zip(actual.allocations, expected.allocations):
                assert i.weight == j.weight
                for ac_ws, ex_ws in zip(i.worker_selectors, j.worker_selectors):
                    WorkerSelectorValidator.validate_worker_selector(ac_ws, ex_ws)

        def validate_passthrough_attachment(
            actual,  # type: PassThroughWorkerSelectorAttachment
            expected,  # type: PassThroughWorkerSelectorAttachment
            **kwargs,  # type: Any
        ):
            assert actual.kind == expected.kind
            assert actual.key == expected.key
            LabelOperatorValidator.validate_label_operator(actual.label_operator, expected.label_operator)

        assert len(entity.worker_selector_attachments) == len(worker_selector_attachments)

        for actual, expected in zip(entity.worker_selector_attachments, worker_selector_attachments):
            assert type(actual) == type(expected)

            if type(actual) == StaticWorkerSelectorAttachment:
                validate_static_worker_selector_attachment(actual, expected)
            elif type(actual) == ConditionalWorkerSelectorAttachment:
                validate_conditional_worker_selector_attachment(actual, expected)
            elif type(actual) == WeightedAllocationWorkerSelectorAttachment:
                validate_weighted_allocation_selector_attachment(actual, expected)
            elif type(actual) == RuleEngineWorkerSelectorAttachment:
                validate_rule_engine_selector_attachment(actual, expected)
            elif type(actual) == PassThroughWorkerSelectorAttachment:
                validate_passthrough_attachment(actual, expected)
            else:
                assert actual == expected

    @staticmethod
    def validate_classification_policy(classification_policy, **kwargs):
        if "identifier" in kwargs:
            ClassificationPolicyValidator.validate_id(classification_policy, kwargs.pop("identifier"))

        if "name" in kwargs:
            ClassificationPolicyValidator.validate_name(classification_policy, kwargs.pop("name"))

        if "fallback_queue_id" in kwargs:
            ClassificationPolicyValidator.validate_fallback_queue_id(
                classification_policy, kwargs.pop("fallback_queue_id")
            )

        if "queue_selector_attachments" in kwargs:
            ClassificationPolicyValidator.validate_queue_selectors(
                classification_policy, kwargs.pop("queue_selector_attachments")
            )

        if "prioritization_rule" in kwargs:
            ClassificationPolicyValidator.validate_prioritization_rule(
                classification_policy, kwargs.pop("prioritization_rule")
            )

        if "worker_selector_attachments" in kwargs:
            ClassificationPolicyValidator.validate_worker_selectors(
                classification_policy, kwargs.pop("worker_selector_attachments")
            )


class LabelOperatorValidator(object):
    @staticmethod
    def validate_label_operator(actual, expected, **kwargs):
        try:
            assert actual == expected
        except AssertionError:
            assert LabelOperator._value2member_map_[actual] == LabelOperator.__getattr__(expected.split(".", 1)[1])


class ExceptionPolicyValidator(object):
    @staticmethod
    def validate_id(entity, identifier, **kwargs):
        assert entity.id == identifier

    @staticmethod
    def validate_name(entity, name, **kwargs):
        assert entity.name == name

    @staticmethod
    def validate_exception_trigger(
        actual,  # type: Union[QueueLengthExceptionTrigger, WaitTimeExceptionTrigger]
        expected,  # type: Union[QueueLengthExceptionTrigger, WaitTimeExceptionTrigger]
        **kwargs,  # type: Any
    ):
        def validate_queue_length_exception_trigger(
            actual,  # type: QueueLengthExceptionTrigger
            expected,  # type: QueueLengthExceptionTrigger
            **kwargs,  # type: Any
        ):
            assert actual.kind == expected.kind
            assert actual.threshold == expected.threshold

        def validate_wait_time_exception_trigger(
            actual,  # type: WaitTimeExceptionTrigger
            expected,  # type: WaitTimeExceptionTrigger
            **kwargs,  # type: Any
        ):
            assert actual.kind == expected.kind
            assert actual.threshold_seconds == expected.threshold_seconds

        assert isinstance(actual, type(expected))
        if type(actual) == QueueLengthExceptionTrigger:
            validate_queue_length_exception_trigger(actual, expected)
        elif type(actual) == WaitTimeExceptionTrigger:
            validate_wait_time_exception_trigger(actual, expected)
        else:
            raise AssertionError("Unable to determine ExceptionTrigger type")

    @staticmethod
    def validate_exception_actions(
        actual,  # type: List[Union[ReclassifyExceptionAction, ManualReclassifyExceptionAction, CancelExceptionAction]]
        expected,  # type: List[Union[ReclassifyExceptionAction, ManualReclassifyExceptionAction, CancelExceptionAction]]
        **kwargs,  # type: Any
    ):
        assert len(actual) == len(expected)

        for actual_exception_action, expected_exception_action in zip(actual, expected):
            if isinstance(actual_exception_action, ManualReclassifyExceptionAction):
                assert actual_exception_action.queue_id == expected_exception_action.queue_id
                assert actual_exception_action.priority == expected_exception_action.priority

                if expected_exception_action.worker_selectors is not None:
                    assert len(actual_exception_action.worker_selectors) == len(
                        expected_exception_action.worker_selectors
                    )
                    for aws, ews in zip(
                        actual_exception_action.worker_selectors, expected_exception_action.worker_selectors
                    ):
                        assert aws == ews
                else:
                    assert len(actual_exception_action.worker_selectors) == 0

            elif isinstance(actual_exception_action, ReclassifyExceptionAction):
                assert (
                    actual_exception_action.classification_policy_id
                    == expected_exception_action.classification_policy_id
                )

                if actual_exception_action.labels_to_upsert is not None:
                    assert Counter(actual_exception_action.labels_to_upsert) == Counter(
                        expected_exception_action.labels_to_upsert
                    )

            elif isinstance(actual_exception_action, CancelExceptionAction):
                assert actual_exception_action.kind == expected_exception_action.kind
                assert actual_exception_action.note == expected_exception_action.note
                assert actual_exception_action.disposition_code == expected_exception_action.disposition_code

            else:
                raise AssertionError("Unable to determine ExceptionAction type")

    @staticmethod
    def validate_exception_rules(
        entity,  # type: ExceptionPolicy
        exception_rules,  # type: List[ExceptionRule]
        **kwargs,
    ):
        for expected_rule, actual_rule in zip(exception_rules, entity.exception_rules):
            assert isinstance(actual_rule, type(expected_rule)) is True
            assert isinstance(actual_rule, ExceptionRule) is True
            assert isinstance(expected_rule, ExceptionRule) is True

            ExceptionPolicyValidator.validate_exception_trigger(actual_rule.trigger, expected_rule.trigger)
            assert any(actual_rule.actions) is True
            assert any(expected_rule.actions) is True

            ExceptionPolicyValidator.validate_exception_actions(actual_rule.actions, expected_rule.actions)

    @staticmethod
    def validate_exception_policy(exception_policy, **kwargs):
        if "identifier" in kwargs:
            ExceptionPolicyValidator.validate_id(exception_policy, kwargs.pop("identifier"))

        if "name" in kwargs:
            ExceptionPolicyValidator.validate_name(exception_policy, kwargs.pop("name"))

        if "exception_rules" in kwargs:
            ExceptionPolicyValidator.validate_exception_rules(exception_policy, kwargs.pop("exception_rules"))


class RouterWorkerValidator(object):
    @staticmethod
    def validate_id(entity, identifier, **kwargs):
        assert entity.id == identifier

    @staticmethod
    def validate_total_capacity(entity, total_capacity, **kwargs):
        assert entity.capacity == total_capacity

    @staticmethod
    def validate_labels(entity, label_collection, **kwargs):
        assert isinstance(entity.labels, dict) is True
        assert "Id" in entity.labels
        assert entity.labels["Id"] == entity.id

        updated_label_collection = dict(label_collection)
        updated_label_collection["Id"] = entity.id
        assert entity.labels == updated_label_collection

    @staticmethod
    def validate_tags(entity, tag_collection, **kwargs):
        assert isinstance(entity.tags, dict) is True
        assert entity.tags == tag_collection

    @staticmethod
    def validate_queue_assignment(
        entity,
        queue_assignments,  # type: List[str]
        **kwargs,
    ):
        assert len(entity.queues) == len(queue_assignments)
        for k, v in zip(entity.queues, queue_assignments):
            assert k == v

    @staticmethod
    def validate_channel_configurations(
        entity,  # type: RouterWorker
        channel_configurations,  # type: List[RouterChannel]
        **kwargs,
    ):
        assert len(entity.channels) == len(channel_configurations)
        for k, v in zip(entity.channels, channel_configurations):
            assert k == v

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
            assert entity.state == RouterWorkerState.DRAINING or entity.state == RouterWorkerState.INACTIVE

    @staticmethod
    def validate_max_concurrent_offers(entity, max_concurrent_offers, **kwargs):
        assert entity.max_concurrent_offers == max_concurrent_offers

    @staticmethod
    def validate_worker(worker, **kwargs):
        if "identifier" in kwargs:
            RouterWorkerValidator.validate_id(worker, kwargs.pop("identifier"))

        if "capacity" in kwargs:
            RouterWorkerValidator.validate_total_capacity(worker, kwargs.pop("capacity"))

        if "labels" in kwargs:
            RouterWorkerValidator.validate_labels(worker, kwargs.pop("labels"))

        if "tags" in kwargs:
            RouterWorkerValidator.validate_tags(worker, kwargs.pop("tags"))

        if "queues" in kwargs:
            RouterWorkerValidator.validate_queue_assignment(worker, kwargs.pop("queues"))

        if "channels" in kwargs:
            RouterWorkerValidator.validate_channel_configurations(worker, kwargs.pop("channels"))

        if "available_for_offers" in kwargs:
            RouterWorkerValidator.validate_worker_availability(worker, kwargs.pop("available_for_offers"))

        if "max_concurrent_offers" in kwargs:
            RouterWorkerValidator.validate_max_concurrent_offers(worker, kwargs.pop("max_concurrent_offers"))


class RouterJobValidator(object):
    @staticmethod
    def validate_id(entity: RouterJob, identifier, **kwargs):
        assert entity.id == identifier

    @staticmethod
    def validate_channel_reference(entity: RouterJob, channel_reference, **kwargs):
        assert entity.channel_reference == channel_reference

    @staticmethod
    def validate_channel_id(entity: RouterJob, channel_id, **kwargs):
        assert entity.channel_id == channel_id

    @staticmethod
    def validate_queue_id(entity: RouterJob, queue_id, **kwargs):
        assert entity.queue_id == queue_id

    @staticmethod
    def validate_job_priority(entity: RouterJob, job_priority, **kwargs):
        assert entity.priority == job_priority

    @staticmethod
    def validate_requested_worker_selectors(entity: RouterJob, requested_worker_selectors, **kwargs):
        assert len(entity.requested_worker_selectors) == len(requested_worker_selectors)

        for actual, expected in zip(entity.requested_worker_selectors, requested_worker_selectors):
            assert type(actual) == type(expected)
            WorkerSelectorValidator.validate_worker_selector(actual, expected)

    @staticmethod
    def validate_labels(entity: RouterJob, label_collection, **kwargs):
        assert isinstance(entity.labels, dict) is True
        assert entity.labels == label_collection

    @staticmethod
    def validate_tags(entity: RouterJob, tag_collection, **kwargs):
        assert isinstance(entity.tags, dict) is True
        assert entity.tags == tag_collection

    @staticmethod
    def validate_notes(entity: RouterJob, note_collection: List[RouterJobNote], **kwargs):
        assert isinstance(entity.notes, list) is True
        assert len(entity.notes) == len(note_collection)

        for k1, k2 in zip(entity.notes, note_collection):
            assert k1.message == k2.message
            assert k1.added_at is not None and k2.added_at is not None

    @staticmethod
    def validate_scheduled_time_utc(entity: RouterJob, scheduled_time_utc: Union[str, datetime], **kwargs):
        if isinstance(scheduled_time_utc, datetime):
            assert entity.scheduled_time_utc == scheduled_time_utc
        elif isinstance(scheduled_time_utc, str):
            scheduled_time_utc_as_dt: datetime = _convert_str_to_datetime(scheduled_time_utc)
            assert entity.scheduled_time_utc == scheduled_time_utc_as_dt
        else:
            raise AssertionError

    @staticmethod
    def validate_unavailable_for_matching(entity: RouterJob, unavailable_for_matching, **kwargs):
        assert entity.unavailable_for_matching == unavailable_for_matching

    @staticmethod
    def validate_job(router_job: RouterJob, **kwargs: Any):
        if "identifier" in kwargs:
            RouterJobValidator.validate_id(router_job, kwargs.pop("identifier"))

        if "channel_reference" in kwargs:
            RouterJobValidator.validate_channel_reference(router_job, kwargs.pop("channel_reference"))

        if "channel_id" in kwargs:
            RouterJobValidator.validate_channel_id(router_job, kwargs.pop("channel_id"))

        if "queue_id" in kwargs:
            RouterJobValidator.validate_queue_id(router_job, kwargs.pop("queue_id"))

        if "priority" in kwargs:
            RouterJobValidator.validate_job_priority(router_job, kwargs.pop("priority"))

        if "requested_worker_selectors" in kwargs:
            RouterJobValidator.validate_requested_worker_selectors(router_job, kwargs.pop("requested_worker_selectors"))

        if "labels" in kwargs:
            RouterJobValidator.validate_labels(router_job, kwargs.pop("labels"))

        if "tags" in kwargs:
            RouterJobValidator.validate_tags(router_job, kwargs.pop("tags"))

        if "notes" in kwargs:
            RouterJobValidator.validate_notes(router_job, kwargs.pop("notes"))

        if "scheduled_time_utc" in kwargs:
            RouterJobValidator.validate_scheduled_time_utc(router_job, kwargs.pop("scheduled_time_utc"))

        if "unavailable_for_matching" in kwargs:
            RouterJobValidator.validate_unavailable_for_matching(router_job, kwargs.pop("unavailable_for_matching"))
