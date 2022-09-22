# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Dict, List, Union

import pydash
from marshmallow import EXCLUDE, Schema

from azure.ai.ml._ml_exceptions import ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2022_02_01_preview.models import AmlToken, ManagedIdentity, UserIdentity
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, NodeType
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.job_limits import SweepJobLimits
from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException
from azure.ai.ml.entities._job.pipeline._io import PipelineInputBase
from azure.ai.ml.entities._job.sweep.early_termination_policy import BanditPolicy, EarlyTerminationPolicy
from azure.ai.ml.entities._job.sweep.objective import Objective
from azure.ai.ml.entities._job.sweep.parameterized_sweep import ParameterizedSweep
from azure.ai.ml.entities._job.sweep.sampling_algorithm import SamplingAlgorithm
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution
from azure.ai.ml.sweep import SweepJob

from ..._schema import PathAwareSchema
from ..._schema._utils.data_binding_expression import support_data_binding_expression_for_fields
from ..._utils.utils import camel_to_snake
from .base_node import BaseNode

module_logger = logging.getLogger(__name__)


class Sweep(ParameterizedSweep, BaseNode):
    """Base class for sweep node, used for command component version
    consumption.

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
        # TODO: get rid of self._job_inputs, self._job_outputs once we have general Input
        self._job_inputs, self._job_outputs = inputs, outputs

        kwargs.pop("type", None)
        BaseNode.__init__(
            self,
            type=NodeType.SWEEP,
            component=trial,
            inputs=inputs,
            outputs=outputs,
            compute=compute,
            **kwargs,
        )
        # init mark for _AttrDict
        self._init = True
        ParameterizedSweep.__init__(
            self,
            sampling_algorithm=sampling_algorithm,
            objective=objective,
            limits=limits,
            early_termination=early_termination,
            search_space=search_space,
        )

        self.identity = identity
        self._init = False

    @property
    def trial(self):
        return self._component

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return [
            "limits",
            "sampling_algorithm",
            "objective",
            "early_termination",
            "search_space",
        ]

    def _to_rest_object(self, **kwargs) -> dict:
        rest_obj = super(Sweep, self)._to_rest_object(**kwargs)
        # hack: ParameterizedSweep.early_termination is not allowed to be None
        for key in ["early_termination"]:
            if key in rest_obj and rest_obj[key] is None:
                del rest_obj[key]

        # hack: only early termination policy does not follow yaml schema now, should be removed after server-side made
        # the change
        if "early_termination" in rest_obj:
            rest_obj["early_termination"] = self.early_termination._to_rest_object()

        rest_obj.update(
            dict(
                type=self.type,
                trial=self._get_trial_component_rest_obj(),
            )
        )
        return rest_obj

    @classmethod
    def _from_rest_object(cls, obj: dict) -> "Sweep":
        obj = BaseNode._rest_object_to_init_params(obj)

        # hack: only early termination policy does not follow yaml schema now, should be removed after server-side made
        # the change
        if "early_termination" in obj and "policy_type" in obj["early_termination"]:
            # can't use _from_rest_object here, because obj is a dict instead of an EarlyTerminationPolicy rest object
            obj["early_termination"]["type"] = camel_to_snake(obj["early_termination"].pop("policy_type"))

        # TODO: use cls._get_schema() to load from rest object
        from azure.ai.ml._schema._sweep.parameterized_sweep import ParameterizedSweepSchema

        schema = ParameterizedSweepSchema(context={BASE_PATH_CONTEXT_KEY: "./"})
        support_data_binding_expression_for_fields(schema, ["type"])

        base_sweep = schema.load(obj, unknown=EXCLUDE, partial=True)
        for key, value in base_sweep.items():
            obj[key] = value

        # trial
        trial_component_id = pydash.get(obj, "trial.componentId", None)
        obj["trial"] = trial_component_id  # check this

        return Sweep(**obj)

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
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline.component_job import SweepSchema

        return SweepSchema(context=context)

    @classmethod
    def _get_origin_inputs_and_search_space(cls, built_inputs: Dict[str, PipelineInputBase]):
        """Separate mixed true inputs & search space definition from inputs of
        this node and return them.

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

    def __setattr__(self, key, value):
        super(Sweep, self).__setattr__(key, value)
        if key == "early_termination" and isinstance(self.early_termination, BanditPolicy):
            # only one of slack_amount and slack_factor can be specified but default value is 0.0.
            # Need to keep track of which one is null.
            if self.early_termination.slack_amount == 0.0:
                self.early_termination.slack_amount = None
            if self.early_termination.slack_factor == 0.0:
                self.early_termination.slack_factor = None
