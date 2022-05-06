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
    RouterJob,
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
    'JobQueue',
    'RouterJob',

    # Created models
    'LabelCollection',

    # Credentials
    'CommunicationTokenCredential'
]

__version__ = VERSION
