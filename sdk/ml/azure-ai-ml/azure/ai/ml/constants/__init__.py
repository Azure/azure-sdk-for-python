# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This package defines constants used in Azure Machine Learning SDKv2."""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._common import AssetTypes, InputOutputModes, ModelType, Scope, TimeZone
from ._component import ParallelTaskType
from ._deployment import BatchDeploymentOutputAction
from ._job import (
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
from ._registry import AcrAccountSku, StorageAccountType
from ._workspace import ManagedServiceIdentityType
from ._monitoring import (
    MonitorSignalType,
    MonitorMetricName,
    MonitorModelType,
    MonitorFeatureType,
    MonitorDatasetContext,
)

TabularTrainingMode.__module__ = __name__

__all__ = [
    "ImportSourceType",
    "JobType",
    "ParallelTaskType",
    "AssetTypes",
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
]
