# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
from typing import List
from ._models import (
    BestWorkerMode,
    CancelExceptionAction,
    RouterChannel,
    ConditionalQueueSelectorAttachment,
    ConditionalWorkerSelectorAttachment,
    DirectMapRouterRule,
    DistributionMode,
    ExceptionAction,
    ExceptionRule,
    ExceptionTrigger,
    ExpressionRouterRule,
    FunctionRouterRule,
    FunctionRouterRuleCredential,
    JobMatchingMode,
    LongestIdleMode,
    ManualReclassifyExceptionAction,
    OAuth2WebhookClientCredential,
    PassThroughQueueSelectorAttachment,
    PassThroughWorkerSelectorAttachment,
    QueueAndMatchMode,
    QueueLengthExceptionTrigger,
    QueueSelectorAttachment,
    QueueWeightedAllocation,
    ReclassifyExceptionAction,
    RoundRobinMode,
    RouterJobAssignment,
    RouterJobOffer,
    RouterQueueSelector,
    RouterWorkerAssignment,
    RouterWorkerSelector,
    RuleEngineQueueSelectorAttachment,
    RuleEngineWorkerSelectorAttachment,
    ScheduleAndSuspendMode,
    ScoringRuleOptions,
    StaticQueueSelectorAttachment,
    StaticRouterRule,
    StaticWorkerSelectorAttachment,
    SuspendMode,
    WaitTimeExceptionTrigger,
    WebhookRouterRule,
    WeightedAllocationQueueSelectorAttachment,
    WeightedAllocationWorkerSelectorAttachment,
    WorkerSelectorAttachment,
    WorkerWeightedAllocation,
    RouterJobNote,
)
from ._enums import (
    ExpressionRouterRuleLanguage,
    LabelOperator,
    RouterJobStatus,
    RouterWorkerSelectorStatus,
    RouterWorkerState,
    ScoringRuleParameterSelector,
    RouterJobStatusSelector,
    RouterWorkerStateSelector,
)
from .._datetimeutils import _convert_str_to_datetime


__all__: List[str] = [
    "BestWorkerMode",
    "CancelExceptionAction",
    "RouterChannel",
    "ConditionalQueueSelectorAttachment",
    "ConditionalWorkerSelectorAttachment",
    "DirectMapRouterRule",
    "DistributionMode",
    "ExceptionAction",
    "ExceptionRule",
    "ExceptionTrigger",
    "ExpressionRouterRule",
    "FunctionRouterRule",
    "FunctionRouterRuleCredential",
    "JobMatchingMode",
    "LongestIdleMode",
    "ManualReclassifyExceptionAction",
    "OAuth2WebhookClientCredential",
    "PassThroughQueueSelectorAttachment",
    "PassThroughWorkerSelectorAttachment",
    "QueueAndMatchMode",
    "QueueLengthExceptionTrigger",
    "QueueSelectorAttachment",
    "QueueWeightedAllocation",
    "ReclassifyExceptionAction",
    "RoundRobinMode",
    "RouterJobAssignment",
    "RouterJobOffer",
    "RouterQueueSelector",
    "RouterWorkerAssignment",
    "RouterWorkerSelector",
    "RuleEngineQueueSelectorAttachment",
    "RuleEngineWorkerSelectorAttachment",
    "ScheduleAndSuspendMode",
    "ScoringRuleOptions",
    "StaticQueueSelectorAttachment",
    "StaticRouterRule",
    "StaticWorkerSelectorAttachment",
    "SuspendMode",
    "WaitTimeExceptionTrigger",
    "WebhookRouterRule",
    "WeightedAllocationQueueSelectorAttachment",
    "WeightedAllocationWorkerSelectorAttachment",
    "WorkerSelectorAttachment",
    "WorkerWeightedAllocation",
    "ExpressionRouterRuleLanguage",
    "LabelOperator",
    "RouterJobStatus",
    "RouterWorkerSelectorStatus",
    "RouterWorkerState",
    "ScoringRuleParameterSelector",
    "RouterJobStatusSelector",
    "RouterWorkerStateSelector",
    "RouterJobNote",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
