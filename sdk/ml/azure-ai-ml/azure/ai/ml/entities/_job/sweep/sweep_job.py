# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Any, Dict, Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, JobException
from azure.ai.ml._restclient.v2022_02_01_preview.models import AmlToken, JobBaseData, ManagedIdentity
from azure.ai.ml._restclient.v2022_02_01_preview.models import SweepJob as RestSweepJob
from azure.ai.ml._restclient.v2022_02_01_preview.models import TrialComponent, UserIdentity
from azure.ai.ml._schema._sweep.sweep_job import SweepJobSchema
from azure.ai.ml._utils.utils import map_single_brackets_and_warn
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, TYPE, JobType
from azure.ai.ml.entities._job.command_job import CommandJob
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    to_rest_dataset_literal_inputs,
    validate_inputs_for_command,
    validate_key_contains_allowed_characters,
)
from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin
from azure.ai.ml.entities._job.sweep.sampling_algorithm import SamplingAlgorithm
from azure.ai.ml.entities._util import load_from_dict

from ..job_limits import SweepJobLimits
from ..parameterized_command import ParameterizedCommand
from .early_termination_policy import EarlyTerminationPolicy
from .objective import Objective
from .parameterized_sweep import ParameterizedSweep
from .search_space import SweepDistribution

module_logger = logging.getLogger(__name__)


class SweepJob(Job, ParameterizedSweep, JobIOMixin):
    """Sweep job for hyperparameter tuning.

    :param name: Name of the job.
    :type name: str
    :param display_name: Display name of the job.
    :type display_name: str
    :param description: Description of the job.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param experiment_name:  Name of the experiment the job will be created under, if None is provided, job will be created under experiment 'Default'.
    :type experiment_name: str
    :param identity: Identity that training job will use while running on compute.
    :type identity: Union[azure.ai.ml.ManagedIdentity, azure.ai.ml.AmlToken, azure.ai.ml.UserIdentity]
    :param inputs: Inputs to the command.
    :type inputs: dict
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: dict[str, azure.ai.ml.Output]
    :param sampling_algorithm: The hyperparameter sampling algorithm to use over the `search_space`. Defaults to "random".
    :type sampling_algorithm: str
    :param search_space: Dictionary of the hyperparameter search space. The key is the name of the hyperparameter and the value is the parameter expression.
    :type search_space: Dict
    :param objective: Metric to optimize for.
    :type objective: Objective
    :param compute: The compute target the job runs on.
    :type compute: str
    :param trial: The job configuration for each trial. Each trial will be provided with a different combination of hyperparameter values that the system samples from the search_space.
    :type trial: Union[azure.ai.ml.entities.CommandJob, azure.ai.ml.entities.CommandComponent]
    :param early_termination: The early termination policy to use. A trial job is canceled when the criteria of the specified policy are met. If omitted, no early termination policy will be applied.
    :type early_termination: EarlyTerminationPolicy
    :param limits: Limits for the sweep job.
    :type limits: ~azure.ai.ml.entities.SweepJobLimits
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str = None,
        description: str = None,
        tags: Dict = None,
        display_name: str = None,
        experiment_name: str = None,
        identity: Union[ManagedIdentity, AmlToken, UserIdentity] = None,
        inputs: Dict[str, Union[Input, str, bool, int, float]] = None,
        outputs: Dict[str, Output] = None,
        compute: str = None,
        limits: SweepJobLimits = None,
        sampling_algorithm: Union[str, SamplingAlgorithm] = None,
        search_space: Dict[str, SweepDistribution] = None,
        objective: Objective = None,
        trial: Union[CommandJob, CommandComponent] = None,
        early_termination: EarlyTerminationPolicy = None,
        **kwargs: Any,
    ):
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
        self.inputs = inputs
        self.outputs = outputs
        self.trial = trial
        self.identity = identity

        ParameterizedSweep.__init__(
            self,
            limits=limits,
            sampling_algorithm=sampling_algorithm,
            objective=objective,
            early_termination=early_termination,
            search_space=search_space,
        )

    def _to_dict(self) -> Dict:
        return SweepJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_rest_object(self) -> JobBaseData:
        self._override_missing_properties_from_trial()
        self.trial.command = map_single_brackets_and_warn(self.trial.command)
        search_space = {param: space._to_rest_object() for (param, space) in self.search_space.items()}

        validate_inputs_for_command(self.trial.command, self.inputs)
        for key in search_space.keys():
            validate_key_contains_allowed_characters(key)

        trial_component = TrialComponent(
            code_id=self.trial.code,
            environment_id=self.trial.environment,
            command=self.trial.command,
            environment_variables=self.trial.environment_variables,
            resources=self.trial.resources._to_rest_object() if self.trial.resources else None,
        )

        sweep_job = RestSweepJob(
            display_name=self.display_name,
            description=self.description,
            experiment_name=self.experiment_name,
            search_space=search_space,
            sampling_algorithm=self._get_rest_sampling_algorithm(),
            limits=self.limits._to_rest_object() if self.limits else None,
            early_termination=self.early_termination,
            properties=self.properties,
            compute_id=self.compute,
            objective=self.objective,
            trial=trial_component,
            tags=self.tags,
            inputs=to_rest_dataset_literal_inputs(self.inputs),
            outputs=to_rest_data_outputs(self.outputs),
            identity=self.identity,
        )
        sweep_job_resource = JobBaseData(properties=sweep_job)
        sweep_job_resource.name = self.name
        return sweep_job_resource

    def _to_component(self, context: Dict = None, **kwargs):
        msg = "no sweep component entity"
        raise JobException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.SWEEP_JOB,
            error_category=ErrorCategory.USER_ERROR,
        )

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "SweepJob":
        loaded_schema = load_from_dict(SweepJobSchema, data, context, additional_message, **kwargs)
        loaded_schema["trial"] = ParameterizedCommand(**(loaded_schema["trial"]))
        sweep_job = SweepJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_schema)
        return sweep_job

    @classmethod
    def _load_from_rest(cls, obj: JobBaseData) -> "SweepJob":
        properties: RestSweepJob = obj.properties

        # Unpack termination schema
        early_termination = EarlyTerminationPolicy._from_rest_object(properties.early_termination)

        # Unpack sampling algorithm
        sampling_algorithm = SamplingAlgorithm._from_rest_object(properties.sampling_algorithm)

        trial = ParameterizedCommand._load_from_sweep_job(obj.properties)
        # Compute also appears in both layers of the yaml, but only one of the REST.
        # This should be a required field in one place, but cannot be if its optional in two

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
            creation_context=obj.system_data,
            trial=trial,
            compute=properties.compute_id,
            sampling_algorithm=sampling_algorithm,
            search_space={
                param: SweepDistribution._from_rest_object(dist) for (param, dist) in properties.search_space.items()
            },
            limits=SweepJobLimits._from_rest_object(properties.limits),
            early_termination=early_termination,
            objective=properties.objective,
            inputs=from_rest_inputs_to_dataset_literal(properties.inputs),
            outputs=from_rest_data_outputs(properties.outputs),
            identity=properties.identity,
        )

    def _override_missing_properties_from_trial(self):
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
            self.limits = SweepJobLimits(trial_timeout=self.trial.limits.timeout)
        elif has_trial_limits_timeout and not self.limits.trial_timeout:
            self.limits.trial_timeout = self.trial.limits.timeout
