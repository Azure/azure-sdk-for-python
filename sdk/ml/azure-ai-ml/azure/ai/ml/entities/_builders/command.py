# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import logging
import os
import uuid
from enum import Enum
from typing import Dict, List, Optional, Union

from os import PathLike

from marshmallow import INCLUDE

from azure.ai.ml._schema.core.fields import NestedField, UnionField
from .base_node import BaseNode
from .sweep import Sweep
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ManagedIdentity,
    AmlToken,
    UserIdentity,
    CommandJobLimits as RestCommandJobLimits,
)
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, NodeType

from azure.ai.ml.entities._job.sweep.objective import Objective
from azure.ai.ml.entities import (
    Component,
    CommandComponent,
    ResourceConfiguration,
    CommandJobLimits,
    Environment,
    CommandJob,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ResourceConfiguration as RestResourceConfiguration,
)
from azure.ai.ml.entities._job.sweep.early_termination_policy import EarlyTerminationPolicy
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution
from .._job.pipeline._io import PipelineInput, PipelineOutputBase
from .._util import validate_attribute_type, get_rest_dict
from azure.ai.ml.entities._job.distribution import (
    MpiDistribution,
    TensorFlowDistribution,
    PyTorchDistribution,
    DistributionConfiguration,
)
from ..._schema.job.distribution import PyTorchDistributionSchema, TensorFlowDistributionSchema, MPIDistributionSchema
from azure.ai.ml._ml_exceptions import ValidationException, ErrorTarget

module_logger = logging.getLogger(__name__)


class Command(BaseNode):
    """Base class for command node, used for command component version consumption.

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
        inputs: Dict[str, Union[PipelineInput, PipelineOutputBase, Input, str, bool, int, float, Enum, "Input"]] = None,
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

        self._init = True
        kwargs.pop("type", None)
        _from_component_func = kwargs.pop("_from_component_func", False)
        super(Command, self).__init__(type=NodeType.COMMAND, component=component, compute=compute, **kwargs)

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

        # initialize io
        inputs, outputs = inputs or {}, outputs or {}
        # when command node is constructed inside dsl.pipeline, inputs can be PipelineInput or Output of another node
        supported_input_types = (
            PipelineInput,
            PipelineOutputBase,
            Input,
            SweepDistribution,
            str,
            bool,
            int,
            float,
            Enum,
        )
        self._validate_io(inputs, supported_input_types, Input)
        supported_output_types = (str, Output)
        self._validate_io(outputs, supported_output_types, Output)
        # parse empty dict to None so we won't pass default mode, type to backend
        for k, v in inputs.items():
            if v == {}:
                inputs[k] = None
        # TODO: get rid of self._job_inputs, self._job_outputs once we have unified Input
        self._job_inputs, self._job_outputs = inputs, outputs
        if isinstance(component, Component):
            # Build the inputs from component input definition and given inputs, unfilled inputs will be None
            self._inputs = self._build_inputs_dict(component.inputs, inputs or {})
            # Build the outputs from component output definition and given outputs, unfilled outputs will be None
            self._outputs = self._build_outputs_dict(component.outputs, outputs or {})
        else:
            # Build inputs/outputs dict without meta when definition not available
            self._inputs = self._build_inputs_dict_without_meta(inputs or {})
            self._outputs = self._build_outputs_dict_without_meta(outputs or {})

        # Generate an id for every component instance
        self._instance_id = str(uuid.uuid4())
        if _from_component_func:
            # add current component in pipeline stack for dsl scenario
            self._register_in_current_pipeline_component_builder()

        self._swept = False
        self._init = False

    @property
    def distribution(self) -> Union[PyTorchDistribution, MpiDistribution, TensorFlowDistribution]:
        return self._distribution

    @distribution.setter
    def distribution(self, value):
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
    def resources(self, value):
        if isinstance(value, dict):
            value = ResourceConfiguration(**value)
        self._resources = value

    @property
    def component(self) -> Union[str, CommandComponent]:
        return self._component

    @property
    def command(self) -> str:
        return self.component.command

    @property
    def code(self) -> Optional[Union[str, PathLike]]:
        return self.component.code

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
        """Turn the command into a sweep node with extra sweep run setting. The command component in current Command
        node will be used as its trial component.
        A command node can sweep for multiple times, and the generated sweep node will share the same trial component.

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
            trial=self.component,
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

    def _initializing(self) -> bool:
        # use this to indicate ongoing init process so all attributes set during init process won't be set as
        # arbitrary attribute in _AttrDict
        # TODO: replace this hack
        return self._init

    @classmethod
    def _validate_io(cls, io_dict: dict, allowed_types: tuple, parse_cls):
        for key, value in io_dict.items():
            # output mode of last node should not affect input mode of next node
            if isinstance(value, PipelineOutputBase):
                # value = copy.deepcopy(value)
                value = value._deepcopy()  # Decoupled input and output
                io_dict[key] = value
                value.mode = None
            if value is None or isinstance(value, allowed_types):
                pass
            elif isinstance(value, dict):
                # parse dict to allowed type
                io_dict[key] = parse_cls(**value)
            else:
                msg = "Expecting {} for input/output {}, got {} instead."
                raise ValidationException(
                    message=msg.format(allowed_types, key, type(value)),
                    no_personal_data_message=msg.format(allowed_types, "[key]", type(value)),
                    target=ErrorTarget.COMMAND_JOB,
                )

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
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            properties=self.properties,
            command=self.component.command,
            experiment_name=self.experiment_name,
            code=self.component.code,
            compute=self.compute,
            environment=self.environment,
            distribution=self.distribution,
            identity=self.identity,
            environment_variables=self.environment_variables,
            resources=self.resources,
            limits=self.limits,
            inputs=self._job_inputs,
            outputs=self._job_outputs,
        )

    @classmethod
    def _picked_fields_in_to_rest(cls) -> List[str]:
        return ["resources", "distribution", "limits", "environment_variables"]

    def _node_specified_pre_to_rest_operations(self, rest_obj):
        for key in self._picked_fields_in_to_rest():
            if key not in rest_obj:
                rest_obj[key] = None

        rest_obj.update(
            dict(
                componentId=self._get_component_id(),
                distribution=get_rest_dict(self.distribution),
                limits=get_rest_dict(self.limits),
                resources=get_rest_dict(self.resources, clear_empty_value=True),
                **self._get_attrs(),
            )
        )

    @classmethod
    def _from_rest_object(cls, obj: dict) -> "Command":
        inputs = obj.get("inputs", {})
        outputs = obj.get("outputs", {})

        obj["inputs"] = cls._from_rest_inputs(inputs)
        obj["outputs"] = cls._from_rest_outputs(outputs)

        # resources
        if "resources" in obj and obj["resources"]:
            resources = RestResourceConfiguration.from_dict(obj["resources"])
            obj["resources"] = ResourceConfiguration._from_rest_object(resources)

        # Change componentId -> component, computeId -> compute
        component_id = obj.pop("componentId", None)
        compute_id = obj.pop("computeId", None)
        obj["component"] = component_id
        obj["compute"] = compute_id

        # distribution
        if "distribution" in obj and obj["distribution"]:
            obj["distribution"] = DistributionConfiguration._from_rest_object(obj["distribution"])
        # handle limits
        if "limits" in obj and obj["limits"]:
            rest_limits = RestCommandJobLimits.from_dict(obj["limits"])
            obj["limits"] = CommandJobLimits()._from_rest_object(rest_limits)
        return Command(**obj)

    def _build_inputs(self):
        inputs = super(Command, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value
        return built_inputs

    @classmethod
    def _get_schema(cls):
        from azure.ai.ml._schema.pipeline import CommandSchema

        return CommandSchema(context={BASE_PATH_CONTEXT_KEY: "./"})

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
                # get outputs
            for name, original_output in self.outputs.items():
                # use setattr here to make sure owner of input won't change
                setattr(node.outputs, name, original_output._data)
            # set default values: compute, environment_variables, outputs
            node._name = self.name
            node.compute = self.compute
            node.tags = self.tags
            node.display_name = self.display_name
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

    @property
    def _extra_skip_fields_in_validation(self) -> List[str]:
        """
        Extra fields that should be skipped in validation.
        """
        return ["component"]
