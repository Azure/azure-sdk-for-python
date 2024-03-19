# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

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
from azure.ai.ml.entities._job.job_resource_configuration import JobResourceConfiguration
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

from ..._restclient.v2022_10_01.models import ComponentVersion
from ..._schema import PathAwareSchema
from ..._schema._utils.data_binding_expression import support_data_binding_expression_for_fields
from ..._utils.utils import camel_to_snake
from .base_node import BaseNode

module_logger = logging.getLogger(__name__)


class Sweep(ParameterizedSweep, BaseNode):
    """Base class for sweep node.

    This class should not be instantiated directly. Instead, it should be created via the builder function: sweep.

    :param trial: The ID or instance of the command component or job to be run for the step.
    :type trial: Union[~azure.ai.ml.entities.CommandComponent, str]
    :param compute: The compute definition containing the compute information for the step.
    :type compute: str
    :param limits: The limits for the sweep node.
    :type limits: ~azure.ai.ml.sweep.SweepJobLimits
    :param sampling_algorithm: The sampling algorithm to use to sample inside the search space.
        Accepted values are: "random", "grid", or "bayesian".
    :type sampling_algorithm: str
    :param objective: The objective used to determine the target run with the local optimal
        hyperparameter in search space.
    :type objective: ~azure.ai.ml.sweep.Objective
    :param early_termination_policy: The early termination policy of the sweep node.
    :type early_termination_policy: Union[

        ~azure.mgmt.machinelearningservices.models.BanditPolicy,
        ~azure.mgmt.machinelearningservices.models.MedianStoppingPolicy,
        ~azure.mgmt.machinelearningservices.models.TruncationSelectionPolicy

    ]

    :param search_space: The hyperparameter search space to run trials in.
    :type search_space: Dict[str, Union[

        ~azure.ai.ml.entities.Choice,
        ~azure.ai.ml.entities.LogNormal,
        ~azure.ai.ml.entities.LogUniform,
        ~azure.ai.ml.entities.Normal,
        ~azure.ai.ml.entities.QLogNormal,
        ~azure.ai.ml.entities.QLogUniform,
        ~azure.ai.ml.entities.QNormal,
        ~azure.ai.ml.entities.QUniform,
        ~azure.ai.ml.entities.Randint,
        ~azure.ai.ml.entities.Uniform

    ]]

    :param inputs: Mapping of input data bindings used in the job.
    :type inputs: Dict[str, Union[

        ~azure.ai.ml.Input,

        str,
        bool,
        int,
        float

    ]]

    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Dict[str, Union[str, ~azure.ai.ml.Output]]
    :param identity: The identity that the training job will use while running on compute.
    :type identity: Union[

        ~azure.ai.ml.ManagedIdentityConfiguration,
        ~azure.ai.ml.AmlTokenConfiguration,
        ~azure.ai.ml.UserIdentityConfiguration

    ]

    :param queue_settings: The queue settings for the job.
    :type queue_settings: ~azure.ai.ml.entities.QueueSettings
    :param resources: Compute Resource configuration for the job.
    :type resources: Optional[Union[dict, ~azure.ai.ml.entities.ResourceConfiguration]]
    """

    def __init__(
        self,
        *,
        trial: Optional[Union[CommandComponent, str]] = None,
        compute: Optional[str] = None,
        limits: Optional[SweepJobLimits] = None,
        sampling_algorithm: Optional[Union[str, SamplingAlgorithm]] = None,
        objective: Optional[Objective] = None,
        early_termination: Optional[
            Union[BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy, EarlyTerminationPolicy, str]
        ] = None,
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
            Union[Dict, ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
        queue_settings: Optional[QueueSettings] = None,
        resources: Optional[Union[dict, JobResourceConfiguration]] = None,
        **kwargs: Any,
    ) -> None:
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
            resources=resources,
        )

        self.identity: Any = identity
        self._init = False

    @property
    def trial(self) -> CommandComponent:
        """The ID or instance of the command component or job to be run for the step.

        :rtype: ~azure.ai.ml.entities.CommandComponent
        """
        res: CommandComponent = self._component
        return res

    @property
    def search_space(
        self,
    ) -> Optional[
        Dict[
            str,
            Union[Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform],
        ]
    ]:
        """Dictionary of the hyperparameter search space.

        Each key is the name of a hyperparameter and its value is the parameter expression.

        :rtype: Dict[str, Union[~azure.ai.ml.entities.Choice, ~azure.ai.ml.entities.LogNormal,
            ~azure.ai.ml.entities.LogUniform, ~azure.ai.ml.entities.Normal, ~azure.ai.ml.entities.QLogNormal,
            ~azure.ai.ml.entities.QLogUniform, ~azure.ai.ml.entities.QNormal, ~azure.ai.ml.entities.QUniform,
            ~azure.ai.ml.entities.Randint, ~azure.ai.ml.entities.Uniform]]
        """
        return self._search_space

    @search_space.setter
    def search_space(self, values: Dict[str, Dict[str, Union[str, int, float, dict]]]) -> None:
        """Sets the search space for the sweep job.

        :param values: The search space to set.
        :type values: Dict[str, Dict[str, Union[str, int, float, dict]]]
        """
        search_space: Dict = {}
        for name, value in values.items():
            # If value is a SearchSpace object, directly pass it to job.search_space[name]
            search_space[name] = self._value_type_to_class(value) if isinstance(value, dict) else value
        self._search_space = search_space

    @classmethod
    def _value_type_to_class(cls, value: Any) -> Dict:
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

        res: dict = search_space_dict[value_type](**value)
        return res

    @classmethod
    def _get_supported_inputs_types(cls) -> Tuple:
        supported_types = super()._get_supported_inputs_types() or ()
        return (
            SweepDistribution,
            *supported_types,
        )

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "Sweep":
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
            "resources",
        ]

    def _to_rest_object(self, **kwargs: Any) -> dict:
        rest_obj: dict = super(Sweep, self)._to_rest_object(**kwargs)
        # hack: ParameterizedSweep.early_termination is not allowed to be None
        for key in ["early_termination"]:
            if key in rest_obj and rest_obj[key] is None:
                del rest_obj[key]

        # hack: only early termination policy does not follow yaml schema now, should be removed after server-side made
        # the change
        if "early_termination" in rest_obj:
            _early_termination: EarlyTerminationPolicy = self.early_termination  # type: ignore
            rest_obj["early_termination"] = _early_termination._to_rest_object().as_dict()

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

    def _get_trial_component_rest_obj(self) -> Union[Dict, ComponentVersion, None]:
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
        if self.search_space is not None:
            for key, _ in self.search_space.items():
                if command is not None:
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
            early_termination=self.early_termination,  # type: ignore[arg-type]
            objective=self.objective,
            inputs=self._job_inputs,
            outputs=self._job_outputs,
            identity=self.identity,
            queue_settings=self.queue_settings,
            resources=self.resources,
        )

    @classmethod
    def _get_component_attr_name(cls) -> str:
        return "trial"

    def _build_inputs(self) -> Dict:
        inputs = super(Sweep, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value

        return built_inputs

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline.component_job import SweepSchema

        return SweepSchema(context=context)

    @classmethod
    def _get_origin_inputs_and_search_space(cls, built_inputs: Optional[Dict[str, NodeInput]]) -> Tuple:
        """Separate mixed true inputs & search space definition from inputs of
        this node and return them.

        Input will be restored to Input/LiteralInput before returned.

        :param built_inputs: The built inputs
        :type built_inputs: Optional[Dict[str, NodeInput]]
        :return: A tuple of the inputs and search space
        :rtype: Tuple[
                Dict[str, Union[Input, str, bool, int, float]],
                Dict[str, SweepDistribution],
            ]
        """
        search_space: Dict = {}
        inputs: Dict = {}
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

    def __setattr__(self, key: Any, value: Any) -> None:
        super(Sweep, self).__setattr__(key, value)
        if key == "early_termination" and isinstance(self.early_termination, BanditPolicy):
            # only one of slack_amount and slack_factor can be specified but default value is 0.0.
            # Need to keep track of which one is null.
            if self.early_termination.slack_amount == 0.0:
                self.early_termination.slack_amount = None  # type: ignore[assignment]
            if self.early_termination.slack_factor == 0.0:
                self.early_termination.slack_factor = None  # type: ignore[assignment]

    @property
    def early_termination(self) -> Optional[Union[str, EarlyTerminationPolicy]]:
        """The early termination policy for the sweep job.

        :rtype: Union[str, ~azure.ai.ml.sweep.BanditPolicy, ~azure.ai.ml.sweep.MedianStoppingPolicy,
            ~azure.ai.ml.sweep.TruncationSelectionPolicy]
        """
        return self._early_termination

    @early_termination.setter
    def early_termination(self, value: Optional[Union[str, EarlyTerminationPolicy]]) -> None:
        """Sets the early termination policy for the sweep job.

        :param value: The early termination policy for the sweep job.
        :type value: Union[~azure.ai.ml.sweep.BanditPolicy, ~azure.ai.ml.sweep.MedianStoppingPolicy,
            ~azure.ai.ml.sweep.TruncationSelectionPolicy, dict[str, Union[str, float, int, bool]]]
        """
        if isinstance(value, dict):
            early_termination_schema = EarlyTerminationField()
            value = early_termination_schema._deserialize(value=value, attr=None, data=None)
        self._early_termination = value  # type: ignore[assignment]
