# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
import logging
import os
from enum import Enum
from os import PathLike
from typing import Dict, List, Optional, Union

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
from azure.ai.ml.entities._component.component import Component
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
    TensorFlowDistribution,
    RayDistribution,
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
    TensorFlowDistributionSchema,
    RayDistributionSchema,
)
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


class Command(BaseNode):
    """Base class for command node, used for command component version consumption.

    You should not instantiate this class directly. Instead, you should
    create from builder function: command.

    :param component: Id or instance of the command component/job to be run for the step
    :type component: CommandComponent
    :param inputs: Inputs to the command.
    :type inputs: Dict[str, Union[Input, SweepDistribution, str, bool, int, float, Enum, dict]]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Dict[str, Union[str, Output, dict]]
    :param name: Name of the command.
    :type name: str
    :param description: Description of the command.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The job property dictionary.
    :type properties: dict[str, str]
    :param display_name: Display name of the job.
    :type display_name: str
    :param experiment_name:  Name of the experiment the job will be created under,
        if None is provided, default will be set to current directory name.
    :type experiment_name: str
    :param command: Command to be executed in training.
    :type command: str
    :param compute: The compute target the job runs on.
    :type compute: str
    :param resources: Compute Resource configuration for the command.
    :type resources: Union[Dict, ~azure.ai.ml.entities.JobResourceConfiguration]
    :param code: A local path or http:, https:, azureml: url pointing to a remote location.
    :type code: str
    :param distribution: Distribution configuration for distributed training.
    :type distribution: Union[Dict, PyTorchDistribution, MpiDistribution, TensorFlowDistribution, RayDistribution]
    :param environment: Environment that training job will run in.
    :type environment: Union[Environment, str]
    :param limits: Command Job limit.
    :type limits: ~azure.ai.ml.entities.CommandJobLimits
    :param identity: Identity that training job will use while running on compute.
    :type identity: Union[ManagedIdentity, AmlToken, UserIdentity]
    :param services: Interactive services for the node. This is an experimental parameter, and may change at any time.
        Please see https://aka.ms/azuremlexperimental for more information.
    :type services:
        Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]
    :param queue_settings: Queue settings for the job.
    :type queue_settings: QueueSettings
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
            Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
        distribution: Optional[
            Union[Dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution, RayDistribution]
        ] = None,
        environment: Optional[Union[Environment, str]] = None,
        environment_variables: Optional[Dict] = None,
        resources: Optional[JobResourceConfiguration] = None,
        services: Optional[
            Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]
        ] = None,
        queue_settings: Optional[QueueSettings] = None,
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        # resolve normal dict to dict[str, JobService]
        services = _resolve_job_services(services)
        kwargs.pop("type", None)
        self._parameters = kwargs.pop("parameters", {})
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
        self.environment = environment
        self._resources = resources
        self._services = services
        self.queue_settings = queue_settings

        if isinstance(self.component, CommandComponent):
            self.resources = self.resources or self.component.resources
            self.distribution = self.distribution or self.component.distribution

        self._swept = False
        self._init = False

    @classmethod
    def _get_supported_inputs_types(cls):
        supported_types = super()._get_supported_inputs_types() or ()
        return (
            SweepDistribution,
            *supported_types,
        )

    @classmethod
    def _get_supported_outputs_types(cls):
        return str, Output

    @property
    def parameters(self) -> Dict[str, str]:
        """MLFlow parameters.

        :return: MLFlow parameters logged in job.
        :rtype: Dict[str, str]
        """
        return self._parameters

    @property
    def distribution(
        self,
    ) -> Union[PyTorchDistribution, MpiDistribution, TensorFlowDistribution, RayDistribution]:
        return self._distribution

    @distribution.setter
    def distribution(
        self,
        value: Union[Dict, PyTorchDistribution, TensorFlowDistribution, MpiDistribution, RayDistribution],
    ):
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
        return self._resources

    @resources.setter
    def resources(self, value: Union[Dict, JobResourceConfiguration]):
        if isinstance(value, dict):
            value = JobResourceConfiguration(**value)
        self._resources = value

    @property
    def queue_settings(self) -> QueueSettings:
        return self._queue_settings

    @queue_settings.setter
    def queue_settings(self, value: Union[Dict, QueueSettings]):
        if isinstance(value, dict):
            value = QueueSettings(**value)
        self._queue_settings = value

    @property
    def identity(
        self,
    ) -> Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]]:
        """Configuration of the hyperparameter identity."""
        return self._identity

    @identity.setter
    def identity(
        self,
        value: Union[
            Dict[str, str], ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration, None
        ],
    ):
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
    def services(self) -> Dict:
        return self._services

    @services.setter
    def services(self, value: Dict):
        self._services = _resolve_job_services(value)

    @property
    def component(self) -> Union[str, CommandComponent]:
        return self._component

    @property
    def command(self) -> Optional[str]:
        # the same as code
        return self.component.command if hasattr(self.component, "command") else None

    @command.setter
    def command(self, value: str) -> None:
        if isinstance(self.component, Component):
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
        # BaseNode is an _AttrDict to allow dynamic attributes, so that lower version of SDK can work with attributes
        # added in higher version of SDK.
        # self.code will be treated as an Arbitrary attribute if it raises AttributeError in getting
        # (when self.component doesn't have attribute code, self.component = 'azureml:xxx:1' e.g.
        # you may check _AttrDict._is_arbitrary_attr for detailed logic for Arbitrary judgement),
        # then its value will be set to _AttrDict and be deserialized as {"shape": {}} instead of None,
        # which is invalid in schema validation.
        return self.component.code if hasattr(self.component, "code") else None

    @code.setter
    def code(self, value: str) -> None:
        if isinstance(self.component, Component):
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
        **kwargs,  # pylint: disable=unused-argument
    ):
        """Set resources for Command."""
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
        if isinstance(self.component, Component):
            self.component.resources = self.resources

    def set_limits(self, *, timeout: int, **kwargs):  # pylint: disable=unused-argument
        """Set limits for Command."""
        if isinstance(self.limits, CommandJobLimits):
            self.limits.timeout = timeout
        else:
            self.limits = CommandJobLimits(timeout=timeout)

    def set_queue_settings(self, *, job_tier: Optional[str] = None, priority: Optional[str] = None):
        """Set QueueSettings for the job.
        :param job_tier: determines the job tier.
        :type job_tier: str
        :param priority: controls the priority on the compute.
        :type priority: str
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
        """Turn the command into a sweep node with extra sweep run setting. The command component in current Command
        node will be used as its trial component. A command node can sweep for multiple times, and the generated sweep
        node will share the same trial component.

        :param primary_metric: primary metric of the sweep objective, AUC e.g. The metric must be logged in running
            the trial component.
        :type primary_metric: str
        :param goal: goal of the sweep objective.
        :type goal: str, valid values: maximize or minimize
        :param sampling_algorithm: sampling algorithm to sample inside search space. Defaults to "random"
        :type sampling_algorithm: str, valid values: random, grid or bayesian
        :param compute: target compute to run the node. If not specified, compute of current node will be used.
        :type compute: str
        :param max_total_trials: maximum trials to run, will overwrite value in limits
        :type max_total_trials: int
        :param max_concurrent_trials: Sweep Job max concurrent trials.
        :type max_concurrent_trials: int
        :param max_total_trials: Sweep Job max total trials.
        :type max_total_trials: int
        :param timeout: The max run duration in seconds, after which the job will be cancelled.
        :type timeout: int
        :param trial_timeout: Sweep Job Trial timeout value in seconds.
        :type trial_timeout: int
        :param early_termination_policy: early termination policy of the sweep node:
        :type early_termination_policy: Union[EarlyTerminationPolicy, str], valid values: bandit, median_stopping
            or truncation_selection.
        :param identity: Identity that training job will use while running on compute.
        :type identity: Union[
            ManagedIdentityConfiguration,
            AmlTokenConfiguration,
            UserIdentityConfiguration]
        :param queue_settings: Queue settings for the job.
        :type queue_settings: QueueSettings
        :param job_tier: **Experimental** determines the job tier.
        :type job_tier: str
        :param priority: **Experimental** controls the priority on the compute.
        :type priority: str
        :return: A sweep node with component from current Command node as its trial component.
        :rtype: Sweep
        """
        self._swept = True
        # inputs & outputs are already built in source Command obj
        # pylint: disable=abstract-class-instantiated
        inputs, inputs_search_space = Sweep._get_origin_inputs_and_search_space(self.inputs)
        if search_space:
            inputs_search_space.update(search_space)

        if not queue_settings:
            queue_settings = self.queue_settings
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

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["resources", "distribution", "limits", "environment_variables", "queue_settings"]

    def _to_rest_object(self, **kwargs) -> dict:
        rest_obj = super()._to_rest_object(**kwargs)
        for key, value in {
            "componentId": self._get_component_id(),
            "distribution": get_rest_dict_for_node_attrs(self.distribution, clear_empty_value=True),
            "limits": get_rest_dict_for_node_attrs(self.limits, clear_empty_value=True),
            "resources": get_rest_dict_for_node_attrs(self.resources, clear_empty_value=True),
            "services": get_rest_dict_for_node_attrs(self.services),
            "identity": self.identity._to_dict() if self.identity else None,
            "queue_settings": get_rest_dict_for_node_attrs(self.queue_settings, clear_empty_value=True),
        }.items():
            if value is not None:
                rest_obj[key] = value
        return convert_ordered_dict_to_dict(rest_obj)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "Command":
        from .command_func import command

        loaded_data = load_from_dict(CommandJobSchema, data, context, additional_message, **kwargs)

        # resources a limits properties are flatten in command() function, exact them and set separately
        resources = loaded_data.pop("resources", None)
        limits = loaded_data.pop("limits", None)

        command_job = command(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

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
            obj["identity"] = _BaseJobIdentityConfiguration._load(obj["identity"])

        if "queue_settings" in obj and obj["queue_settings"]:
            obj["queue_settings"] = QueueSettings._from_rest_object(obj["queue_settings"])

        return obj

    @classmethod
    def _load_from_rest_job(cls, obj: JobBase) -> "Command":
        from .command_func import command

        rest_command_job: RestCommandJob = obj.properties

        command_job = command(
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
            identity=_BaseJobIdentityConfiguration._from_rest_object(rest_command_job.identity)
            if rest_command_job.identity
            else None,
            environment_variables=rest_command_job.environment_variables,
            inputs=from_rest_inputs_to_dataset_literal(rest_command_job.inputs),
            outputs=from_rest_data_outputs(rest_command_job.outputs),
        )
        command_job._id = obj.id
        command_job.resources = JobResourceConfiguration._from_rest_object(rest_command_job.resources)
        command_job.limits = CommandJobLimits._from_rest_object(rest_command_job.limits)
        command_job.queue_settings = QueueSettings._from_rest_object(rest_command_job.queue_settings)
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

    def _build_inputs(self):
        inputs = super(Command, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value

        return built_inputs

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline import CommandSchema

        return CommandSchema(context=context)

    def __call__(self, *args, **kwargs) -> "Command":
        """Call Command as a function will return a new instance each time."""
        if isinstance(self._component, Component):
            # call this to validate inputs
            node = self._component(*args, **kwargs)
            # merge inputs
            for name, original_input in self.inputs.items():
                if name not in kwargs.keys():
                    # use setattr here to make sure owner of input won't change
                    setattr(node.inputs, name, original_input._data)
                    node._job_inputs[name] = original_input._data
                # get outputs
            for name, original_output in self.outputs.items():
                # use setattr here to make sure owner of input won't change
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
            message=msg.format(type(Component), self._component),
            no_personal_data_message=msg.format(type(Component), "self._component"),
            target=ErrorTarget.COMMAND_JOB,
            error_type=ValidationErrorType.INVALID_VALUE,
        )


def _resolve_job_services(
    services: dict,
) -> Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]:
    """Resolve normal dict to dict[str, JobService]"""
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
