# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access,too-many-lines
import copy
import logging
import os
from enum import Enum
from os import PathLike
from typing import Any, Dict, List, Optional, Tuple, Union, cast, overload

from marshmallow import INCLUDE, Schema

from azure.ai.ml._restclient.v2023_04_01_preview.models import CommandJob as RestCommandJob
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobBase
from azure.ai.ml._schema.core.fields import ExperimentalField, NestedField, UnionField
from azure.ai.ml._schema.job.command_job import CommandJobSchema
from azure.ai.ml._schema.job.identity import AMLTokenIdentitySchema, ManagedIdentitySchema, UserIdentitySchema
from azure.ai.ml._schema.job.services import JobServiceSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, LOCAL_COMPUTE_PROPERTY, LOCAL_COMPUTE_TARGET
from azure.ai.ml.constants._component import ComponentSource, NodeType
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._credentials import (
    AmlTokenConfiguration,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
    _BaseJobIdentityConfiguration,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, from_rest_inputs_to_dataset_literal
from azure.ai.ml.entities._job.command_job import CommandJob
from azure.ai.ml.entities._job.distribution import (
    DistributionConfiguration,
    MpiDistribution,
    PyTorchDistribution,
    RayDistribution,
    TensorFlowDistribution,
)
from azure.ai.ml.entities._job.job_limits import CommandJobLimits
from azure.ai.ml.entities._job.job_resource_configuration import JobResourceConfiguration
from azure.ai.ml.entities._job.job_service import (
    JobService,
    JobServiceBase,
    JupyterLabJobService,
    SshJobService,
    TensorBoardJobService,
    VsCodeJobService,
)
from azure.ai.ml.entities._job.queue_settings import QueueSettings
from azure.ai.ml.entities._job.sweep.early_termination_policy import EarlyTerminationPolicy
from azure.ai.ml.entities._job.sweep.objective import Objective
from azure.ai.ml.entities._job.sweep.search_space import (
    Choice,
    LogNormal,
    LogUniform,
    Normal,
    QLogNormal,
    QLogUniform,
    QNormal,
    QUniform,
    Randint,
    SweepDistribution,
    Uniform,
)
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from ..._schema import PathAwareSchema
from ..._schema.job.distribution import (
    MPIDistributionSchema,
    PyTorchDistributionSchema,
    RayDistributionSchema,
    TensorFlowDistributionSchema,
)
from .._job.pipeline._io import NodeWithGroupInputMixin
from .._util import (
    convert_ordered_dict_to_dict,
    from_rest_dict_to_dummy_rest_object,
    get_rest_dict_for_node_attrs,
    load_from_dict,
    validate_attribute_type,
)
from .base_node import BaseNode
from .sweep import Sweep

module_logger = logging.getLogger(__name__)


class Command(BaseNode, NodeWithGroupInputMixin):
    """Base class for command node, used for command component version consumption.

    You should not instantiate this class directly. Instead, you should create it using the builder function: command().

    :keyword component: The ID or instance of the command component or job to be run for the step.
    :paramtype component: Union[str, ~azure.ai.ml.entities.CommandComponent]
    :keyword compute: The compute target the job will run on.
    :paramtype compute: Optional[str]
    :keyword inputs: A mapping of input names to input data sources used in the job.
    :paramtype inputs: Optional[dict[str, Union[
        ~azure.ai.ml.Input, str, bool, int, float, Enum]]]
    :keyword outputs: A mapping of output names to output data sources used in the job.
    :paramtype outputs: Optional[dict[str, Union[str, ~azure.ai.ml.Output]]]
    :keyword limits: The limits for the command component or job.
    :paramtype limits: ~azure.ai.ml.entities.CommandJobLimits
    :keyword identity: The identity that the command job will use while running on compute.
    :paramtype identity: Optional[Union[
        dict[str, str],
        ~azure.ai.ml.entities.ManagedIdentityConfiguration,
        ~azure.ai.ml.entities.AmlTokenConfiguration,
        ~azure.ai.ml.entities.UserIdentityConfiguration]]
    :keyword distribution: The configuration for distributed jobs.
    :paramtype distribution: Optional[Union[dict, ~azure.ai.ml.PyTorchDistribution, ~azure.ai.ml.MpiDistribution,
        ~azure.ai.ml.TensorFlowDistribution, ~azure.ai.ml.RayDistribution]]
    :keyword environment: The environment that the job will run in.
    :paramtype environment: Optional[Union[str, ~azure.ai.ml.entities.Environment]]
    :keyword environment_variables:  A dictionary of environment variable names and values.
        These environment variables are set on the process where the user script is being executed.
    :paramtype environment_variables: Optional[dict[str, str]]
    :keyword resources: The compute resource configuration for the command.
    :paramtype resources: Optional[~azure.ai.ml.entities.JobResourceConfiguration]
    :keyword services: The interactive services for the node. This is an experimental parameter, and may change at any
        time. Please see https://aka.ms/azuremlexperimental for more information.
    :paramtype services: Optional[dict[str, Union[~azure.ai.ml.entities.JobService,
        ~azure.ai.ml.entities.JupyterLabJobService,
        ~azure.ai.ml.entities.SshJobService, ~azure.ai.ml.entities.TensorBoardJobService,
        ~azure.ai.ml.entities.VsCodeJobService]]]
    :keyword queue_settings: Queue settings for the job.
    :paramtype queue_settings: Optional[~azure.ai.ml.entities.QueueSettings]
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Command cannot be successfully validated.
        Details will be provided in the error message.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        *,
        component: Union[str, CommandComponent],
        compute: Optional[str] = None,
        inputs: Optional[
            Dict[
                str,
                Union[
                    Input,
                    str,
                    bool,
                    int,
                    float,
                    Enum,
                ],
            ]
        ] = None,
        outputs: Optional[Dict[str, Union[str, Output]]] = None,
        limits: Optional[CommandJobLimits] = None,
        identity: Optional[
            Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
        distribution: Optional[
            Union[
                Dict,
                MpiDistribution,
                TensorFlowDistribution,
                PyTorchDistribution,
                RayDistribution,
                DistributionConfiguration,
            ]
        ] = None,
        environment: Optional[Union[Environment, str]] = None,
        environment_variables: Optional[Dict] = None,
        resources: Optional[JobResourceConfiguration] = None,
        services: Optional[
            Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]
        ] = None,
        queue_settings: Optional[QueueSettings] = None,
        **kwargs: Any,
    ) -> None:
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        # resolve normal dict to dict[str, JobService]
        services = _resolve_job_services(services)
        kwargs.pop("type", None)
        self._parameters: dict = kwargs.pop("parameters", {})
        BaseNode.__init__(
            self,
            type=NodeType.COMMAND,
            inputs=inputs,
            outputs=outputs,
            component=component,
            compute=compute,
            services=services,
            **kwargs,
        )

        # init mark for _AttrDict
        self._init = True
        # initialize command job properties
        self.limits = limits
        self.identity = identity
        self._distribution = distribution
        self.environment_variables = {} if environment_variables is None else environment_variables
        self.environment: Any = environment
        self._resources = resources
        self._services = services
        self.queue_settings = queue_settings

        if isinstance(self.component, CommandComponent):
            self.resources = self.resources or self.component.resources  # type: ignore[assignment]
            self.distribution = self.distribution or self.component.distribution

        self._swept: bool = False
        self._init = False

    @classmethod
    def _get_supported_inputs_types(cls) -> Tuple:
        supported_types = super()._get_supported_inputs_types() or ()
        return (
            SweepDistribution,
            *supported_types,
        )

    @classmethod
    def _get_supported_outputs_types(cls) -> Tuple:
        return str, Output

    @property
    def parameters(self) -> Dict[str, str]:
        """MLFlow parameters to be logged during the job.

        :return: The MLFlow parameters to be logged during the job.
        :rtype: dict[str, str]
        """
        return self._parameters

    @property
    def distribution(
        self,
    ) -> Optional[
        Union[
            Dict,
            MpiDistribution,
            TensorFlowDistribution,
            PyTorchDistribution,
            RayDistribution,
            DistributionConfiguration,
        ]
    ]:
        """The configuration for the distributed command component or job.

        :return: The configuration for distributed jobs.
        :rtype: Union[~azure.ai.ml.PyTorchDistribution, ~azure.ai.ml.MpiDistribution,
            ~azure.ai.ml.TensorFlowDistribution, ~azure.ai.ml.RayDistribution]
        """
        return self._distribution

    @distribution.setter
    def distribution(
        self,
        value: Union[Dict, PyTorchDistribution, TensorFlowDistribution, MpiDistribution, RayDistribution],
    ) -> None:
        """Sets the configuration for the distributed command component or job.

        :param value: The configuration for distributed jobs.
        :type value: Union[dict, ~azure.ai.ml.PyTorchDistribution, ~azure.ai.ml.MpiDistribution,
            ~azure.ai.ml.TensorFlowDistribution, ~azure.ai.ml.RayDistribution]
        """
        if isinstance(value, dict):
            dist_schema = UnionField(
                [
                    NestedField(PyTorchDistributionSchema, unknown=INCLUDE),
                    NestedField(TensorFlowDistributionSchema, unknown=INCLUDE),
                    NestedField(MPIDistributionSchema, unknown=INCLUDE),
                    ExperimentalField(NestedField(RayDistributionSchema, unknown=INCLUDE)),
                ]
            )
            value = dist_schema._deserialize(value=value, attr=None, data=None)
        self._distribution = value

    @property
    def resources(self) -> JobResourceConfiguration:
        """The compute resource configuration for the command component or job.

        :rtype: ~azure.ai.ml.entities.JobResourceConfiguration
        """
        return cast(JobResourceConfiguration, self._resources)

    @resources.setter
    def resources(self, value: Union[Dict, JobResourceConfiguration]) -> None:
        """Sets the compute resource configuration for the command component or job.

        :param value: The compute resource configuration for the command component or job.
        :type value: Union[dict, ~azure.ai.ml.entities.JobResourceConfiguration]
        """
        if isinstance(value, dict):
            value = JobResourceConfiguration(**value)
        self._resources = value

    @property
    def queue_settings(self) -> Optional[QueueSettings]:
        """The queue settings for the command component or job.

        :return: The queue settings for the command component or job.
        :rtype: ~azure.ai.ml.entities.QueueSettings
        """
        return self._queue_settings

    @queue_settings.setter
    def queue_settings(self, value: Union[Dict, QueueSettings]) -> None:
        """Sets the queue settings for the command component or job.

        :param value: The queue settings for the command component or job.
        :type value: Union[dict, ~azure.ai.ml.entities.QueueSettings]
        """
        if isinstance(value, dict):
            value = QueueSettings(**value)
        self._queue_settings = value

    @property
    def identity(
        self,
    ) -> Optional[Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]]:
        """The identity that the job will use while running on compute.

        :return: The identity that the job will use while running on compute.
        :rtype: Optional[Union[~azure.ai.ml.ManagedIdentityConfiguration, ~azure.ai.ml.AmlTokenConfiguration,
            ~azure.ai.ml.UserIdentityConfiguration]]
        """
        return self._identity

    @identity.setter
    def identity(
        self,
        value: Optional[Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]],
    ) -> None:
        """Sets the identity that the job will use while running on compute.

        :param value: The identity that the job will use while running on compute.
        :type value: Union[dict[str, str], ~azure.ai.ml.ManagedIdentityConfiguration,
            ~azure.ai.ml.AmlTokenConfiguration, ~azure.ai.ml.UserIdentityConfiguration]
        """
        if isinstance(value, dict):
            identity_schema = UnionField(
                [
                    NestedField(ManagedIdentitySchema, unknown=INCLUDE),
                    NestedField(AMLTokenIdentitySchema, unknown=INCLUDE),
                    NestedField(UserIdentitySchema, unknown=INCLUDE),
                ]
            )
            value = identity_schema._deserialize(value=value, attr=None, data=None)
        self._identity = value

    @property
    def services(
        self,
    ) -> Optional[
        Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]
    ]:
        """The interactive services for the node.

        This is an experimental parameter, and may change at any time.
        Please see https://aka.ms/azuremlexperimental for more information.

        :rtype: dict[str, Union[~azure.ai.ml.entities.JobService, ~azure.ai.ml.entities.JupyterLabJobService,
            ~azure.ai.ml.entities.SshJobService, ~azure.ai.ml.entities.TensorBoardJobService,
            ~azure.ai.ml.entities.VsCodeJobService]]
        """
        return self._services

    @services.setter
    def services(
        self,
        value: Dict,
    ) -> None:
        """Sets the interactive services for the node.

        This is an experimental parameter, and may change at any time.
        Please see https://aka.ms/azuremlexperimental for more information.

        :param value: The interactive services for the node.
        :type value: dict[str, Union[~azure.ai.ml.entities.JobService, ~azure.ai.ml.entities.JupyterLabJobService,
            ~azure.ai.ml.entities.SshJobService, ~azure.ai.ml.entities.TensorBoardJobService,
            ~azure.ai.ml.entities.VsCodeJobService]]
        """
        self._services = _resolve_job_services(value)  # type: ignore[assignment]

    @property
    def component(self) -> Union[str, CommandComponent]:
        """The ID or instance of the command component or job to be run for the step.

        :return: The ID or instance of the command component or job to be run for the step.
        :rtype: Union[str, ~azure.ai.ml.entities.CommandComponent]
        """
        return self._component

    @property
    def command(self) -> Optional[str]:
        """The command to be executed.

        :rtype: Optional[str]
        """
        # the same as code
        if not isinstance(self.component, CommandComponent):
            return None

        if self.component.command is None:
            return None
        return str(self.component.command)

    @command.setter
    def command(self, value: str) -> None:
        """Sets the command to be executed.

        :param value: The command to be executed.
        :type value: str
        """
        if isinstance(self.component, CommandComponent):
            self.component.command = value
        else:
            msg = "Can't set command property for a registered component {}. Tried to set it to {}."
            raise ValidationException(
                message=msg.format(self.component, value),
                no_personal_data_message=msg,
                target=ErrorTarget.COMMAND_JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    @property
    def code(self) -> Optional[Union[str, PathLike]]:
        """The source code to run the job.

        :rtype: Optional[Union[str, os.PathLike]]
        """
        # BaseNode is an _AttrDict to allow dynamic attributes, so that lower version of SDK can work with attributes
        # added in higher version of SDK.
        # self.code will be treated as an Arbitrary attribute if it raises AttributeError in getting
        # (when self.component doesn't have attribute code, self.component = 'azureml:xxx:1' e.g.
        # you may check _AttrDict._is_arbitrary_attr for detailed logic for Arbitrary judgement),
        # then its value will be set to _AttrDict and be deserialized as {"shape": {}} instead of None,
        # which is invalid in schema validation.
        if not isinstance(self.component, CommandComponent):
            return None

        if self.component.code is None:
            return None

        return str(self.component.code)

    @code.setter
    def code(self, value: str) -> None:
        """Sets the source code to run the job.

        :param value: The source code to run the job. Can be a local path or "http:", "https:", or "azureml:" url
            pointing to a remote location.
        :type value: str
        """
        if isinstance(self.component, CommandComponent):
            self.component.code = value
        else:
            msg = "Can't set code property for a registered component {}"
            raise ValidationException(
                message=msg.format(self.component),
                no_personal_data_message=msg,
                target=ErrorTarget.COMMAND_JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    def set_resources(
        self,
        *,
        instance_type: Optional[Union[str, List[str]]] = None,
        instance_count: Optional[int] = None,
        locations: Optional[List[str]] = None,
        properties: Optional[Dict] = None,
        docker_args: Optional[str] = None,
        shm_size: Optional[str] = None,
        # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> None:
        """Set resources for Command.

        :keyword instance_type: The type of compute instance to run the job on. If not specified, the job will run on
            the default compute target.
        :paramtype instance_type: Optional[Union[str, List[str]]]
        :keyword instance_count: The number of instances to run the job on. If not specified, the job will run on a
            single instance.
        :paramtype instance_count: Optional[int]
        :keyword locations: The list of locations where the job will run. If not specified, the job will run on the
            default compute target.
        :paramtype locations: Optional[List[str]]
        :keyword properties: The properties of the job.
        :paramtype properties: Optional[dict]
        :keyword docker_args: The Docker arguments for the job.
        :paramtype docker_args: Optional[str]
        :keyword shm_size: The size of the docker container's shared memory block. This should be in the
            format of (number)(unit) where the number has to be greater than 0 and the unit can be one of
            b(bytes), k(kilobytes), m(megabytes), or g(gigabytes).
        :paramtype shm_size: Optional[str]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_command_configurations.py
                :start-after: [START command_set_resources]
                :end-before: [END command_set_resources]
                :language: python
                :dedent: 8
                :caption: Setting resources on a Command.
        """
        if self.resources is None:
            self.resources = JobResourceConfiguration()

        if locations is not None:
            self.resources.locations = locations
        if instance_type is not None:
            self.resources.instance_type = instance_type
        if instance_count is not None:
            self.resources.instance_count = instance_count
        if properties is not None:
            self.resources.properties = properties
        if docker_args is not None:
            self.resources.docker_args = docker_args
        if shm_size is not None:
            self.resources.shm_size = shm_size

        # Save the resources to internal component as well, otherwise calling sweep() will loose the settings
        if isinstance(self.component, CommandComponent):
            self.component.resources = self.resources

    def set_limits(self, *, timeout: int, **kwargs: Any) -> None:  # pylint: disable=unused-argument
        """Set limits for Command.

        :keyword timeout: The timeout for the job in seconds.
        :paramtype timeout: int

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_command_configurations.py
                :start-after: [START command_set_limits]
                :end-before: [END command_set_limits]
                :language: python
                :dedent: 8
                :caption: Setting a timeout limit of 10 seconds on a Command.
        """
        if isinstance(self.limits, CommandJobLimits):
            self.limits.timeout = timeout
        else:
            self.limits = CommandJobLimits(timeout=timeout)

    def set_queue_settings(self, *, job_tier: Optional[str] = None, priority: Optional[str] = None) -> None:
        """Set QueueSettings for the job.

        :keyword job_tier: The job tier. Accepted values are "Spot", "Basic", "Standard", or "Premium".
        :paramtype job_tier: Optional[str]
        :keyword priority:  The priority of the job on the compute. Defaults to "Medium".
        :paramtype priority: Optional[str]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_command_configurations.py
                :start-after: [START command_set_queue_settings]
                :end-before: [END command_set_queue_settings]
                :language: python
                :dedent: 8
                :caption: Configuring queue settings on a Command.
        """
        if isinstance(self.queue_settings, QueueSettings):
            self.queue_settings.job_tier = job_tier
            self.queue_settings.priority = priority
        else:
            self.queue_settings = QueueSettings(job_tier=job_tier, priority=priority)

    def sweep(
        self,
        *,
        primary_metric: str,
        goal: str,
        sampling_algorithm: str = "random",
        compute: Optional[str] = None,
        max_concurrent_trials: Optional[int] = None,
        max_total_trials: Optional[int] = None,
        timeout: Optional[int] = None,
        trial_timeout: Optional[int] = None,
        early_termination_policy: Optional[Union[EarlyTerminationPolicy, str]] = None,
        search_space: Optional[
            Dict[
                str,
                Union[
                    Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform
                ],
            ]
        ] = None,
        identity: Optional[
            Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
        queue_settings: Optional[QueueSettings] = None,
        job_tier: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> Sweep:
        """Turns the command into a sweep node with extra sweep run setting. The command component
        in the current command node will be used as its trial component. A command node can sweep
        multiple times, and the generated sweep node will share the same trial component.

        :keyword primary_metric: The primary metric of the sweep objective - e.g. AUC (Area Under the Curve).
            The metric must be logged while running the trial component.
        :paramtype primary_metric: str
        :keyword goal: The goal of the Sweep objective. Accepted values are "minimize" or "maximize".
        :paramtype goal: str
        :keyword sampling_algorithm: The sampling algorithm to use inside the search space.
            Acceptable values are "random", "grid", or "bayesian". Defaults to "random".
        :paramtype sampling_algorithm: str
        :keyword compute: The target compute to run the node on. If not specified, the current node's compute
            will be used.
        :paramtype compute: Optional[str]
        :keyword max_total_trials: The maximum number of total trials to run. This value will overwrite the value in
            CommandJob.limits if specified.
        :paramtype max_total_trials: Optional[int]
        :keyword max_concurrent_trials: The maximum number of concurrent trials for the Sweep job.
        :paramtype max_concurrent_trials: Optional[int]
        :keyword timeout: The maximum run duration in seconds, after which the job will be cancelled.
        :paramtype timeout: Optional[int]
        :keyword trial_timeout: The Sweep Job trial timeout value, in seconds.
        :paramtype trial_timeout: Optional[int]
        :keyword early_termination_policy: The early termination policy of the sweep node. Acceptable
            values are "bandit", "median_stopping", or "truncation_selection". Defaults to None.
        :paramtype early_termination_policy: Optional[Union[~azure.ai.ml.sweep.BanditPolicy,
            ~azure.ai.ml.sweep.TruncationSelectionPolicy, ~azure.ai.ml.sweep.MedianStoppingPolicy, str]]
        :keyword identity: The identity that the job will use while running on compute.
        :paramtype identity: Optional[Union[
            ~azure.ai.ml.ManagedIdentityConfiguration,
            ~azure.ai.ml.AmlTokenConfiguration,
            ~azure.ai.ml.UserIdentityConfiguration]]
        :keyword search_space: The search space to use for the sweep job.
        :paramtype search_space: Optional[Dict[str, Union[
            Choice,
            LogNormal,
            LogUniform,
            Normal,
            QLogNormal,
            QLogUniform,
            QNormal,
            QUniform,
            Randint,
            Uniform

        ]]]

        :keyword queue_settings: The queue settings for the job.
        :paramtype queue_settings: Optional[~azure.ai.ml.entities.QueueSettings]
        :keyword job_tier: **Experimental** The job tier. Accepted values are "Spot", "Basic",
            "Standard", or "Premium".
        :paramtype job_tier: Optional[str]
        :keyword priority: **Experimental** The compute priority. Accepted values are "low",
            "medium", and "high".
        :paramtype priority: Optional[str]
        :return: A Sweep node with the component from current Command node as its trial component.
        :rtype: ~azure.ai.ml.entities.Sweep

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
                :start-after: [START configure_sweep_job_bandit_policy]
                :end-before: [END configure_sweep_job_bandit_policy]
                :language: python
                :dedent: 8
                :caption: Creating a Sweep node from a Command job.
        """
        self._swept = True
        # inputs & outputs are already built in source Command obj
        # pylint: disable=abstract-class-instantiated
        inputs, inputs_search_space = Sweep._get_origin_inputs_and_search_space(self.inputs)
        if search_space:
            inputs_search_space.update(search_space)

        if not queue_settings:
            queue_settings = self.queue_settings
        if queue_settings is not None:
            if job_tier is not None:
                queue_settings.job_tier = job_tier
            if priority is not None:
                queue_settings.priority = priority

        sweep_node = Sweep(
            trial=copy.deepcopy(
                self.component
            ),  # Make a copy of the underneath Component so that the original node can still be used.
            compute=self.compute if compute is None else compute,
            objective=Objective(goal=goal, primary_metric=primary_metric),
            sampling_algorithm=sampling_algorithm,
            inputs=inputs,
            outputs=self._get_origin_job_outputs(),
            search_space=inputs_search_space,
            early_termination=early_termination_policy,
            name=self.name,
            description=self.description,
            display_name=self.display_name,
            tags=self.tags,
            properties=self.properties,
            experiment_name=self.experiment_name,
            identity=self.identity if not identity else identity,
            _from_component_func=True,
            queue_settings=queue_settings,
        )
        sweep_node.set_limits(
            max_total_trials=max_total_trials,
            max_concurrent_trials=max_concurrent_trials,
            timeout=timeout,
            trial_timeout=trial_timeout,
        )
        return sweep_node

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "component": (str, CommandComponent),
            "environment": (str, Environment),
            "environment_variables": dict,
            "resources": (dict, JobResourceConfiguration),
            "limits": (dict, CommandJobLimits),
            "code": (str, os.PathLike),
        }

    def _to_job(self) -> CommandJob:
        if isinstance(self.component, CommandComponent):
            return CommandJob(
                id=self.id,
                name=self.name,
                display_name=self.display_name,
                description=self.description,
                tags=self.tags,
                properties=self.properties,
                command=self.component.command,
                experiment_name=self.experiment_name,
                code=self.component.code,
                compute=self.compute,
                status=self.status,
                environment=self.environment,
                distribution=self.distribution,
                identity=self.identity,
                environment_variables=self.environment_variables,
                resources=self.resources,
                limits=self.limits,
                inputs=self._job_inputs,
                outputs=self._job_outputs,
                services=self.services,
                creation_context=self.creation_context,
                parameters=self.parameters,
                queue_settings=self.queue_settings,
            )

        return CommandJob(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            properties=self.properties,
            command=None,
            experiment_name=self.experiment_name,
            code=None,
            compute=self.compute,
            status=self.status,
            environment=self.environment,
            distribution=self.distribution,
            identity=self.identity,
            environment_variables=self.environment_variables,
            resources=self.resources,
            limits=self.limits,
            inputs=self._job_inputs,
            outputs=self._job_outputs,
            services=self.services,
            creation_context=self.creation_context,
            parameters=self.parameters,
            queue_settings=self.queue_settings,
        )

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["resources", "distribution", "limits", "environment_variables", "queue_settings"]

    def _to_rest_object(self, **kwargs: Any) -> dict:
        rest_obj = super()._to_rest_object(**kwargs)
        for key, value in {
            "componentId": self._get_component_id(),
            "distribution": get_rest_dict_for_node_attrs(self.distribution, clear_empty_value=True),
            "limits": get_rest_dict_for_node_attrs(self.limits, clear_empty_value=True),
            "resources": get_rest_dict_for_node_attrs(self.resources, clear_empty_value=True),
            "services": get_rest_dict_for_node_attrs(self.services),
            "identity": get_rest_dict_for_node_attrs(self.identity),
            "queue_settings": get_rest_dict_for_node_attrs(self.queue_settings, clear_empty_value=True),
        }.items():
            if value is not None:
                rest_obj[key] = value
        return cast(dict, convert_ordered_dict_to_dict(rest_obj))

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "Command":
        from .command_func import command

        loaded_data = load_from_dict(CommandJobSchema, data, context, additional_message, **kwargs)

        # resources a limits properties are flatten in command() function, exact them and set separately
        resources = loaded_data.pop("resources", None)
        limits = loaded_data.pop("limits", None)

        command_job: Command = command(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

        command_job.resources = resources
        command_job.limits = limits
        return command_job

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: dict) -> Dict:
        obj = BaseNode._from_rest_object_to_init_params(obj)

        if "resources" in obj and obj["resources"]:
            obj["resources"] = JobResourceConfiguration._from_rest_object(obj["resources"])

        # services, sweep won't have services
        if "services" in obj and obj["services"]:
            # pipeline node rest object are dicts while _from_rest_job_services expect RestJobService
            services = {}
            for service_name, service in obj["services"].items():
                # in rest object of a pipeline job, service will be transferred to a dict as
                # it's attributes of a node, but JobService._from_rest_object expect a
                # RestJobService, so we need to convert it back. Here we convert the dict to a
                # dummy rest object which may work as a RestJobService instead.
                services[service_name] = from_rest_dict_to_dummy_rest_object(service)
            obj["services"] = JobServiceBase._from_rest_job_services(services)

        # handle limits
        if "limits" in obj and obj["limits"]:
            obj["limits"] = CommandJobLimits._from_rest_object(obj["limits"])

        if "identity" in obj and obj["identity"]:
            obj["identity"] = _BaseJobIdentityConfiguration._from_rest_object(obj["identity"])

        if "queue_settings" in obj and obj["queue_settings"]:
            obj["queue_settings"] = QueueSettings._from_rest_object(obj["queue_settings"])

        return obj

    @classmethod
    def _load_from_rest_job(cls, obj: JobBase) -> "Command":
        from .command_func import command

        rest_command_job: RestCommandJob = obj.properties

        command_job: Command = command(
            name=obj.name,
            display_name=rest_command_job.display_name,
            description=rest_command_job.description,
            tags=rest_command_job.tags,
            properties=rest_command_job.properties,
            command=rest_command_job.command,
            experiment_name=rest_command_job.experiment_name,
            services=JobServiceBase._from_rest_job_services(rest_command_job.services),
            status=rest_command_job.status,
            creation_context=SystemData._from_rest_object(obj.system_data) if obj.system_data else None,
            code=rest_command_job.code_id,
            compute=rest_command_job.compute_id,
            environment=rest_command_job.environment_id,
            distribution=DistributionConfiguration._from_rest_object(rest_command_job.distribution),
            parameters=rest_command_job.parameters,
            identity=(
                _BaseJobIdentityConfiguration._from_rest_object(rest_command_job.identity)
                if rest_command_job.identity
                else None
            ),
            environment_variables=rest_command_job.environment_variables,
            inputs=from_rest_inputs_to_dataset_literal(rest_command_job.inputs),
            outputs=from_rest_data_outputs(rest_command_job.outputs),
        )
        command_job._id = obj.id
        command_job.resources = cast(
            JobResourceConfiguration, JobResourceConfiguration._from_rest_object(rest_command_job.resources)
        )
        command_job.limits = CommandJobLimits._from_rest_object(rest_command_job.limits)
        command_job.queue_settings = QueueSettings._from_rest_object(rest_command_job.queue_settings)
        if isinstance(command_job.component, CommandComponent):
            command_job.component._source = (
                ComponentSource.REMOTE_WORKSPACE_JOB
            )  # This is used by pipeline job telemetries.

        # Handle special case of local job
        if (
            command_job.resources is not None
            and command_job.resources.properties is not None
            and command_job.resources.properties.get(LOCAL_COMPUTE_PROPERTY, None)
        ):
            command_job.compute = LOCAL_COMPUTE_TARGET
            command_job.resources.properties.pop(LOCAL_COMPUTE_PROPERTY)
        return command_job

    def _build_inputs(self) -> Dict:
        inputs = super(Command, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value

        return built_inputs

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline import CommandSchema

        return CommandSchema(context=context)

    # pylint: disable-next=docstring-missing-param
    def __call__(self, *args: Any, **kwargs: Any) -> "Command":
        """Call Command as a function will return a new instance each time.

        :return: A Command node
        :rtype: Command
        """
        if isinstance(self._component, CommandComponent):
            # call this to validate inputs
            node: Command = self._component(*args, **kwargs)
            # merge inputs
            for name, original_input in self.inputs.items():
                if name not in kwargs:
                    # use setattr here to make sure owner of input won't change
                    setattr(node.inputs, name, original_input._data)
                    node._job_inputs[name] = original_input._data
                # get outputs
            for name, original_output in self.outputs.items():
                # use setattr here to make sure owner of input won't change
                if not isinstance(original_output, str):
                    setattr(node.outputs, name, original_output._data)
            self._refine_optional_inputs_with_no_value(node, kwargs)
            # set default values: compute, environment_variables, outputs
            # won't copy name to be able to distinguish if a node's name is assigned by user
            # e.g. node_1 = command_func()
            # In above example, node_1.name will be None so we can apply node_1 as it's name
            node.compute = self.compute
            node.tags = self.tags
            # Pass through the display name only if the display name is not system generated.
            node.display_name = self.display_name if self.display_name != self.name else None
            node.environment = copy.deepcopy(self.environment)
            # deep copy for complex object
            node.environment_variables = copy.deepcopy(self.environment_variables)
            node.limits = copy.deepcopy(self.limits)
            node.distribution = copy.deepcopy(self.distribution)
            node.resources = copy.deepcopy(self.resources)
            node.queue_settings = copy.deepcopy(self.queue_settings)
            node.services = copy.deepcopy(self.services)
            node.identity = copy.deepcopy(self.identity)
            return node
        msg = "Command can be called as a function only when referenced component is {}, currently got {}."
        raise ValidationException(
            message=msg.format(type(CommandComponent), self._component),
            no_personal_data_message=msg.format(type(CommandComponent), "self._component"),
            target=ErrorTarget.COMMAND_JOB,
            error_type=ValidationErrorType.INVALID_VALUE,
        )


@overload
def _resolve_job_services(services: Optional[Dict]): ...


@overload
def _resolve_job_services(
    services: Dict[str, Union[JobServiceBase, Dict]],
) -> Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]: ...


def _resolve_job_services(
    services: Optional[Dict[str, Union[JobServiceBase, Dict]]],
) -> Optional[Dict]:
    """Resolve normal dict to dict[str, JobService]

    :param services: A dict that maps service names to either a JobServiceBase object, or a Dict used to build one
    :type services: Optional[Dict[str, Union[JobServiceBase, Dict]]]
    :return:
        * None if `services` is None
        * A map of job service names to job services
    :rtype: Optional[
            Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]
        ]
    """
    if services is None:
        return None

    if not isinstance(services, dict):
        msg = f"Services must be a dict, got {type(services)} instead."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.COMMAND_JOB,
            error_category=ErrorCategory.USER_ERROR,
        )

    result = {}
    for name, service in services.items():
        if isinstance(service, dict):
            service = load_from_dict(JobServiceSchema, service, context={BASE_PATH_CONTEXT_KEY: "."})
        elif not isinstance(
            service, (JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService)
        ):
            msg = f"Service value for key {name!r} must be a dict or JobService object, got {type(service)} instead."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.COMMAND_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        result[name] = service
    return result
