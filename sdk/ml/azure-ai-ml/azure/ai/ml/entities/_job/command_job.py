# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
import logging
from pathlib import Path
from typing import Dict, Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2022_02_01_preview.models import AmlToken
from azure.ai.ml._restclient.v2022_02_01_preview.models import CommandJob as RestCommandJob
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobBaseData, ManagedIdentity, UserIdentity
from azure.ai.ml._schema.job.command_job import CommandJobSchema
from azure.ai.ml._utils.utils import map_single_brackets_and_warn
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, LOCAL_COMPUTE_PROPERTY, LOCAL_COMPUTE_TARGET, TYPE, JobType
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    to_rest_dataset_literal_inputs,
    validate_inputs_for_command,
)
from azure.ai.ml.entities._job.distribution import DistributionConfiguration
from azure.ai.ml.entities._util import load_from_dict

from .job import Job
from .job_io_mixin import JobIOMixin
from .job_limits import CommandJobLimits
from .parameterized_command import ParameterizedCommand
from .resource_configuration import ResourceConfiguration

module_logger = logging.getLogger(__name__)


class CommandJob(Job, ParameterizedCommand, JobIOMixin):
    """Command job.

    :param name: Name of the job.
    :type name: str
    :param description: Description of the job.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param display_name: Display name of the job.
    :type display_name: str
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param experiment_name:  Name of the experiment the job will be created under, if None is provided, default will be set to current directory name.
    :type experiment_name: str
    :param services: Information on services associated with the job, readonly.
    :type services: dict[str, JobService]
    :param inputs: Inputs to the command.
    :type inputs: dict[str, Union[azure.ai.ml.Input, str, bool, int, float]]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: dict[str, azure.ai.ml.Output]
    :param command: Command to be executed in training.
    :type command: str
    :param compute: The compute target the job runs on.
    :type compute: str
    :param resources: Compute Resource configuration for the job.
    :type resources: ~azure.ai.ml.entities.ResourceConfiguration
    :param code: A local path or http:, https:, azureml: url pointing to a remote location.
    :type code: str
    :param distribution: Distribution configuration for distributed training.
    :type distribution: Union[azure.ai.ml.PyTorchDistribution, azure.ai.ml.MpiDistribution, azure.ai.ml.TensorFlowDistribution]
    :param environment: Environment that training job will run in.
    :type environment: Union[azure.ai.ml.entities.Environment, str]
    :param identity: Identity that training job will use while running on compute.
    :type identity: Union[azure.ai.ml.ManagedIdentity, azure.ai.ml.AmlToken, azure.ai.ml.UserIdentity]
    :param limits: Command Job limit.
    :type limits: ~azure.ai.ml.entities.CommandJobLimits
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        inputs: Dict[str, Union[Input, str, bool, int, float]] = None,
        outputs: Dict[str, Union[Output]] = None,
        limits: CommandJobLimits = None,
        identity: Union[ManagedIdentity, AmlToken, UserIdentity] = None,
        **kwargs
    ):
        kwargs[TYPE] = JobType.COMMAND
        self._parameters = kwargs.pop("parameters", {})

        super().__init__(**kwargs)

        self.outputs = outputs
        self.inputs = inputs
        self.limits = limits
        self.identity = identity

    @property
    def parameters(self) -> Dict[str, str]:
        """MLFlow parameters.

        :return: MLFlow parameters logged in job.
        :rtype: Dict[str, str]
        """
        return self._parameters

    def _to_dict(self) -> Dict:
        return CommandJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_rest_object(self) -> JobBaseData:
        self._validate()
        self.command = map_single_brackets_and_warn(self.command)
        modified_properties = copy.deepcopy(self.properties)
        # Remove any properties set on the service as read-only
        modified_properties.pop("_azureml.ComputeTargetType", None)
        # Handle local compute case
        compute = self.compute
        resources = self.resources
        if self.compute == LOCAL_COMPUTE_TARGET:
            compute = None
            if resources is None:
                resources = ResourceConfiguration()
            if resources.properties is None:
                resources.properties = {}
            # This is the format of the October Api response. We need to match it exactly
            resources.properties[LOCAL_COMPUTE_PROPERTY] = {LOCAL_COMPUTE_PROPERTY: True}

        properties = RestCommandJob(
            display_name=self.display_name,
            description=self.description,
            command=self.command,
            code_id=self.code,
            compute_id=compute,
            properties=modified_properties,
            experiment_name=self.experiment_name,
            inputs=to_rest_dataset_literal_inputs(self.inputs),
            outputs=to_rest_data_outputs(self.outputs),
            environment_id=self.environment,
            distribution=self.distribution,
            tags=self.tags,
            identity=self.identity,
            environment_variables=self.environment_variables,
            resources=resources._to_rest_object() if resources else None,
            limits=self.limits._to_rest_object() if self.limits else None,
            services=self.services,
        )
        result = JobBaseData(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "CommandJob":
        loaded_data = load_from_dict(CommandJobSchema, data, context, additional_message, **kwargs)
        return CommandJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

    @classmethod
    def _load_from_rest(cls, obj: JobBaseData) -> "CommandJob":
        rest_command_job: RestCommandJob = obj.properties
        command_job = CommandJob(
            name=obj.name,
            id=obj.id,
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
            resources=ResourceConfiguration._from_rest_object(rest_command_job.resources),
            limits=CommandJobLimits._from_rest_object(rest_command_job.limits),
            inputs=from_rest_inputs_to_dataset_literal(rest_command_job.inputs),
            outputs=from_rest_data_outputs(rest_command_job.outputs),
        )
        # Handle special case of local job
        if (
            command_job.resources is not None
            and command_job.resources.properties is not None
            and command_job.resources.properties.get(LOCAL_COMPUTE_PROPERTY, None)
        ):
            command_job.compute = LOCAL_COMPUTE_TARGET
            command_job.resources.properties.pop(LOCAL_COMPUTE_PROPERTY)
        return command_job

    def _to_component(self, context: Dict = None, **kwargs):
        """Translate a command job to component.

        :param context: Context of command job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated command component.
        """
        from azure.ai.ml.entities import CommandComponent

        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        context = context or {BASE_PATH_CONTEXT_KEY: Path("./")}

        # Create anonymous command component with default version as 1
        return CommandComponent(
            tags=self.tags,
            is_anonymous=True,
            base_path=context[BASE_PATH_CONTEXT_KEY],
            code=self.code,
            command=self.command,
            environment=self.environment,
            description=self.description,
            inputs=self._to_inputs(inputs=self.inputs, pipeline_job_dict=pipeline_job_dict),
            outputs=self._to_outputs(outputs=self.outputs, pipeline_job_dict=pipeline_job_dict),
            resources=self.resources if self.resources else None,
            distribution=self.distribution if self.distribution else None,
        )

    def _to_node(self, context: Dict = None, **kwargs):
        """Translate a command job to a pipeline node.

        :param context: Context of command job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated command component.
        """
        from azure.ai.ml.entities._builders import Command

        component = self._to_component(context, **kwargs)

        return Command(
            component=component,
            compute=self.compute,
            # Need to supply the inputs with double curly.
            inputs=self.inputs,
            outputs=self.outputs,
            environment_variables=self.environment_variables,
            description=self.description,
            tags=self.tags,
            display_name=self.display_name,
            limits=self.limits,
        )

    def _validate(self) -> None:
        if self.compute is None:
            msg = "compute is required"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        if self.command is None:
            msg = "command is required"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        if self.environment is None:
            msg = "environment is required for non-local runs"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        validate_inputs_for_command(self.command, self.inputs)
