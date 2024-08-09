# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Any, Dict, NoReturn, Optional, Union

from azure.ai.ml._restclient.v2023_08_01_preview.models import JobBase
from azure.ai.ml._restclient.v2023_08_01_preview.models import SweepJob as RestSweepJob
from azure.ai.ml._restclient.v2023_08_01_preview.models import TrialComponent
from azure.ai.ml._schema._sweep.sweep_job import SweepJobSchema
from azure.ai.ml._utils.utils import map_single_brackets_and_warn
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._credentials import (
    AmlTokenConfiguration,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
    _BaseJobIdentityConfiguration,
)
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    to_rest_dataset_literal_inputs,
    validate_inputs_for_command,
    validate_key_contains_allowed_characters,
)
from azure.ai.ml.entities._job.command_job import CommandJob
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin
from azure.ai.ml.entities._job.job_resource_configuration import JobResourceConfiguration
from azure.ai.ml.entities._job.sweep.sampling_algorithm import SamplingAlgorithm
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, JobException

# from ..identity import AmlToken, Identity, ManagedIdentity, UserIdentity
from ..job_limits import SweepJobLimits
from ..parameterized_command import ParameterizedCommand
from ..queue_settings import QueueSettings
from .early_termination_policy import (
    BanditPolicy,
    EarlyTerminationPolicy,
    MedianStoppingPolicy,
    TruncationSelectionPolicy,
)
from .objective import Objective
from .parameterized_sweep import ParameterizedSweep
from .search_space import (
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

module_logger = logging.getLogger(__name__)


class SweepJob(Job, ParameterizedSweep, JobIOMixin):
    """Sweep job for hyperparameter tuning.

    .. note::
        For sweep jobs, inputs, outputs, and parameters are accessible as environment variables using the prefix
        ``AZUREML_SWEEP_``. For example, if you have a parameter named "learning_rate", you can access it as
        ``AZUREML_SWEEP_learning_rate``.

    :keyword name: Name of the job.
    :paramtype name: str
    :keyword display_name: Display name of the job.
    :paramtype display_name: str
    :keyword description: Description of the job.
    :paramtype description: str
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated.
    :paramtype tags: dict[str, str]
    :keyword properties: The asset property dictionary.
    :paramtype properties: dict[str, str]
    :keyword experiment_name:  Name of the experiment the job will be created under. If None is provided,
        job will be created under experiment 'Default'.
    :paramtype experiment_name: str
    :keyword identity: Identity that the training job will use while running on compute.
    :paramtype identity: Union[
        ~azure.ai.ml.ManagedIdentityConfiguration,
        ~azure.ai.ml.AmlTokenConfiguration,
        ~azure.ai.ml.UserIdentityConfiguration

    ]

    :keyword inputs: Inputs to the command.
    :paramtype inputs: dict
    :keyword outputs: Mapping of output data bindings used in the job.
    :paramtype outputs: dict[str, ~azure.ai.ml.Output]
    :keyword sampling_algorithm: The hyperparameter sampling algorithm to use over the `search_space`. Defaults to
        "random".

    :paramtype sampling_algorithm: str
    :keyword search_space: Dictionary of the hyperparameter search space. The key is the name of the hyperparameter
        and the value is the parameter expression.

    :paramtype search_space: Dict
    :keyword objective: Metric to optimize for.
    :paramtype objective: Objective
    :keyword compute: The compute target the job runs on.
    :paramtype compute: str
    :keyword trial: The job configuration for each trial. Each trial will be provided with a different combination
        of hyperparameter values that the system samples from the search_space.

    :paramtype trial: Union[
        ~azure.ai.ml.entities.CommandJob,
        ~azure.ai.ml.entities.CommandComponent

    ]

    :keyword early_termination: The early termination policy to use. A trial job is canceled
        when the criteria of the specified policy are met. If omitted, no early termination policy will be applied.

    :paramtype early_termination:  Union[
        ~azure.mgmt.machinelearningservices.models.BanditPolicy,
        ~azure.mgmt.machinelearningservices.models.MedianStoppingPolicy,
        ~azure.mgmt.machinelearningservices.models.TruncationSelectionPolicy

    ]

    :keyword limits: Limits for the sweep job.
    :paramtype limits: ~azure.ai.ml.entities.SweepJobLimits
    :keyword queue_settings: Queue settings for the job.
    :paramtype queue_settings: ~azure.ai.ml.entities.QueueSettings
    :keyword resources: Compute Resource configuration for the job.
    :paramtype resources: Optional[Union[~azure.ai.ml.entities.ResourceConfiguration]
    :keyword kwargs: A dictionary of additional configuration parameters.
    :paramtype kwargs: dict


    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_sweep_configurations.py
            :start-after: [START configure_sweep_job_bayesian_sampling_algorithm]
            :end-before: [END configure_sweep_job_bayesian_sampling_algorithm]
            :language: python
            :dedent: 8
            :caption: Creating a SweepJob
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        display_name: Optional[str] = None,
        experiment_name: Optional[str] = None,
        identity: Optional[
            Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
        inputs: Optional[Dict[str, Union[Input, str, bool, int, float]]] = None,
        outputs: Optional[Dict] = None,
        compute: Optional[str] = None,
        limits: Optional[SweepJobLimits] = None,
        sampling_algorithm: Optional[Union[str, SamplingAlgorithm]] = None,
        search_space: Optional[
            Dict[
                str,
                Union[
                    Choice, LogNormal, LogUniform, Normal, QLogNormal, QLogUniform, QNormal, QUniform, Randint, Uniform
                ],
            ]
        ] = None,
        objective: Optional[Objective] = None,
        trial: Optional[Union[CommandJob, CommandComponent]] = None,
        early_termination: Optional[
            Union[EarlyTerminationPolicy, BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy]
        ] = None,
        queue_settings: Optional[QueueSettings] = None,
        resources: Optional[Union[dict, JobResourceConfiguration]] = None,
        **kwargs: Any,
    ) -> None:
        kwargs[TYPE] = JobType.SWEEP

        Job.__init__(
            self,
            name=name,
            description=description,
            tags=tags,
            display_name=display_name,
            experiment_name=experiment_name,
            compute=compute,
            **kwargs,
        )
        self.inputs = inputs  # type: ignore[assignment]
        self.outputs = outputs  # type: ignore[assignment]
        self.trial = trial
        self.identity = identity

        ParameterizedSweep.__init__(
            self,
            limits=limits,
            sampling_algorithm=sampling_algorithm,
            objective=objective,
            early_termination=early_termination,
            search_space=search_space,
            queue_settings=queue_settings,
            resources=resources,
        )

    def _to_dict(self) -> Dict:
        res: dict = SweepJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)  # pylint: disable=no-member
        return res

    def _to_rest_object(self) -> JobBase:
        self._override_missing_properties_from_trial()
        if self.trial is not None:
            self.trial.command = map_single_brackets_and_warn(self.trial.command)

        if self.search_space is not None:
            search_space = {param: space._to_rest_object() for (param, space) in self.search_space.items()}

        if self.trial is not None:
            validate_inputs_for_command(self.trial.command, self.inputs)
        for key in search_space.keys():
            validate_key_contains_allowed_characters(key)

        if self.trial is not None:
            trial_component = TrialComponent(
                code_id=self.trial.code,
                distribution=(
                    self.trial.distribution._to_rest_object()
                    if self.trial.distribution and not isinstance(self.trial.distribution, Dict)
                    else None
                ),
                environment_id=self.trial.environment,
                command=self.trial.command,
                environment_variables=self.trial.environment_variables,
                resources=(
                    self.trial.resources._to_rest_object()
                    if self.trial.resources and not isinstance(self.trial.resources, Dict)
                    else None
                ),
            )

        sweep_job = RestSweepJob(
            display_name=self.display_name,
            description=self.description,
            experiment_name=self.experiment_name,
            search_space=search_space,
            sampling_algorithm=self._get_rest_sampling_algorithm() if self.sampling_algorithm else None,
            limits=self.limits._to_rest_object() if self.limits else None,
            early_termination=(
                self.early_termination._to_rest_object()
                if self.early_termination and not isinstance(self.early_termination, str)
                else None
            ),
            properties=self.properties,
            compute_id=self.compute,
            objective=self.objective._to_rest_object() if self.objective else None,
            trial=trial_component,
            tags=self.tags,
            inputs=to_rest_dataset_literal_inputs(self.inputs, job_type=self.type),
            outputs=to_rest_data_outputs(self.outputs),
            identity=self.identity._to_job_rest_object() if self.identity else None,
            queue_settings=self.queue_settings._to_rest_object() if self.queue_settings else None,
            resources=(
                self.resources._to_rest_object() if self.resources and not isinstance(self.resources, dict) else None
            ),
        )

        if not sweep_job.resources and sweep_job.trial.resources:
            sweep_job.resources = sweep_job.trial.resources

        sweep_job_resource = JobBase(properties=sweep_job)
        sweep_job_resource.name = self.name
        return sweep_job_resource

    def _to_component(self, context: Optional[Dict] = None, **kwargs: Any) -> NoReturn:
        msg = "no sweep component entity"
        raise JobException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.SWEEP_JOB,
            error_category=ErrorCategory.USER_ERROR,
        )

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "SweepJob":
        loaded_schema = load_from_dict(SweepJobSchema, data, context, additional_message, **kwargs)
        loaded_schema["trial"] = ParameterizedCommand(**(loaded_schema["trial"]))
        sweep_job = SweepJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_schema)
        return sweep_job

    @classmethod
    def _load_from_rest(cls, obj: JobBase) -> "SweepJob":
        properties: RestSweepJob = obj.properties

        # Unpack termination schema
        early_termination = EarlyTerminationPolicy._from_rest_object(properties.early_termination)

        # Unpack sampling algorithm
        sampling_algorithm = SamplingAlgorithm._from_rest_object(properties.sampling_algorithm)

        trial = ParameterizedCommand._load_from_sweep_job(obj.properties)
        # Compute also appears in both layers of the yaml, but only one of the REST.
        # This should be a required field in one place, but cannot be if its optional in two

        _search_space = {}
        for param, dist in properties.search_space.items():
            _search_space[param] = SweepDistribution._from_rest_object(dist)

        return SweepJob(
            name=obj.name,
            id=obj.id,
            display_name=properties.display_name,
            description=properties.description,
            properties=properties.properties,
            tags=properties.tags,
            experiment_name=properties.experiment_name,
            services=properties.services,
            status=properties.status,
            creation_context=SystemData._from_rest_object(obj.system_data) if obj.system_data else None,
            trial=trial,  # type: ignore[arg-type]
            compute=properties.compute_id,
            sampling_algorithm=sampling_algorithm,
            search_space=_search_space,  # type: ignore[arg-type]
            limits=SweepJobLimits._from_rest_object(properties.limits),
            early_termination=early_termination,
            objective=Objective._from_rest_object(properties.objective) if properties.objective else None,
            inputs=from_rest_inputs_to_dataset_literal(properties.inputs),
            outputs=from_rest_data_outputs(properties.outputs),
            identity=(
                _BaseJobIdentityConfiguration._from_rest_object(properties.identity) if properties.identity else None
            ),
            queue_settings=properties.queue_settings,
            resources=properties.resources if hasattr(properties, "resources") else None,
        )

    def _override_missing_properties_from_trial(self) -> None:
        if not isinstance(self.trial, CommandJob):
            return

        if not self.compute:
            self.compute = self.trial.compute
        if not self.inputs:
            self.inputs = self.trial.inputs
        if not self.outputs:
            self.outputs = self.trial.outputs

        has_trial_limits_timeout = self.trial.limits and self.trial.limits.timeout
        if has_trial_limits_timeout and not self.limits:
            time_out = self.trial.limits.timeout if self.trial.limits is not None else None
            self.limits = SweepJobLimits(trial_timeout=time_out)
        elif has_trial_limits_timeout and self.limits is not None and not self.limits.trial_timeout:
            self.limits.trial_timeout = self.trial.limits.timeout if self.trial.limits is not None else None
