# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
import typing
from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, Union

from azure.ai.ml._restclient.v2022_10_01.models import JobBase as RestJobBase
from azure.ai.ml._restclient.v2022_10_01.models import JobScheduleAction
from azure.ai.ml._restclient.v2022_10_01.models import PipelineJob as RestPipelineJob
from azure.ai.ml._restclient.v2022_10_01.models import Schedule as RestSchedule
from azure.ai.ml._restclient.v2022_10_01.models import ScheduleProperties
from azure.ai.ml._schema.schedule.schedule import ScheduleSchema
from azure.ai.ml._utils.utils import camel_to_snake, dump_yaml_to_file, is_private_preview_enabled
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import ARM_ID_PREFIX, BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.pipeline.pipeline_job import PipelineJob
from azure.ai.ml.entities._mixins import RestTranslatableMixin, TelemetryMixin, YamlTranslatableMixin
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities._validation import SchemaValidatableMixin, MutableValidationResult
from .. import CommandJob, SparkJob
from .._builders import BaseNode

from ...exceptions import ErrorCategory, ErrorTarget, ScheduleException, ValidationException
from .trigger import CronTrigger, RecurrenceTrigger, TriggerBase


class JobSchedule(YamlTranslatableMixin, SchemaValidatableMixin, RestTranslatableMixin, Resource, TelemetryMixin):
    """JobSchedule object.

    :param name: Name of the schedule.
    :type name: str
    :param trigger: Trigger of the schedule.
    :type trigger: Union[CronTrigger, RecurrenceTrigger]
    :param create_job: The schedule action job definition.
    :type create_job: Job
    :param display_name: Display name of the schedule.
    :type display_name: str
    :param description: Description of the schedule, defaults to None
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The job property dictionary.
    :type properties: dict[str, str]
    """

    def __init__(
        self,
        *,
        name: str,
        trigger: Union[CronTrigger, RecurrenceTrigger],
        create_job: Job,
        display_name: str = None,
        description: str = None,
        tags: Dict = None,
        properties: Dict = None,
        **kwargs,
    ):
        is_enabled = kwargs.pop("is_enabled", None)
        provisioning_state = kwargs.pop("provisioning_state", None)
        super().__init__(name=name, description=description, tags=tags, properties=properties, **kwargs)
        self.trigger = trigger
        self.display_name = display_name
        self.create_job = create_job
        self._is_enabled = is_enabled
        self._provisioning_state = provisioning_state

    @property
    def is_enabled(self):
        """
        Return the schedule is enabled or not.

        :return: Enabled status.
        :rtype: bool
        """
        return self._is_enabled

    @property
    def provisioning_state(self):
        """
        Return the schedule's provisioning state. Possible values include:
        "Creating", "Updating", "Deleting", "Succeeded", "Failed", "Canceled".

        :return: Provisioning state.
        :rtype: str
        """
        return self._provisioning_state

    @classmethod
    def _load(
        cls,
        data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "JobSchedule":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return JobSchedule(
            base_path=context[BASE_PATH_CONTEXT_KEY],
            **load_from_dict(ScheduleSchema, data, context, **kwargs),
        )

    @classmethod
    def _load_from_rest_dict(
        cls,
        data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "JobSchedule":
        """
        Load job schedule from rest object dict.

        This function is added because the user-faced schema is different from the rest one.
        For example:
        user yaml create_job is a file reference with updates(not a job definition):
        create_job:
            job: ./job.yaml
            inputs:
                input: 10
        while what we get from rest will be a complete job definition:
        create_job:
            name: xx
            jobs:
                node1: ...
            inputs:
                input: ..
        """
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        create_job_key = "create_job"
        if create_job_key not in data:
            msg = "Job definition for schedule '{}' can not be None."
            raise ScheduleException(
                message=msg.format(data["name"]),
                no_personal_data_message=msg.format("[name]"),
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.SYSTEM_ERROR,
            )
        # Load the job definition separately
        create_job_data = data.pop(create_job_key)
        # Save the id for remote job reference before load job, as data dict will be changed
        job_id = create_job_data.get("id")
        if isinstance(job_id, str) and job_id.startswith(ARM_ID_PREFIX):
            job_id = job_id[len(ARM_ID_PREFIX) :]
        create_job = Job._load(
            data=create_job_data,
            **kwargs,
        )
        # Set id manually as it is a dump only field in schema
        create_job._id = job_id
        schedule = JobSchedule(
            base_path=context[BASE_PATH_CONTEXT_KEY],
            **load_from_dict(ScheduleSchema, data, context, **kwargs),
            **{create_job_key: None},
        )
        schedule.create_job = create_job
        return schedule

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the schedule content into a file in yaml format.

        :param dest: The destination to receive this schedule's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[str, PathLike, IO[AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    @classmethod
    def _create_schema_for_validation(cls, context):
        return ScheduleSchema(context=context)

    @classmethod
    def _get_validation_error_target(cls) -> ErrorTarget:
        return ErrorTarget.SCHEDULE

    def _customized_validate(self) -> MutableValidationResult:
        """Validate the resource with customized logic."""
        if isinstance(self.create_job, PipelineJob):
            return self.create_job._validate()
        return self._create_empty_validation_result()

    @classmethod
    def _get_skip_fields_in_schema_validation(cls) -> typing.List[str]:
        """Get the fields that should be skipped in schema validation.

        Override this method to add customized validation logic.
        """
        return ["create_job"]

    @classmethod
    def _from_rest_object(cls, obj: RestSchedule) -> "JobSchedule":
        properties = obj.properties
        action: JobScheduleAction = properties.action
        if action.job_definition is None:
            msg = "Job definition for schedule '{}' can not be None."
            raise ScheduleException(
                message=msg.format(obj.name),
                no_personal_data_message=msg.format("[name]"),
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.SYSTEM_ERROR,
            )
        if camel_to_snake(action.job_definition.job_type) not in [JobType.PIPELINE, JobType.COMMAND, JobType.SPARK]:
            msg = f"Unsupported job type {action.job_definition.job_type} for schedule '{{}}'."
            raise ScheduleException(
                message=msg.format(obj.name),
                no_personal_data_message=msg.format("[name]"),
                target=ErrorTarget.JOB,
                # Classified as user_error as we may support other type afterwards.
                error_category=ErrorCategory.USER_ERROR,
            )
        # Wrap job definition with JobBase for Job._from_rest_object call.
        create_job = RestJobBase(properties=action.job_definition)
        # id is a readonly field so set it after init.
        # TODO: Add this support after source job id move to JobBaseProperties
        if hasattr(action.job_definition, "source_job_id"):
            create_job.id = action.job_definition.source_job_id
        create_job = Job._from_rest_object(create_job)
        return cls(
            trigger=TriggerBase._from_rest_object(properties.trigger),
            create_job=create_job,
            name=obj.name,
            display_name=properties.display_name,
            description=properties.description,
            tags=properties.tags,
            properties=properties.properties,
            provisioning_state=properties.provisioning_state,
            is_enabled=properties.is_enabled,
            creation_context=SystemData._from_rest_object(obj.system_data),
        )

    def _to_rest_object(self) -> RestSchedule:
        """Build current parameterized schedule instance to a schedule object before submission.

        :return: Rest schedule.
        """
        if isinstance(self.create_job, BaseNode):
            self.create_job = self.create_job._to_job()
        private_enabled = is_private_preview_enabled()
        if isinstance(self.create_job, PipelineJob):
            job_definition = self.create_job._to_rest_object().properties
            # Set the source job id, as it is used only for schedule scenario.
            job_definition.source_job_id = self.create_job.id
        elif private_enabled and isinstance(self.create_job, (CommandJob, SparkJob)):
            job_definition = self.create_job._to_rest_object().properties
            # TODO: Merge this branch with PipelineJob after source job id move to JobBaseProperties
            # job_definition.source_job_id = self.create_job.id
        elif isinstance(self.create_job, str):  # arm id reference
            # TODO: Update this after source job id move to JobBaseProperties
            job_definition = RestPipelineJob(source_job_id=self.create_job)
        else:
            msg = "Unsupported job type '{}' in schedule {}."
            raise ValidationException(
                message=msg.format(type(self.create_job).__name__, self.name),
                no_personal_data_message=msg.format("[type]", "[name]"),
                target=ErrorTarget.SCHEDULE,
                error_category=ErrorCategory.USER_ERROR,
            )
        return RestSchedule(
            properties=ScheduleProperties(
                description=self.description,
                properties=self.properties,
                tags=self.tags,
                action=JobScheduleAction(job_definition=job_definition),
                display_name=self.display_name,
                is_enabled=self._is_enabled,
                trigger=self.trigger._to_rest_object(),
            )
        )

    def _to_dict(self) -> Dict:
        """Convert the resource to a dictionary."""
        return self._dump_for_validation()

    def __str__(self):
        try:
            return self._to_yaml()
        except BaseException:  # pylint: disable=broad-except
            return super(JobSchedule, self).__str__()

    def _get_telemetry_values(self, *args, **kwargs):
        """Return the telemetry values of schedule."""
        return {"trigger_type": type(self.trigger).__name__}
