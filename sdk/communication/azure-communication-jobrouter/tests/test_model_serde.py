# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import datetime
import unittest
from azure.communication.jobrouter import (
    ScoringRuleOptions,
    ScoringRuleParameterSelector,
    StaticQueueSelectorAttachment,
    ConditionalQueueSelectorAttachment,
    RouterQueueSelector,
    LabelOperator,
    ClassificationPolicy,
    StaticRouterRule,
    ExpressionRouterRule,
    FunctionRouterRule,
    FunctionRouterRuleCredential,
    BestWorkerMode,
    LongestIdleMode,
    RoundRobinMode,
    DistributionPolicy,
    JobMatchingMode,
    ScheduleAndSuspendMode,
)

from azure.communication.jobrouter._router_serializer import _deserialize_from_json, _serialize_to_json

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
    )
]

prioritization_rules = [
    StaticRouterRule(value = 1),
    ExpressionRouterRule(expression = "1"),
    FunctionRouterRule(
        function_uri = "https://fake.azurewebsites.net/fakeRule",
        credential = FunctionRouterRuleCredential(function_key = "fakeKey"))
]

min_concurrent_offer_count = 1
max_concurrent_offer_count = 1

distribution_modes = [
    BestWorkerMode(min_concurrent_offers = min_concurrent_offer_count,
                   max_concurrent_offers = max_concurrent_offer_count),
    LongestIdleMode(min_concurrent_offers = min_concurrent_offer_count,
                    max_concurrent_offers = max_concurrent_offer_count),
    RoundRobinMode(min_concurrent_offers = min_concurrent_offer_count,
                   max_concurrent_offers = max_concurrent_offer_count)
]


class TestModelSerializationDeserialization(unittest.TestCase):
    def test_static_queue_selector_attachment_is_serialized_correctly(self):
        static_attachment = StaticQueueSelectorAttachment(
            queue_selector = RouterQueueSelector(
                key = "test_key", label_operator = LabelOperator.EQUAL, value = "test_value"
            )
        )

        serialized_json = _serialize_to_json(static_attachment, "StaticQueueSelectorAttachment")
        deserialized_json = _deserialize_from_json("QueueSelectorAttachment", serialized_json)
        self.assertEqual(_serialize_to_json(static_attachment, "StaticQueueSelectorAttachment"), _serialize_to_json(deserialized_json, "StaticQueueSelectorAttachment"))

    def test_classification_policy_is_serialized_correctly(self):
        classification_policy: ClassificationPolicy = ClassificationPolicy(
            name = "fakeName",
            fallback_queue_id = "fakeQueueId",
            queue_selectors = queue_selectors,
            prioritization_rule = prioritization_rules[0]
        )

        serialized_json = _serialize_to_json(classification_policy, "ClassificationPolicy")
        deserialized_json = _deserialize_from_json("ClassificationPolicy", serialized_json)
        self.assertEqual(_serialize_to_json(classification_policy, "ClassificationPolicy"), _serialize_to_json(deserialized_json, "ClassificationPolicy"))

    def test_distribution_policy_is_serialized_correctly(self):

        for mode in distribution_modes:
            distribution_policy: DistributionPolicy = DistributionPolicy(
                    offer_expires_after_seconds = 10.0,
                    mode = mode,
                    name = "fakeName",
                )

            serialized_json = _serialize_to_json(distribution_policy, "DistributionPolicy")
            print(serialized_json)
            deserialized_json = _deserialize_from_json("DistributionPolicy", serialized_json)
            print(deserialized_json)
            self.assertEqual(_serialize_to_json(deserialized_json, "DistributionPolicy"),
                             _serialize_to_json(distribution_policy, "DistributionPolicy"))
            print("--------------------------------------------------------\n")


    def test_job_matching_mode_overloads(self):
        queue_and_match = JobMatchingMode(queue_and_match_mode = {})
        schedule_and_suspend = JobMatchingMode(
            schedule_and_suspend_mode = ScheduleAndSuspendMode(schedule_at = datetime.datetime.utcnow()))
        suspend_mode = JobMatchingMode(suspend_mode = {})

        for m in [queue_and_match, schedule_and_suspend, suspend_mode]:
            serialized_json = _serialize_to_json(m, "JobMatchingMode")
            deserialized_json = _deserialize_from_json("JobMatchingMode", serialized_json)
            self.assertEqual(_serialize_to_json(m, "JobMatchingMode"),
                             _serialize_to_json(deserialized_json, "JobMatchingMode"))


if __name__ == '__main__':
    unittest.main()
