# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.communication.jobrouter import (
    BestWorkerMode,
    LongestIdleMode,
    RoundRobinMode,
    LabelCollection
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