# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from azure.ai.ml._restclient.v2022_02_01_preview.models import ScheduleStatus

from ._assets._artifacts.data import Data
from ._assets._artifacts.model import Model
from ._assets.asset import Asset
from ._assets.environment import BuildContext, Environment
from ._component.command_component import CommandComponent
from ._component.component import Component
from ._component.parallel_component import ParallelComponent
from ._compute._aml_compute_node_info import AmlComputeNodeInfo
from ._compute._identity import IdentityConfiguration
from ._compute._schedule import (
    ComputePowerAction,
    ComputeSchedules,
    ComputeStartStopSchedule,
    ScheduleState,
)
from ._compute._usage import Usage, UsageName
from ._compute._user_assigned_identity import UserAssignedIdentity
from ._compute._vm_size import VmSize
from ._compute.aml_compute import AmlCompute, AmlComputeSshSettings
from ._compute.compute import Compute, NetworkSettings
from ._compute.compute_instance import AssignedUserConfiguration, ComputeInstance, ComputeInstanceSshSettings
from ._compute.kubernetes_compute import KubernetesCompute
from ._compute.unsupported_compute import UnsupportedCompute
from ._compute.virtual_machine_compute import VirtualMachineCompute, VirtualMachineSshSettings
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
from ._endpoint.batch_endpoint import BatchEndpoint
from ._endpoint.endpoint import Endpoint
from ._endpoint.online_endpoint import KubernetesOnlineEndpoint, ManagedOnlineEndpoint, OnlineEndpoint
from ._job.base_job import _BaseJob
from ._job.command_job import CommandJob
from ._job.compute_configuration import ComputeConfiguration
from ._job.input_port import InputPort
from ._job.job import Job
from ._job.job_limits import CommandJobLimits
from ._job.parallel.parallel_task import ParallelTask
from ._job.parallel.retry_settings import RetrySettings
from ._job.parameterized_command import ParameterizedCommand

# Pipeline related entities goes behind component since it depends on component
from ._job.pipeline.pipeline_job import PipelineJob, PipelineJobSettings
from ._job.resource_configuration import ResourceConfiguration
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
from ._resource import Resource
from ._schedule.schedule import JobSchedule
from ._schedule.trigger import RecurrencePattern, CronTrigger, RecurrenceTrigger
from ._workspace.connections.workspace_connection import WorkspaceConnection
from ._workspace.customer_managed_key import CustomerManagedKey
from ._workspace.private_endpoint import EndpointConnection, PrivateEndpoint
from ._workspace.workspace import Workspace

__all__ = [
    "Resource",
    "Job",
    "CommandJob",
    "PipelineJob",
    "CommandJobLimits",
    "ComputeConfiguration",
    "ResourceConfiguration",
    "ParameterizedCommand",
    "InputPort",
    "BatchEndpoint",
    "OnlineEndpoint",
    "BatchDeployment",
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
    "WorkspaceConnection",
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
    "IdentityConfiguration",
    "NetworkSettings",
    "Component",
    "PipelineJobSettings",
    "ParallelComponent",
    "CommandComponent",
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
    "UserAssignedIdentity",
    "VmSize",
    "Usage",
    "UsageName",
    "CronTrigger",
    "RecurrenceTrigger",
    "RecurrencePattern",
    "JobSchedule",
    "ComputePowerAction",
    "ComputeSchedules",
    "ComputeStartStopSchedule",
    "ScheduleState",
    "VirtualMachineSshSettings",
    "AmlComputeSshSettings",
    "AmlComputeNodeInfo",
]
