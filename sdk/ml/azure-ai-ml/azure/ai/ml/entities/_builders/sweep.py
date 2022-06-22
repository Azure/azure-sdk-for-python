# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import uuid
from typing import Dict, Union, List

from marshmallow import Schema

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    JobInput as RestJobInput,
    JobOutput as RestJobOutput,
    AmlToken,
    ManagedIdentity,
    UserIdentity,
)
import pydash
from marshmallow.utils import EXCLUDE
from azure.ai.ml.constants import ComponentJobConstants, BASE_PATH_CONTEXT_KEY, NodeType
from azure.ai.ml._utils.utils import map_single_brackets_and_warn
from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException
from azure.ai.ml.entities._job.pipeline._io import PipelineInputBase
from azure.ai.ml.entities._job.sweep.early_termination_policy import EarlyTerminationPolicy
from azure.ai.ml.entities._job.sweep.objective import Objective
from azure.ai.ml.entities._job.sweep.parameterized_sweep import ParameterizedSweep
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution
from azure.ai.ml.entities._job._input_output_helpers import (
    to_rest_dataset_literal_inputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    from_rest_data_outputs,
    validate_inputs_for_command,
)
from azure.ai.ml.entities._job.pipeline._pipeline_job_helpers import (
    process_sdk_component_job_io,
    from_dict_to_rest_io,
)
from azure.ai.ml.entities import CommandComponent, Component
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.sweep import SweepJob
from azure.ai.ml.entities._job.sweep.sampling_algorithm import SamplingAlgorithm
from azure.ai.ml.entities._job.job_limits import SweepJobLimits
from .base_node import BaseNode
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget
from ..._schema import PathAwareSchema
from ..._utils._arm_id_utils import get_resource_name_from_arm_id_safe

module_logger = logging.getLogger(__name__)


class Sweep(ParameterizedSweep, BaseNode):
    """Base class for sweep node, used for command component version consumption.

    :param trial: Id or instance of the command component/job to be run for the step
    :type trial: Union[CommandComponent, str]
    :param compute: Compute definition containing the compute information for the step
    :type compute: str
    :param limits: limits in running the sweep node.
    :type limits: SweepJobLimits
    :param sampling_algorithm: sampling algorithm to sample inside search space
    :type sampling_algorithm: str, valid values: random, grid or bayesian
    :param objective: the objective used to pick target run with the local optimal hyperparameter in search space.
    :type objective: Objective
    :param early_termination_policy: early termination policy of the sweep node.
    :type early_termination_policy: EarlyTerminationPolicy
    :param search_space: hyperparameter search space to run trials.
    :type search_space: Dict[str, SweepDistribution]
    :param inputs: Inputs to the command.
    :type inputs: Dict[str, Union[Input, str, bool, int, float]]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Dict[str, Union[str, Output]]
    :param identity: Identity that training job will use while running on compute.
    :type identity: Union[ManagedIdentity, AmlToken, UserIdentity]
    """

    def __init__(
        self,
        *,
        trial: Union[CommandComponent, str] = None,
        compute: str = None,
        limits: SweepJobLimits = None,
        sampling_algorithm: Union[str, SamplingAlgorithm] = None,
        objective: Objective = None,
        early_termination: EarlyTerminationPolicy = None,
        search_space: Dict[str, SweepDistribution] = None,
        inputs: Dict[str, Union[Input, str, bool, int, float]] = None,
        outputs: Dict[str, Union[str, Output]] = None,
        identity: Union[ManagedIdentity, AmlToken, UserIdentity] = None,
        **kwargs,
    ):
        self._init = True

        # TODO: get rid of self._job_inputs, self._job_outputs once we have general Input
        self._job_inputs, self._job_outputs = inputs, outputs

        # initialize io
        if isinstance(trial, Component):
            # Build the inputs from component input definition and given inputs, unfilled inputs will be None
            self._inputs = self._build_inputs_dict(trial.inputs, inputs or {})
            # Build the outputs from component output definition and given outputs, unfilled outputs will be None
            self._outputs = self._build_outputs_dict(trial.outputs, outputs or {})
        else:
            # Build inputs/outputs dict without meta when definition not available
            self._inputs = self._build_inputs_dict_without_meta(inputs or {})
            self._outputs = self._build_outputs_dict_without_meta(outputs or {})

        kwargs.pop("type", None)
        _from_component_func = kwargs.pop("_from_component_func", False)
        BaseNode.__init__(self, type=NodeType.SWEEP, component=trial, compute=compute, **kwargs)
        ParameterizedSweep.__init__(
            self,
            sampling_algorithm=sampling_algorithm,
            objective=objective,
            limits=limits,
            early_termination=early_termination,
            search_space=search_space,
        )

        # Generate an id for every component instance
        self._instance_id = str(uuid.uuid4())
        if _from_component_func:
            # add current component in pipeline stack for dsl scenario
            self._register_in_current_pipeline_component_builder()
        self.identity = identity
        self._init = False

    @property
    def trial(self):
        return self._component

    def _initializing(self) -> bool:
        return self._init

    @classmethod
    def _picked_fields_in_to_rest(cls) -> List[str]:
        return ["limits", "sampling_algorithm", "objective", "early_termination", "search_space"]

    def _node_specified_pre_to_rest_operations(self, rest_obj):
        # trial
        self._override_missing_properties_from_trial()
        if isinstance(self.trial, CommandComponent):
            self.trial.command = map_single_brackets_and_warn(self.trial.command)
            validate_inputs_for_command(self.trial.command, {**self.inputs, **self.search_space})

        rest_obj.update(
            dict(
                type=self.type,
                trial=self._get_trial_component_rest_obj(),
            )
        )

    def _get_trial_component_rest_obj(self):
        # trial component to rest object is different from usual component
        trial_component_id = self._get_component_id()
        if trial_component_id is None:
            return None
        elif isinstance(trial_component_id, str):
            return dict(componentId=trial_component_id)
        elif isinstance(trial_component_id, CommandComponent):
            return trial_component_id._to_rest_object()
        else:
            raise UserErrorException(f"invalid trial in sweep node {self.name}: {str(self.trial)}")

    def _to_job(self) -> SweepJob:
        command = self.trial.command
        for key, _ in self.search_space.items():
            # Double curly brackets to escape
            command = command.replace(f"${{{{inputs.{key}}}}}", f"${{{{search_space.{key}}}}}")

        # TODO: raise exception when the trial is a pre-registered component
        if command != self.trial.command and isinstance(self.trial, CommandComponent):
            self.trial.command = command

        return SweepJob(
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            properties=self.properties,
            tags=self.tags,
            experiment_name=self.experiment_name,
            trial=self.trial,
            compute=self.compute,
            sampling_algorithm=self.sampling_algorithm,
            search_space=self.search_space,
            limits=self.limits,
            early_termination=self.early_termination,
            objective=self.objective,
            inputs=self._job_inputs,
            outputs=self._job_outputs,
            identity=self.identity,
        )

    @classmethod
    def _get_component_attr_name(cls):
        return "trial"

    @classmethod
    def _from_rest_object(cls, obj: dict) -> "Sweep":
        # TODO: use cls._get_schema() to load from rest object
        from azure.ai.ml._schema._sweep.parameterized_sweep import ParameterizedSweepSchema
        from ..._schema._utils.data_binding_expression import support_data_binding_expression_for_fields

        schema = ParameterizedSweepSchema(context={BASE_PATH_CONTEXT_KEY: "./"})
        support_data_binding_expression_for_fields(schema, ["type"])

        base_sweep = schema.load(obj, unknown=EXCLUDE)
        for key, value in base_sweep.items():
            obj[key] = value
        inputs = obj.get("inputs", {})
        outputs = obj.get("outputs", {})

        # JObject -> RestJobInput/RestJobOutput
        input_bindings, rest_inputs = from_dict_to_rest_io(inputs, RestJobInput, [ComponentJobConstants.INPUT_PATTERN])
        output_bindings, rest_outputs = from_dict_to_rest_io(
            outputs, RestJobOutput, [ComponentJobConstants.OUTPUT_PATTERN]
        )

        # RestJobInput/RestJobOutput -> JobInput/JobOutput
        dataset_literal_inputs = from_rest_inputs_to_dataset_literal(rest_inputs)
        data_outputs = from_rest_data_outputs(rest_outputs)

        obj["inputs"] = {**dataset_literal_inputs, **input_bindings}
        obj["outputs"] = {**data_outputs, **output_bindings}

        # Change computeId -> compute
        compute_id = obj.pop("computeId", None)
        obj["compute"] = get_resource_name_from_arm_id_safe(compute_id)

        # trial
        trial_component_id = pydash.get(obj, "trial.componentId", None)
        obj["trial"] = trial_component_id  # check this

        return Sweep(**obj)

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline.component_job import SweepSchema

        return SweepSchema(context=context)

    @classmethod
    def _get_origin_inputs_and_search_space(cls, built_inputs: Dict[str, PipelineInputBase]):
        """Separate mixed true inputs & search space definition from inputs of this node and return them.
        Input will be restored to Input/LiteralInput before returned.
        """
        search_space: Dict[str, SweepDistribution] = {}
        inputs: Dict[str, Union[Input, str, bool, int, float]] = {}
        if built_inputs is not None:
            for input_name, input_obj in built_inputs.items():
                if isinstance(input_obj, PipelineInputBase):
                    if isinstance(input_obj._data, SweepDistribution):
                        search_space[input_name] = input_obj._data
                    else:
                        inputs[input_name] = input_obj._data
                else:
                    msg = "unsupported built input type: {}: {}"
                    raise ValidationException(
                        message=msg.format(input_name, type(input_obj)),
                        no_personal_data_message=msg.format("[input_name]", type(input_obj)),
                        target=ErrorTarget.SWEEP_JOB,
                    )
        return inputs, search_space

    def _is_input_set(self, input_name: str) -> bool:
        if super(Sweep, self)._is_input_set(input_name):
            return True
        else:
            return self.search_space is not None and input_name in self.search_space
