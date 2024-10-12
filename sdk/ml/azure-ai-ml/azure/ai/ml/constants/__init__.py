# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This package defines constants used in Azure Machine Learning SDKv2."""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from azure.ai.ml._restclient.v2023_10_01.models import ListViewType

from ._assets import IPProtectionLevel
from ._common import AssetTypes, InputOutputModes, InputTypes, ModelType, Scope, TimeZone, WorkspaceKind
from ._component import ParallelTaskType
from ._deployment import BatchDeploymentOutputAction
from ._job import (
    DataGenerationTaskType,
    DataGenerationType,
    DistributionType,
    ImageClassificationModelNames,
    ImageInstanceSegmentationModelNames,
    ImageObjectDetectionModelNames,
    ImportSourceType,
    JobType,
    NlpLearningRateScheduler,
    NlpModels,
    TabularTrainingMode,
)
from ._monitoring import (
    MonitorDatasetContext,
    MonitorFeatureType,
    MonitorMetricName,
    MonitorModelType,
    MonitorSignalType,
    MonitorTargetTasks,
)
from ._registry import AcrAccountSku, StorageAccountType
from ._workspace import ManagedServiceIdentityType

TabularTrainingMode.__module__ = __name__

__all__ = [
    "DataGenerationTaskType",
    "DataGenerationType",
    "ImportSourceType",
    "JobType",
    "ParallelTaskType",
    "AssetTypes",
    "InputTypes",
    "InputOutputModes",
    "DistributionType",
    "TimeZone",
    "BatchDeploymentOutputAction",
    "ModelType",
    "ManagedServiceIdentityType",
    "ImageClassificationModelNames",
    "ImageObjectDetectionModelNames",
    "ImageInstanceSegmentationModelNames",
    "StorageAccountType",
    "AcrAccountSku",
    "NlpModels",
    "NlpLearningRateScheduler",
    "Scope",
    "TabularTrainingMode",
    "MonitorSignalType",
    "MonitorMetricName",
    "MonitorModelType",
    "MonitorFeatureType",
    "MonitorDatasetContext",
    "MonitorTargetTasks",
    "IPProtectionLevel",
    "ListViewType",
    "WorkspaceKind",
]
