# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

import logging
from typing import Dict, List, Optional, Union

import pydash
from marshmallow import EXCLUDE, Schema

from azure.ai.ml._schema._sweep.sweep_fields_provider import EarlyTerminationField
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.constants._job.sweep import SearchSpace
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._credentials import (
    AmlTokenConfiguration,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.job_limits import SweepJobLimits
from azure.ai.ml.entities._job.pipeline._io import NodeInput
from azure.ai.ml.entities._job.queue_settings import QueueSettings
from azure.ai.ml.entities._job.sweep.early_termination_policy import (
    BanditPolicy,
    EarlyTerminationPolicy,
    MedianStoppingPolicy,
    TruncationSelectionPolicy,
)
from azure.ai.ml.entities._job.sweep.objective import Objective
from azure.ai.ml.entities._job.sweep.parameterized_sweep import ParameterizedSweep
from azure.ai.ml.entities._job.sweep.sampling_algorithm import SamplingAlgorithm
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
from azure.ai.ml.exceptions import ErrorTarget, UserErrorException, ValidationErrorType, ValidationException
from azure.ai.ml.sweep import SweepJob

from ..._schema import PathAwareSchema
from ..._schema._utils.data_binding_expression import support_data_binding_expression_for_fields
from ..._utils.utils import camel_to_snake
from .base_node import BaseNode

module_logger = logging.getLogger(__name__)


class Sweep(ParameterizedSweep, BaseNode):
    """Base class for sweep node, used for command component version
    consumption.

    You should not instantiate this class directly. Instead, you should
    create from builder function: sweep.

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
    :type early_termination_policy: Union[
    ~azure.mgmt.machinelearningservices.models.BanditPolicy,
    ~azure.mgmt.machinelearningservices.models.MedianStoppingPolicy,
    ~azure.mgmt.machinelearningservices.models.TruncationSelectionPolicy]
    :param search_space: hyperparameter search space to run trials.
    :type search_space: Dict[str, Union[~azure.ai.ml.entities.Choice,
    ~azure.ai.ml.entities.LogNormal,
    ~azure.ai.ml.entities.LogUniform,
    ~azure.ai.ml.entities.Normal,
    ~azure.ai.ml.entities.QLogNormal,
    ~azure.ai.ml.entities.QLogUniform,
    ~azure.ai.ml.entities.QNormal,
    ~azure.ai.ml.entities.QUniform,
    ~azure.ai.ml.entities.Randint,
    ~azure.ai.ml.entities.Uniform]]
    :param inputs: Inputs to the command.
    :type inputs: Dict[str, Union[Input, str, bool, int, float]]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Dict[str, Union[str, Output]]
    :param identity: Identity that training job will use while running on compute.
    :type identity: Union[
        ManagedIdentityConfiguration,
        AmlTokenConfiguration,
        UserIdentityConfiguration]
    :param queue_settings: Queue settings for the job.
    :type queue_settings: QueueSettings
    """

    def __init__(
        self,
        *,
        trial: Optional[Union[CommandComponent, str]] = None,
        compute: Optional[str] = None,
        limits: Optional[SweepJobLimits] = None,
        sampling_algorithm: Optional[Union[str, SamplingAlgorithm]] = None,
        objective: Optional[Objective] = None,
        early_termination: Optional[Union[BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy]] = None,
        search_space: Optional[
            Dict[
                str,
                Union[
                    Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform
                ],
            ]
        ] = None,
        inputs: Optional[Dict[str, Union[Input, str, bool, int, float]]] = None,
        outputs: Optional[Dict[str, Union[str, Output]]] = None,
        identity: Optional[
            Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
        queue_settings: Optional[QueueSettings] = None,
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
            queue_settings=queue_settings,
        )

        self.identity = identity
        self._init = False

    @property
    def trial(self):
        """Id or instance of the command component/job to be run for the step."""
        return self._component

    @property
    def search_space(self):
        """Dictionary of the hyperparameter search space.
        The key is the name of the hyperparameter and the value is the parameter expression.
        """
        return self._search_space

    @search_space.setter
    def search_space(self, values: Dict[str, Dict[str, Union[str, int, float, dict]]]):
        search_space = {}
        for name, value in values.items():
            # If value is a SearchSpace object, directly pass it to job.search_space[name]
            search_space[name] = self._value_type_to_class(value) if isinstance(value, dict) else value
        self._search_space = search_space

    @classmethod
    def _value_type_to_class(cls, value):
        value_type = value["type"]
        search_space_dict = {
            SearchSpace.CHOICE: Choice,
            SearchSpace.RANDINT: Randint,
            SearchSpace.LOGNORMAL: LogNormal,
            SearchSpace.NORMAL: Normal,
            SearchSpace.LOGUNIFORM: LogUniform,
            SearchSpace.UNIFORM: Uniform,
            SearchSpace.QLOGNORMAL: QLogNormal,
            SearchSpace.QNORMAL: QNormal,
            SearchSpace.QLOGUNIFORM: QLogUniform,
            SearchSpace.QUNIFORM: QUniform,
        }
        return search_space_dict[value_type](**value)

    @classmethod
    def _get_supported_inputs_types(cls):
        supported_types = super()._get_supported_inputs_types() or ()
        return (
            SweepDistribution,
            *supported_types,
        )

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "Sweep":
        raise NotImplementedError("Sweep._load_from_dict is not supported")

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return [
            "limits",
            "sampling_algorithm",
            "objective",
            "early_termination",
            "search_space",
            "queue_settings",
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
            rest_obj["early_termination"] = self.early_termination._to_rest_object().as_dict()

        rest_obj.update(
            {
                "type": self.type,
                "trial": self._get_trial_component_rest_obj(),
            }
        )
        return rest_obj

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: dict) -> Dict:
        obj = super()._from_rest_object_to_init_params(obj)

        # hack: only early termination policy does not follow yaml schema now, should be removed after server-side made
        # the change
        if "early_termination" in obj and "policy_type" in obj["early_termination"]:
            # can't use _from_rest_object here, because obj is a dict instead of an EarlyTerminationPolicy rest object
            obj["early_termination"]["type"] = camel_to_snake(obj["early_termination"].pop("policy_type"))

        # TODO: use cls._get_schema() to load from rest object
        from azure.ai.ml._schema._sweep.parameterized_sweep import ParameterizedSweepSchema

        schema = ParameterizedSweepSchema(context={BASE_PATH_CONTEXT_KEY: "./"})
        support_data_binding_expression_for_fields(schema, ["type", "component", "trial"])

        base_sweep = schema.load(obj, unknown=EXCLUDE, partial=True)  # pylint: disable=no-member
        for key, value in base_sweep.items():
            obj[key] = value

        # trial
        trial_component_id = pydash.get(obj, "trial.componentId", None)
        obj["trial"] = trial_component_id  # check this

        return obj

    def _get_trial_component_rest_obj(self):
        # trial component to rest object is different from usual component
        trial_component_id = self._get_component_id()
        if trial_component_id is None:
            return None
        if isinstance(trial_component_id, str):
            return {"componentId": trial_component_id}
        if isinstance(trial_component_id, CommandComponent):
            return trial_component_id._to_rest_object()
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
            queue_settings=self.queue_settings,
        )

    @classmethod
    def _get_component_attr_name(cls):
        return "trial"

    def _build_inputs(self):
        inputs = super(Sweep, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value

        return built_inputs

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline.component_job import SweepSchema

        return SweepSchema(context=context)

    @classmethod
    def _get_origin_inputs_and_search_space(cls, built_inputs: Dict[str, NodeInput]):
        """Separate mixed true inputs & search space definition from inputs of
        this node and return them.

        Input will be restored to Input/LiteralInput before returned.
        """
        search_space: Dict[
            str,
            Union[Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform],
        ] = {}
        inputs: Dict[str, Union[Input, str, bool, int, float]] = {}
        if built_inputs is not None:
            for input_name, input_obj in built_inputs.items():
                if isinstance(input_obj, NodeInput):
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
                        error_type=ValidationErrorType.INVALID_VALUE,
                    )
        return inputs, search_space

    def _is_input_set(self, input_name: str) -> bool:
        if super(Sweep, self)._is_input_set(input_name):
            return True
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

    @property
    def early_termination(self) -> Union[str, EarlyTerminationPolicy]:
        return self._early_termination

    @early_termination.setter
    def early_termination(self, value: Union[EarlyTerminationPolicy, Dict[str, Union[str, float, int, bool]]]):
        if isinstance(value, dict):
            early_termination_schema = EarlyTerminationField()
            value = early_termination_schema._deserialize(value=value, attr=None, data=None)
        self._early_termination = value
