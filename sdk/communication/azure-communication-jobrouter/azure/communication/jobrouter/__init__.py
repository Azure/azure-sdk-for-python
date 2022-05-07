from ._version import VERSION
from ._router_client import RouterClient
from ._generated.models import (
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
    DirectMapRule,
    ExpressionRule,
    AzureFunctionRule,
    AzureFunctionRuleCredential,
    DistributionPolicy,
    DistributionMode,
    BestWorkerMode,
    LongestIdleMode,
    RoundRobinMode,
    ExceptionPolicy,
    ExceptionRule,
    QueueLengthExceptionTrigger,
    WaitTimeExceptionTrigger,
    ReclassifyExceptionAction,
    ManualReclassifyExceptionAction,
    CancelExceptionAction,
    RouterJob,
    QueueStatistics,
)

from ._models import (
    LabelCollection,
    JobQueue
)

from ._shared.user_credential import CommunicationTokenCredential

__all__ = [
    # Clients
    'RouterClient',

    # Generated models
    'ClassificationPolicy',
    'LabelOperator',
    'QueueSelector',
    'StaticQueueSelector',
    'ConditionalQueueSelector',
    'RuleEngineQueueSelector',
    'PassThroughQueueSelector',
    'QueueWeightedAllocation',
    'WeightedAllocationQueueSelector',
    'WorkerSelector',
    'StaticWorkerSelector',
    'ConditionalWorkerSelector',
    'RuleEngineWorkerSelector',
    'PassThroughWorkerSelector',
    'WorkerWeightedAllocation',
    'WeightedAllocationWorkerSelector',
    'StaticRule',
    'DirectMapRule',
    'ExpressionRule',
    'AzureFunctionRule',
    'AzureFunctionRuleCredential',
    'DistributionPolicy',
    'DistributionMode',
    'BestWorkerMode',
    'LongestIdleMode',
    'RoundRobinMode',
    'ExceptionPolicy',
    'ExceptionRule',
    'QueueLengthExceptionTrigger',
    'WaitTimeExceptionTrigger',
    'ReclassifyExceptionAction',
    'ManualReclassifyExceptionAction',
    'CancelExceptionAction',
    'RouterJob',
    'QueueStatistics',

    # Created models
    'LabelCollection',
    'JobQueue',

    # Credentials
    'CommunicationTokenCredential'
]

__version__ = VERSION
