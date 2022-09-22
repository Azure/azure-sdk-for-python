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

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2022_02_01_preview.models import AmlToken
from azure.ai.ml._restclient.v2022_02_01_preview.models import CommandJob as RestCommandJob
from azure.ai.ml._restclient.v2022_02_01_preview.models import CommandJobLimits as RestCommandJobLimits
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobBaseData, ManagedIdentity
from azure.ai.ml._restclient.v2022_02_01_preview.models import ResourceConfiguration as RestResourceConfiguration
from azure.ai.ml._restclient.v2022_02_01_preview.models import UserIdentity
from azure.ai.ml._schema.core.fields import NestedField, UnionField
from azure.ai.ml._schema.job.command_job import CommandJobSchema
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
    LOCAL_COMPUTE_PROPERTY,
    LOCAL_COMPUTE_TARGET,
    ComponentSource,
    NodeType,
)
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.command_job import CommandJob
from azure.ai.ml.entities._job.job_limits import CommandJobLimits
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, from_rest_inputs_to_dataset_literal
from azure.ai.ml.entities._job.distribution import (
    DistributionConfiguration,
    MpiDistribution,
    PyTorchDistribution,
    TensorFlowDistribution,
)
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
from azure.ai.ml.entities._job.sweep.early_termination_policy import EarlyTerminationPolicy
from azure.ai.ml.entities._job.sweep.objective import Objective
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution

from ..._schema import PathAwareSchema
from ..._schema.job.distribution import MPIDistributionSchema, PyTorchDistributionSchema, TensorFlowDistributionSchema
from .._job.pipeline._io import PipelineInput, PipelineOutputBase
from .._job.pipeline._pipeline_expression import PipelineExpression
from .._util import convert_ordered_dict_to_dict, get_rest_dict, load_from_dict, validate_attribute_type
from .base_node import BaseNode
from .sweep import Sweep

module_logger = logging.getLogger(__name__)


class Command(BaseNode):
    """Base class for command node, used for command component version
    consumption.

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
    :param experiment_name:  Name of the experiment the job will be created under, if None is provided, default will be set to current directory name.
    :type experiment_name: str
    :param command: Command to be executed in training.
    :type command: str
    :param compute: The compute target the job runs on.
    :type compute: str
    :param resources: Compute Resource configuration for the command.
    :type resources: Union[Dict, ~azure.ai.ml.entities.ResourceConfiguration]
    :param code: A local path or http:, https:, azureml: url pointing to a remote location.
    :type code: str
    :param distribution: Distribution configuration for distributed training.
    :type distribution: Union[Dict, PyTorchDistribution, MpiDistribution, TensorFlowDistribution]
    :param environment: Environment that training job will run in.
    :type environment: Union[Environment, str]
    :param limits: Command Job limit.
    :type limits: ~azure.ai.ml.entities.CommandJobLimits
    :param identity: Identity that training job will use while running on compute.
    :type identity: Union[ManagedIdentity, AmlToken, UserIdentity]
    """

    def __init__(
        self,
        *,
        component: Union[str, CommandComponent],
        compute: str = None,
        inputs: Dict[
            str,
            Union[
                PipelineInput,
                PipelineOutputBase,
                Input,
                str,
                bool,
                int,
                float,
                Enum,
                "Input",
            ],
        ] = None,
        outputs: Dict[str, Union[str, Output, "Output"]] = None,
        limits: CommandJobLimits = None,
        identity: Union[ManagedIdentity, AmlToken, UserIdentity] = None,
        distribution: Union[Dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution] = None,
        environment: Union[Environment, str] = None,
        environment_variables: Dict = None,
        resources: ResourceConfiguration = None,
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs.pop("type", None)
        self._parameters = kwargs.pop("parameters", {})
        BaseNode.__init__(
            self,
            type=NodeType.COMMAND,
            inputs=inputs,
            outputs=outputs,
            component=component,
            compute=compute,
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

        if isinstance(self.component, CommandComponent):
            self.resources = self.resources or self.component.resources
            self.distribution = self.distribution or self.component.distribution

        self._swept = False
        self._init = False

    @classmethod
    def _get_supported_inputs_types(cls):
        # when command node is constructed inside dsl.pipeline, inputs can be PipelineInput or Output of another node
        return (
            PipelineInput,
            PipelineOutputBase,
            Input,
            SweepDistribution,
            str,
            bool,
            int,
            float,
            Enum,
            PipelineExpression,
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
    ) -> Union[PyTorchDistribution, MpiDistribution, TensorFlowDistribution]:
        return self._distribution

    @distribution.setter
    def distribution(
        self,
        value: Union[Dict, PyTorchDistribution, TensorFlowDistribution, MpiDistribution],
    ):
        if isinstance(value, dict):
            dist_schema = UnionField(
                [
                    NestedField(PyTorchDistributionSchema, unknown=INCLUDE),
                    NestedField(TensorFlowDistributionSchema, unknown=INCLUDE),
                    NestedField(MPIDistributionSchema, unknown=INCLUDE),
                ]
            )
            value = dist_schema._deserialize(value=value, attr=None, data=None)
        self._distribution = value

    @property
    def resources(self) -> ResourceConfiguration:
        return self._resources

    @resources.setter
    def resources(self, value: Union[Dict, ResourceConfiguration]):
        if isinstance(value, dict):
            value = ResourceConfiguration(**value)
        self._resources = value

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
            msg = "Can't set command property for a registered component {}"
            raise ValidationException(
                msg=msg.format(self.component),
                no_personal_data_message=msg.format(self.component),
                target=ErrorTarget.COMMAND_JOB,
                error_category=ErrorCategory.USER_ERROR,
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
                msg=msg.format(self.component),
                no_personal_data_message=msg.format(self.component),
                target=ErrorTarget.COMMAND_JOB,
                error_category=ErrorCategory.USER_ERROR,
            )

    def set_resources(
        self,
        *,
        instance_type: Union[str, List[str]] = None,
        instance_count: int = None,
        properties: Dict = None,
        **kwargs,
    ):
        """Set resources for Command."""
        if self.resources is None:
            self.resources = ResourceConfiguration()

        if instance_type is not None:
            self.resources.instance_type = instance_type
        if instance_count is not None:
            self.resources.instance_count = instance_count
        if properties is not None:
            self.resources.properties = properties

        # Save the resources to internal component as well, otherwise calling sweep() will loose the settings
        if isinstance(self.component, Component):
            self.component.resources = self.resources

    def set_limits(self, *, timeout: int, **kwargs):
        """Set limits for Command."""
        if isinstance(self.limits, CommandJobLimits):
            self.limits.timeout = timeout
        else:
            self.limits = CommandJobLimits(timeout=timeout)

    def sweep(
        self,
        *,
        primary_metric: str,
        goal: str,
        sampling_algorithm: str = "random",
        compute: str = None,
        max_concurrent_trials: int = None,
        max_total_trials: int = None,
        timeout: int = None,
        trial_timeout: int = None,
        early_termination_policy: Union[EarlyTerminationPolicy, str] = None,
        search_space: Dict[str, SweepDistribution] = None,
        identity: Union[ManagedIdentity, AmlToken, UserIdentity] = None,
    ) -> Sweep:
        """Turn the command into a sweep node with extra sweep run setting. The
        command component in current Command node will be used as its trial
        component. A command node can sweep for multiple times, and the
        generated sweep node will share the same trial component.

        :param primary_metric: primary metric of the sweep objective, AUC e.g. The metric must be logged in
        running the trial component.
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
        :param timeout: The max run duration in seconds , after which the job will be cancelled.
        :type timeout: int
        :param trial_timeout: Sweep Job Trial timeout value in seconds.
        :type trial_timeout: int
        :param early_termination_policy: early termination policy of the sweep node:
        :type early_termination_policy: Union[EarlyTerminationPolicy, str], valid values: bandit, median_stopping or
        truncation_selection.
        :param identity: Identity that training job will use while running on compute.
        :type identity: Union[ManagedIdentity, AmlToken, UserIdentity]
        :return: A sweep node with component from current Command node as its trial component.
        :rtype: Sweep
        """
        self._swept = True
        # inputs & outputs are already built in source Command obj
        inputs, inputs_search_space = Sweep._get_origin_inputs_and_search_space(self.inputs)
        if search_space:
            inputs_search_space.update(search_space)

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
            "resources": (dict, ResourceConfiguration),
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
        )

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["resources", "distribution", "limits", "environment_variables"]

    def _to_rest_object(self, **kwargs) -> dict:
        rest_obj = super()._to_rest_object(**kwargs)
        rest_obj.update(
            convert_ordered_dict_to_dict(
                dict(
                    componentId=self._get_component_id(),
                    distribution=get_rest_dict(self.distribution),
                    limits=get_rest_dict(self.limits),
                    resources=get_rest_dict(self.resources, clear_empty_value=True),
                )
            )
        )
        return rest_obj

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
    def _from_rest_object(cls, obj: dict) -> "Command":
        obj = BaseNode._rest_object_to_init_params(obj)

        # resources, sweep won't have resources
        if "resources" in obj and obj["resources"]:
            resources = RestResourceConfiguration.from_dict(obj["resources"])
            obj["resources"] = ResourceConfiguration._from_rest_object(resources)

        # Change componentId -> component
        component_id = obj.pop("componentId", None)
        obj["component"] = component_id

        # distribution, sweep won't have distribution
        if "distribution" in obj and obj["distribution"]:
            obj["distribution"] = DistributionConfiguration._from_rest_object(obj["distribution"])

        # handle limits
        if "limits" in obj and obj["limits"]:
            rest_limits = RestCommandJobLimits.from_dict(obj["limits"])
            obj["limits"] = CommandJobLimits()._from_rest_object(rest_limits)

        return Command(**obj)

    @classmethod
    def _load_from_rest_job(cls, obj: JobBaseData) -> "Command":
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
            services=rest_command_job.services,
            status=rest_command_job.status,
            creation_context=obj.system_data,
            code=rest_command_job.code_id,
            compute=rest_command_job.compute_id,
            environment=rest_command_job.environment_id,
            distribution=DistributionConfiguration._from_rest_object(rest_command_job.distribution),
            parameters=rest_command_job.parameters,
            identity=rest_command_job.identity,
            environment_variables=rest_command_job.environment_variables,
            inputs=from_rest_inputs_to_dataset_literal(rest_command_job.inputs),
            outputs=from_rest_data_outputs(rest_command_job.outputs),
        )
        command_job._id = obj.id
        command_job.resources = ResourceConfiguration._from_rest_object(rest_command_job.resources)
        command_job.limits = CommandJobLimits._from_rest_object(rest_command_job.limits)
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
            node._name = self.name
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
            return node
        else:
            msg = "Command can be called as a function only when referenced component is {}, currently got {}."
            raise ValidationException(
                message=msg.format(type(Component), self._component),
                no_personal_data_message=msg.format(type(Component), self._component),
                target=ErrorTarget.COMMAND_JOB,
            )
