# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from azure.ai.ml._restclient.v2021_10_01.models import CreatedByType
from azure.ai.ml._restclient.v2022_10_01_preview.models import UsageUnit

from ._assets._artifacts.data import Data
from ._assets._artifacts.model import Model
from ._assets.asset import Asset
from ._assets.environment import BuildContext, Environment
from ._builders import Command, Parallel, Pipeline, Spark, Sweep
from ._component.command_component import CommandComponent
from ._component.component import Component
from ._component.parallel_component import ParallelComponent
from ._component.pipeline_component import PipelineComponent
from ._component.spark_component import SparkComponent
from ._compute._aml_compute_node_info import AmlComputeNodeInfo
from ._compute._schedule import ComputePowerAction, ComputeSchedules, ComputeStartStopSchedule, ScheduleState
from ._compute._usage import Usage, UsageName
from ._compute._vm_size import VmSize
from ._compute.aml_compute import AmlCompute, AmlComputeSshSettings
from ._compute.compute import Compute, NetworkSettings
from ._compute.compute_instance import AssignedUserConfiguration, ComputeInstance, ComputeInstanceSshSettings
from ._compute.kubernetes_compute import KubernetesCompute
from ._compute.synapsespark_compute import AutoPauseSettings, AutoScaleSettings, SynapseSparkCompute
from ._compute.unsupported_compute import UnsupportedCompute
from ._compute.virtual_machine_compute import VirtualMachineCompute, VirtualMachineSshSettings
from ._compute._image_metadata import ImageMetadata
from ._datastore.adls_gen1 import AzureDataLakeGen1Datastore
from ._datastore.azure_storage import AzureBlobDatastore, AzureDataLakeGen2Datastore, AzureFileDatastore
from ._datastore.datastore import Datastore
from ._deployment.batch_deployment import BatchDeployment
from ._deployment.code_configuration import CodeConfiguration
from ._deployment.container_resource_settings import ResourceSettings
from ._deployment.deployment_settings import BatchRetrySettings, OnlineRequestSettings, ProbeSettings
from ._deployment.online_deployment import KubernetesOnlineDeployment, ManagedOnlineDeployment, OnlineDeployment
from ._deployment.resource_requirements_settings import ResourceRequirementsSettings
from ._deployment.scale_settings import DefaultScaleSettings, TargetUtilizationScaleSettings
from ._deployment.batch_job import BatchJob
from ._endpoint.batch_endpoint import BatchEndpoint
from ._endpoint.endpoint import Endpoint
from ._endpoint.online_endpoint import KubernetesOnlineEndpoint, ManagedOnlineEndpoint, OnlineEndpoint,\
    EndpointAuthKeys, EndpointAuthToken
from ._job.command_job import CommandJob
from ._job.compute_configuration import ComputeConfiguration
from ._job.input_port import InputPort
from ._job.job import Job
from ._job.job_limits import CommandJobLimits
from ._job.job_resource_configuration import JobResourceConfiguration
from ._job.job_service import JobService
from ._job.parallel.parallel_task import ParallelTask
from ._job.parallel.retry_settings import RetrySettings
from ._job.parameterized_command import ParameterizedCommand

# Pipeline related entities goes behind component since it depends on component
from ._job.pipeline.pipeline_job import PipelineJob, PipelineJobSettings
from ._job.resource_configuration import ResourceConfiguration
from ._job.service_instance import ServiceInstance
from ._job.spark_job import SparkJob
from ._job.spark_job_entry import SparkJobEntry, SparkJobEntryType
from ._job.spark_resource_configuration import SparkResourceConfiguration
from ._job.sweep.search_space import (
    Choice,
    LogNormal,
    LogUniform,
    Normal,
    QLogNormal,
    QLogUniform,
    QNormal,
    QUniform,
    Randint,
    Uniform,
)
from ._registry.registry import Registry
from ._registry.registry_support_classes import (
    RegistryRegionDetails,
    SystemCreatedAcrAccount,
    SystemCreatedStorageAccount,
)
from ._resource import Resource
from ._schedule.schedule import JobSchedule
from ._schedule.trigger import CronTrigger, RecurrencePattern, RecurrenceTrigger
from ._system_data import SystemData
from ._validation import ValidationResult
from ._workspace.connections.workspace_connection import WorkspaceConnection
from ._workspace.customer_managed_key import CustomerManagedKey
from ._workspace.diagnose import (
    DiagnoseRequestProperties,
    DiagnoseResponseResult,
    DiagnoseResponseResultValue,
    DiagnoseResult,
    DiagnoseWorkspaceParameters,
)
from ._workspace.private_endpoint import EndpointConnection, PrivateEndpoint
from ._workspace.workspace import Workspace
from ._workspace.workspace_keys import WorkspaceKeys, NotebookAccessKeys, ContainerRegistryCredential
from ._credentials import (
    PatTokenConfiguration, SasTokenConfiguration, ManagedIdentityConfiguration,
    AccountKeyConfiguration, UsernamePasswordConfiguration, ServicePrincipalConfiguration,
    CertificateConfiguration, UserIdentityConfiguration, AmlTokenConfiguration, IdentityConfiguration
)

# TODO: enable in PuP
# from ._job.import_job import ImportJob
# from ._component.import_component import ImportComponent

__all__ = [
    # "ImportJob",
    # "ImportComponent",
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
    "JobService",
    "SparkResourceConfiguration",
    "ParameterizedCommand",
    "InputPort",
    "BatchEndpoint",
    "OnlineEndpoint",
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
    "Workspace",
    "WorkspaceKeys",
    "WorkspaceConnection",
    "DiagnoseRequestProperties",
    "DiagnoseResult",
    "DiagnoseResponseResult",
    "DiagnoseResponseResultValue",
    "DiagnoseWorkspaceParameters",
    "PrivateEndpoint",
    "EndpointConnection",
    "CustomerManagedKey",
    "Datastore",
    "AzureDataLakeGen1Datastore",
    "AzureBlobDatastore",
    "AzureDataLakeGen2Datastore",
    "AzureFileDatastore",
    "Compute",
    "VirtualMachineCompute",
    "AmlCompute",
    "ComputeInstance",
    "UnsupportedCompute",
    "KubernetesCompute",
    "NetworkSettings",
    "Component",
    "PipelineJobSettings",
    "ParallelComponent",
    "CommandComponent",
    "SparkComponent",
    "Choice",
    "Normal",
    "LogNormal",
    "QNormal",
    "QLogNormal",
    "Randint",
    "Uniform",
    "QUniform",
    "LogUniform",
    "QLogUniform",
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
    "ComputePowerAction",
    "ComputeSchedules",
    "ComputeStartStopSchedule",
    "ScheduleState",
    "PipelineComponent",
    "VirtualMachineSshSettings",
    "AmlComputeSshSettings",
    "AmlComputeNodeInfo",
    "ImageMetadata",
    "SystemCreatedAcrAccount",
    "SystemCreatedStorageAccount",
    "ValidationResult",
    "RegistryRegionDetails",
    "Registry",
    "SynapseSparkCompute",
    "AutoScaleSettings",
    "AutoPauseSettings",
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
    "EndpointAuthToken"
]
