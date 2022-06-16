# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from ._resource import Resource
from ._assets._artifacts.model import Model
from ._assets.asset import Asset
from ._assets.environment import Environment, BuildContext
from ._assets._artifacts.data import Data
from ._job.job import Job
from ._job.input_port import InputPort
from ._job.command_job import CommandJob
from ._job.parallel.parallel_job import ParallelJob
from ._job.base_job import _BaseJob
from ._job.sweep.search_space import (
    Choice,
    Normal,
    LogNormal,
    QNormal,
    QLogNormal,
    Uniform,
    LogUniform,
    QUniform,
    Randint,
    QLogUniform,
)
from ._job.compute_configuration import ComputeConfiguration
from ._job.resource_configuration import ResourceConfiguration
from ._job.parameterized_command import ParameterizedCommand
from ._job.parallel.parameterized_parallel import ParameterizedParallel
from ._job.job_limits import CommandJobLimits
from ._workspace.workspace import Workspace
from ._workspace.private_endpoint import PrivateEndpoint, EndpointConnection
from ._workspace.customer_managed_key import CustomerManagedKey
from ._workspace.connections.workspace_connection import WorkspaceConnection

from ._endpoint.batch_endpoint import BatchEndpoint
from ._deployment.batch_deployment import BatchDeployment
from ._deployment.code_configuration import CodeConfiguration
from ._endpoint.endpoint import Endpoint
from ._endpoint.online_endpoint import (
    OnlineEndpoint,
    KubernetesOnlineEndpoint,
    ManagedOnlineEndpoint,
)
from ._deployment.online_deployment import (
    OnlineDeployment,
    KubernetesOnlineDeployment,
    ManagedOnlineDeployment,
)
from ._deployment.deployment_settings import (
    OnlineRequestSettings,
    ProbeSettings,
    BatchRetrySettings,
)
from ._job.parallel.parallel_task import ParallelTask
from ._job.parallel.retry_settings import RetrySettings
from ._deployment.scale_settings import (
    DefaultScaleSettings,
    TargetUtilizationScaleSettings,
)
from ._deployment.resource_requirements_settings import ResourceRequirementsSettings
from ._deployment.container_resource_settings import ResourceSettings

from ._datastore.datastore import Datastore
from ._datastore.adls_gen1 import AzureDataLakeGen1Datastore
from ._datastore.azure_storage import (
    AzureBlobDatastore,
    AzureFileDatastore,
    AzureDataLakeGen2Datastore,
)

from ._compute.compute import Compute
from ._compute.virtual_machine_compute import (
    VirtualMachineCompute,
    VirtualMachineSshSettings,
)
from ._compute.aml_compute import AmlCompute, AmlComputeSshSettings
from ._compute.compute import NetworkSettings
from ._compute.compute_instance import (
    ComputeInstance,
    AssignedUserConfiguration,
    ComputeInstanceSshSettings,
)
from ._compute.unsupported_compute import UnsupportedCompute
from ._compute.kubernetes_compute import KubernetesCompute
from ._compute._identity import IdentityConfiguration
from ._compute._user_assigned_identity import UserAssignedIdentity

from ._compute._vm_size import VmSize
from ._compute._aml_compute_node_info import AmlComputeNodeInfo
from ._compute._usage import Usage, UsageName
from ._compute._schedule import (
    CronTrigger,
    RecurrenceTrigger,
    ComputePowerAction,
    ComputeSchedules,
    ComputeStartStopSchedule,
    ScheduleState,
)


from ._component.component import Component
from ._component.command_component import CommandComponent
from ._component.parallel_component import ParallelComponent


# Pipeline related entities goes behind component since it depends on component
from ._job.pipeline.pipeline_job import PipelineJob, PipelineJobSettings


from ._schedule.schedule import CronSchedule, RecurrenceSchedule, RecurrencePattern

from azure.ai.ml._restclient.v2022_02_01_preview.models import ScheduleStatus


__all__ = [
    "Resource",
    "Job",
    "CommandJob",
    "PipelineJob",
    "ParallelJob",
    "CommandJobLimits",
    "ComputeConfiguration",
    "ResourceConfiguration",
    "ParameterizedCommand",
    "ParameterizedParallel",
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
    "CommandComponent",
    "ParallelComponent",
    "_BaseJob",
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
    "ComputePowerAction",
    "ComputeSchedules",
    "ComputeStartStopSchedule",
    "ScheduleState",
    "VirtualMachineSshSettings",
    "AmlComputeSshSettings",
    "AmlComputeNodeInfo",
    "CronSchedule",
    "RecurrenceSchedule",
    "RecurrencePattern",
    "ScheduleStatus",
]
