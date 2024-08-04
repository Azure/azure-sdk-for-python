# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains entities and SDK objects for Azure Machine Learning SDKv2.

Main areas include managing compute targets, creating/managing workspaces and jobs, and submitting/accessing model, runs
and run output/logging etc.
"""
# pylint: disable=naming-mismatch
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import logging
from typing import Any, Optional

from azure.ai.ml._restclient.v2022_10_01.models import CreatedByType
from azure.ai.ml._restclient.v2022_10_01_preview.models import UsageUnit

from ._assets._artifacts._package.base_environment_source import BaseEnvironment
from ._assets._artifacts._package.inferencing_server import (
    AzureMLBatchInferencingServer,
    AzureMLOnlineInferencingServer,
    CustomInferencingServer,
    Route,
    TritonInferencingServer,
)
from ._assets._artifacts._package.model_configuration import ModelConfiguration
from ._assets._artifacts._package.model_package import (
    ModelPackage,
    ModelPackageInput,
    PackageInputPathId,
    PackageInputPathUrl,
    PackageInputPathVersion,
)
from ._assets._artifacts.data import Data
from ._assets._artifacts.feature_set import FeatureSet
from ._assets._artifacts.index import Index
from ._assets._artifacts.model import Model
from ._assets.asset import Asset
from ._assets.environment import BuildContext, Environment
from ._assets.intellectual_property import IntellectualProperty
from ._assets.workspace_asset_reference import (
    WorkspaceAssetReference as WorkspaceModelReference,
)
from ._autogen_entities.models import (
    AzureOpenAIDeployment,
    MarketplaceSubscription,
    ServerlessEndpoint,
    MarketplacePlan,
)
from ._builders import Command, Parallel, Pipeline, Spark, Sweep
from ._component.command_component import CommandComponent
from ._component.component import Component
from ._component.parallel_component import ParallelComponent
from ._component.pipeline_component import PipelineComponent
from ._component.spark_component import SparkComponent
from ._compute._aml_compute_node_info import AmlComputeNodeInfo
from ._compute._custom_applications import (
    CustomApplications,
    EndpointsSettings,
    ImageSettings,
    VolumeSettings,
)
from ._compute._image_metadata import ImageMetadata
from ._compute._schedule import (
    ComputePowerAction,
    ComputeSchedules,
    ComputeStartStopSchedule,
    ScheduleState,
)
from ._compute._setup_scripts import ScriptReference, SetupScripts
from ._compute._usage import Usage, UsageName
from ._compute._vm_size import VmSize
from ._compute.aml_compute import AmlCompute, AmlComputeSshSettings
from ._compute.compute import Compute, NetworkSettings
from ._compute.compute_instance import (
    AssignedUserConfiguration,
    ComputeInstance,
    ComputeInstanceSshSettings,
)
from ._compute.kubernetes_compute import KubernetesCompute
from ._compute.synapsespark_compute import (
    AutoPauseSettings,
    AutoScaleSettings,
    SynapseSparkCompute,
)
from ._compute.unsupported_compute import UnsupportedCompute
from ._compute.virtual_machine_compute import (
    VirtualMachineCompute,
    VirtualMachineSshSettings,
)
from ._credentials import (
    AccessKeyConfiguration,
    AccountKeyConfiguration,
    AmlTokenConfiguration,
    ApiKeyConfiguration,
    CertificateConfiguration,
    IdentityConfiguration,
    ManagedIdentityConfiguration,
    NoneCredentialConfiguration,
    AadCredentialConfiguration,
    PatTokenConfiguration,
    SasTokenConfiguration,
    ServicePrincipalConfiguration,
    UserIdentityConfiguration,
    UsernamePasswordConfiguration,
)
from ._data_import.data_import import DataImport
from ._data_import.schedule import ImportDataSchedule
from ._datastore.adls_gen1 import AzureDataLakeGen1Datastore
from ._datastore.azure_storage import (
    AzureBlobDatastore,
    AzureDataLakeGen2Datastore,
    AzureFileDatastore,
)
from ._datastore.datastore import Datastore
from ._datastore.one_lake import OneLakeArtifact, OneLakeDatastore
from ._deployment.batch_deployment import BatchDeployment
from ._deployment.batch_job import BatchJob
from ._deployment.code_configuration import CodeConfiguration
from ._deployment.container_resource_settings import ResourceSettings
from ._deployment.data_asset import DataAsset
from ._deployment.data_collector import DataCollector
from ._deployment.deployment_collection import DeploymentCollection
from ._deployment.deployment_settings import (
    BatchRetrySettings,
    OnlineRequestSettings,
    ProbeSettings,
)
from ._deployment.model_batch_deployment import ModelBatchDeployment
from ._deployment.model_batch_deployment_settings import ModelBatchDeploymentSettings
from ._deployment.online_deployment import (
    Deployment,
    KubernetesOnlineDeployment,
    ManagedOnlineDeployment,
    OnlineDeployment,
)
from ._deployment.pipeline_component_batch_deployment import (
    PipelineComponentBatchDeployment,
)
from ._deployment.request_logging import RequestLogging
from ._deployment.resource_requirements_settings import ResourceRequirementsSettings
from ._deployment.scale_settings import (
    DefaultScaleSettings,
    OnlineScaleSettings,
    TargetUtilizationScaleSettings,
)
from ._endpoint.batch_endpoint import BatchEndpoint
from ._endpoint.endpoint import Endpoint
from ._endpoint.online_endpoint import (
    EndpointAuthKeys,
    EndpointAuthToken,
    EndpointAadToken,
    KubernetesOnlineEndpoint,
    ManagedOnlineEndpoint,
    OnlineEndpoint,
)
from ._feature_set.data_availability_status import DataAvailabilityStatus
from ._feature_set.feature import Feature
from ._feature_set.feature_set_backfill_metadata import FeatureSetBackfillMetadata
from ._feature_set.feature_set_backfill_request import FeatureSetBackfillRequest
from ._feature_set.feature_set_materialization_metadata import (
    FeatureSetMaterializationMetadata,
)
from ._feature_set.feature_set_specification import FeatureSetSpecification
from ._feature_set.feature_window import FeatureWindow
from ._feature_set.materialization_compute_resource import (
    MaterializationComputeResource,
)
from ._feature_set.materialization_settings import MaterializationSettings
from ._feature_set.materialization_type import MaterializationType
from ._feature_store.feature_store import FeatureStore
from ._feature_store.materialization_store import MaterializationStore
from ._feature_store_entity.data_column import DataColumn
from ._feature_store_entity.data_column_type import DataColumnType
from ._feature_store_entity.feature_store_entity import FeatureStoreEntity
from ._indexes import (
    AzureAISearchConfig,
    IndexDataSource,
    GitSource,
    LocalSource,
)
from ._indexes import ModelConfiguration as IndexModelConfiguration
from ._job.command_job import CommandJob
from ._job.compute_configuration import ComputeConfiguration
from ._job.input_port import InputPort
from ._job.job import Job
from ._job.job_limits import CommandJobLimits
from ._job.job_resource_configuration import JobResourceConfiguration
from ._job.job_service import (
    JobService,
    JupyterLabJobService,
    SshJobService,
    TensorBoardJobService,
    VsCodeJobService,
)
from ._job.parallel.parallel_task import ParallelTask
from ._job.parallel.retry_settings import RetrySettings
from ._job.parameterized_command import ParameterizedCommand

# Pipeline related entities goes behind component since it depends on component
from ._job.pipeline.pipeline_job import PipelineJob, PipelineJobSettings
from ._job.queue_settings import QueueSettings
from ._job.resource_configuration import ResourceConfiguration
from ._job.service_instance import ServiceInstance
from ._job.spark_job import SparkJob
from ._job.spark_job_entry import SparkJobEntry, SparkJobEntryType
from ._job.spark_resource_configuration import SparkResourceConfiguration
from ._monitoring.alert_notification import AlertNotification
from ._monitoring.compute import ServerlessSparkCompute
from ._monitoring.definition import MonitorDefinition
from ._monitoring.input_data import (
    FixedInputData,
    MonitorInputData,
    StaticInputData,
    TrailingInputData,
)
from ._monitoring.schedule import MonitorSchedule
from ._monitoring.signals import (
    BaselineDataRange,
    CustomMonitoringSignal,
    DataDriftSignal,
    DataQualitySignal,
    DataSegment,
    FADProductionData,
    FeatureAttributionDriftSignal,
    GenerationSafetyQualitySignal,
    GenerationTokenStatisticsSignal,
    LlmData,
    ModelPerformanceSignal,
    MonitorFeatureFilter,
    PredictionDriftSignal,
    ProductionData,
    ReferenceData,
)
from ._monitoring.target import MonitoringTarget
from ._monitoring.thresholds import (
    CategoricalDriftMetrics,
    CustomMonitoringMetricThreshold,
    DataDriftMetricThreshold,
    DataQualityMetricsCategorical,
    DataQualityMetricsNumerical,
    DataQualityMetricThreshold,
    FeatureAttributionDriftMetricThreshold,
    GenerationSafetyQualityMonitoringMetricThreshold,
    GenerationTokenStatisticsMonitorMetricThreshold,
    ModelPerformanceClassificationThresholds,
    ModelPerformanceMetricThreshold,
    ModelPerformanceRegressionThresholds,
    NumericalDriftMetrics,
    PredictionDriftMetricThreshold,
)
from ._notification.notification import Notification
from ._registry.registry import Registry
from ._registry.registry_support_classes import (
    RegistryRegionDetails,
    SystemCreatedAcrAccount,
    SystemCreatedStorageAccount,
)
from ._resource import Resource
from ._schedule.schedule import JobSchedule, Schedule, ScheduleTriggerResult
from ._schedule.trigger import CronTrigger, RecurrencePattern, RecurrenceTrigger
from ._system_data import SystemData
from ._validation import ValidationResult
from ._workspace.compute_runtime import ComputeRuntime
from ._workspace.connections.workspace_connection import WorkspaceConnection
from ._workspace.connections.connection_subtypes import (
    AzureBlobStoreConnection,
    MicrosoftOneLakeConnection,
    AzureOpenAIConnection,
    AzureAIServicesConnection,
    AzureAISearchConnection,
    AzureContentSafetyConnection,
    AzureSpeechServicesConnection,
    APIKeyConnection,
    OpenAIConnection,
    SerpConnection,
    ServerlessConnection,
)
from ._workspace.connections.one_lake_artifacts import OneLakeConnectionArtifact
from ._workspace.customer_managed_key import CustomerManagedKey
from ._workspace.diagnose import (
    DiagnoseRequestProperties,
    DiagnoseResponseResult,
    DiagnoseResponseResultValue,
    DiagnoseResult,
    DiagnoseWorkspaceParameters,
)
from ._workspace.feature_store_settings import FeatureStoreSettings
from ._workspace.networking import (
    FqdnDestination,
    IsolationMode,
    ManagedNetwork,
    ManagedNetworkProvisionStatus,
    OutboundRule,
    PrivateEndpointDestination,
    ServiceTagDestination,
)
from ._workspace.private_endpoint import EndpointConnection, PrivateEndpoint
from ._workspace.serverless_compute import ServerlessComputeSettings
from ._workspace.workspace import Workspace
from ._workspace._ai_workspaces.hub import Hub
from ._workspace._ai_workspaces.project import Project
from ._workspace.workspace_keys import (
    ContainerRegistryCredential,
    NotebookAccessKeys,
    WorkspaceKeys,
)

__all__ = [
    "Resource",
    "Job",
    "CommandJob",
    "PipelineJob",
    "ServiceInstance",
    "SystemData",
    "SparkJob",
    "SparkJobEntry",
    "SparkJobEntryType",
    "CommandJobLimits",
    "ComputeConfiguration",
    "CreatedByType",
    "ResourceConfiguration",
    "JobResourceConfiguration",
    "QueueSettings",
    "JobService",
    "SshJobService",
    "TensorBoardJobService",
    "VsCodeJobService",
    "JupyterLabJobService",
    "SparkResourceConfiguration",
    "ParameterizedCommand",
    "InputPort",
    "BatchEndpoint",
    "OnlineEndpoint",
    "Deployment",
    "BatchDeployment",
    "BatchJob",
    "CodeConfiguration",
    "Endpoint",
    "OnlineDeployment",
    "Data",
    "KubernetesOnlineEndpoint",
    "ManagedOnlineEndpoint",
    "KubernetesOnlineDeployment",
    "ManagedOnlineDeployment",
    "OnlineRequestSettings",
    "OnlineScaleSettings",
    "ProbeSettings",
    "BatchRetrySettings",
    "RetrySettings",
    "ParallelTask",
    "DefaultScaleSettings",
    "TargetUtilizationScaleSettings",
    "Asset",
    "Environment",
    "BuildContext",
    "Model",
    "ModelBatchDeployment",
    "ModelBatchDeploymentSettings",
    "Workspace",
    "WorkspaceKeys",
    "WorkspaceConnection",
    "AzureBlobStoreConnection",
    "MicrosoftOneLakeConnection",
    "AzureOpenAIConnection",
    "AzureAIServicesConnection",
    "AzureAISearchConnection",
    "AzureContentSafetyConnection",
    "AzureSpeechServicesConnection",
    "APIKeyConnection",
    "OpenAIConnection",
    "SerpConnection",
    "ServerlessConnection",
    "DiagnoseRequestProperties",
    "DiagnoseResult",
    "DiagnoseResponseResult",
    "DiagnoseResponseResultValue",
    "DiagnoseWorkspaceParameters",
    "PrivateEndpoint",
    "OutboundRule",
    "ManagedNetwork",
    "FqdnDestination",
    "ServiceTagDestination",
    "PrivateEndpointDestination",
    "IsolationMode",
    "ManagedNetworkProvisionStatus",
    "EndpointConnection",
    "CustomerManagedKey",
    "DataImport",
    "Datastore",
    "AzureDataLakeGen1Datastore",
    "AzureBlobDatastore",
    "AzureDataLakeGen2Datastore",
    "AzureFileDatastore",
    "OneLakeDatastore",
    "OneLakeArtifact",
    "OneLakeConnectionArtifact",
    "Compute",
    "VirtualMachineCompute",
    "AmlCompute",
    "ComputeInstance",
    "UnsupportedCompute",
    "KubernetesCompute",
    "NetworkSettings",
    "Component",
    "PipelineJobSettings",
    "PipelineComponentBatchDeployment",
    "ParallelComponent",
    "CommandComponent",
    "SparkComponent",
    "ResourceRequirementsSettings",
    "ResourceSettings",
    "AssignedUserConfiguration",
    "ComputeInstanceSshSettings",
    "VmSize",
    "Usage",
    "UsageName",
    "UsageUnit",
    "CronTrigger",
    "RecurrenceTrigger",
    "RecurrencePattern",
    "JobSchedule",
    "ImportDataSchedule",
    "Schedule",
    "ScheduleTriggerResult",
    "ComputePowerAction",
    "ComputeSchedules",
    "ComputeStartStopSchedule",
    "ScheduleState",
    "PipelineComponent",
    "VirtualMachineSshSettings",
    "AmlComputeSshSettings",
    "AmlComputeNodeInfo",
    "ImageMetadata",
    "CustomApplications",
    "ImageSettings",
    "EndpointsSettings",
    "VolumeSettings",
    "SetupScripts",
    "ScriptReference",
    "SystemCreatedAcrAccount",
    "SystemCreatedStorageAccount",
    "ValidationResult",
    "RegistryRegionDetails",
    "Registry",
    "SynapseSparkCompute",
    "AutoScaleSettings",
    "AutoPauseSettings",
    "WorkspaceModelReference",
    "Hub",
    "Project",
    "Feature",
    "FeatureSet",
    "FeatureSetBackfillRequest",
    "ComputeRuntime",
    "FeatureStoreSettings",
    "FeatureStoreEntity",
    "DataColumn",
    "DataColumnType",
    "FeatureSetSpecification",
    "MaterializationComputeResource",
    "FeatureWindow",
    "MaterializationSettings",
    "MaterializationType",
    "FeatureStore",
    "MaterializationStore",
    "Notification",
    "FeatureSetBackfillMetadata",
    "DataAvailabilityStatus",
    "FeatureSetMaterializationMetadata",
    "ServerlessComputeSettings",
    # builders
    "Command",
    "Parallel",
    "Sweep",
    "Spark",
    "Pipeline",
    "PatTokenConfiguration",
    "SasTokenConfiguration",
    "ManagedIdentityConfiguration",
    "AccountKeyConfiguration",
    "ServicePrincipalConfiguration",
    "CertificateConfiguration",
    "UsernamePasswordConfiguration",
    "UserIdentityConfiguration",
    "AmlTokenConfiguration",
    "IdentityConfiguration",
    "NotebookAccessKeys",
    "ContainerRegistryCredential",
    "EndpointAuthKeys",
    "EndpointAuthToken",
    "EndpointAadToken",
    "ModelPackage",
    "ModelPackageInput",
    "AzureMLOnlineInferencingServer",
    "AzureMLBatchInferencingServer",
    "TritonInferencingServer",
    "CustomInferencingServer",
    "ModelConfiguration",
    "BaseEnvironment",
    "PackageInputPathId",
    "PackageInputPathUrl",
    "PackageInputPathVersion",
    "Route",
    "AccessKeyConfiguration",
    "AlertNotification",
    "ServerlessSparkCompute",
    "ApiKeyConfiguration",
    "MonitorDefinition",
    "MonitorInputData",
    "MonitorSchedule",
    "DataDriftSignal",
    "DataQualitySignal",
    "PredictionDriftSignal",
    "FeatureAttributionDriftSignal",
    "CustomMonitoringSignal",
    "GenerationSafetyQualitySignal",
    "GenerationTokenStatisticsSignal",
    "ModelPerformanceSignal",
    "MonitorFeatureFilter",
    "DataSegment",
    "FADProductionData",
    "LlmData",
    "ProductionData",
    "ReferenceData",
    "BaselineDataRange",
    "MonitoringTarget",
    "FixedInputData",
    "StaticInputData",
    "TrailingInputData",
    "DataDriftMetricThreshold",
    "DataQualityMetricThreshold",
    "PredictionDriftMetricThreshold",
    "FeatureAttributionDriftMetricThreshold",
    "CustomMonitoringMetricThreshold",
    "GenerationSafetyQualityMonitoringMetricThreshold",
    "GenerationTokenStatisticsMonitorMetricThreshold",
    "CategoricalDriftMetrics",
    "NumericalDriftMetrics",
    "DataQualityMetricsNumerical",
    "DataQualityMetricsCategorical",
    "ModelPerformanceMetricThreshold",
    "ModelPerformanceClassificationThresholds",
    "ModelPerformanceRegressionThresholds",
    "DataCollector",
    "IntellectualProperty",
    "DataAsset",
    "DeploymentCollection",
    "RequestLogging",
    "NoneCredentialConfiguration",
    "MarketplacePlan",
    "MarketplaceSubscription",
    "ServerlessEndpoint",
    "AccountKeyConfiguration",
    "AadCredentialConfiguration",
    "Index",
    "AzureOpenAIDeployment",
    "AzureAISearchConfig",
    "IndexDataSource",
    "GitSource",
    "LocalSource",
    "IndexModelConfiguration",
]

# Allow importing these types for backwards compatibility


def __getattr__(name: str):
    requested: Optional[Any] = None

    if name == "Choice":
        from ..sweep import Choice

        requested = Choice
    if name == "LogNormal":
        from ..sweep import LogNormal

        requested = LogNormal
    if name == "LogUniform":
        from ..sweep import LogUniform

        requested = LogUniform
    if name == "Normal":
        from ..sweep import Normal

        requested = Normal
    if name == "QLogNormal":
        from ..sweep import QLogNormal

        requested = QLogNormal
    if name == "QLogUniform":
        from ..sweep import QLogUniform

        requested = QLogUniform
    if name == "QNormal":
        from ..sweep import QNormal

        requested = QNormal
    if name == "QUniform":
        from ..sweep import QUniform

        requested = QUniform
    if name == "Randint":
        from ..sweep import Randint

        requested = Randint
    if name == "Uniform":
        from ..sweep import Uniform

        requested = Uniform

    if requested:
        if not getattr(__getattr__, "warning_issued", False):
            logging.warning(
                " %s will be removed from the azure.ai.ml.entities namespace in a future release."
                " Please import from the azure.ai.ml.sweep namespace instead.",
                name,
            )
            __getattr__.warning_issued = True  # type: ignore[attr-defined]
        return requested

    raise AttributeError(f"module 'azure.ai.ml.entities' has no attribute {name}")
