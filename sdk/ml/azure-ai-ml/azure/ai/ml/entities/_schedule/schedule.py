# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from os import PathLike
from pathlib import Path
from typing import Dict, Union

from azure.ai.ml._restclient.v2022_06_01_preview.models import JobBase as RestJobBase
from azure.ai.ml._restclient.v2022_06_01_preview.models import JobScheduleAction
from azure.ai.ml._restclient.v2022_06_01_preview.models import PipelineJob as RestPipelineJob_0601
from azure.ai.ml._restclient.v2022_06_01_preview.models import Schedule as RestSchedule
from azure.ai.ml._restclient.v2022_06_01_preview.models import ScheduleProperties
from azure.ai.ml._schema.schedule.schedule import ScheduleSchema
from azure.ai.ml._utils.utils import camel_to_snake, dump_yaml_to_file
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, JobType
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.pipeline.pipeline_job import PipelineJob
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._mixins import RestTranslatableMixin, TelemetryMixin, YamlTranslatableMixin
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities._validation import SchemaValidatableMixin

from ..._ml_exceptions import ErrorCategory, ErrorTarget, ScheduleException, ValidationException
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
        create_job = Job._load(
            data=data.pop(create_job_key),
            **kwargs,
        )
        schedule = JobSchedule(
            base_path=context[BASE_PATH_CONTEXT_KEY],
            **load_from_dict(ScheduleSchema, data, context, **kwargs),
            **{create_job_key: None},
        )
        schedule.create_job = create_job
        return schedule

    def dump(self, path: Union[PathLike, str]) -> None:
        """Dump the schedule content into a file in yaml format.

        :param path: Path to a local file as the target, new file will be created, raises exception if the file exists.
        :type path: str
        """

        yaml_serialized = self._to_dict()
        dump_yaml_to_file(path, yaml_serialized, default_flow_style=False)

    @classmethod
    def _create_schema_for_validation(cls, context):
        return ScheduleSchema(context=context)

    @classmethod
    def _from_rest_object(cls, obj: RestSchedule) -> "JobSchedule":
        properties = obj.properties
        action = properties.action
        create_job = None
        if isinstance(action, JobScheduleAction):
            if action.job_definition is None:
                msg = "Job definition for schedule '{}' can not be None."
                raise ScheduleException(
                    message=msg.format(obj.name),
                    no_personal_data_message=msg.format("[name]"),
                    target=ErrorTarget.JOB,
                    error_category=ErrorCategory.SYSTEM_ERROR,
                )
            elif camel_to_snake(action.job_definition.job_type) != JobType.PIPELINE:
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
            create_job.id = action.job_definition.source_job_id
            create_job = PipelineJob._load_from_rest(create_job, new_version=True)
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
            creation_context=obj.system_data,
        )

    def _to_rest_object(self) -> RestSchedule:
        """Build current parameterized schedule instance to a schedule object before submission.

        :return: Rest schedule.
        """
        if isinstance(self.create_job, PipelineJob):
            job_definition = self.create_job._to_rest_object(new_version=True).properties
        elif isinstance(self.create_job, str):  # arm id reference
            job_definition = RestPipelineJob_0601(source_job_id=self.create_job)
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
        except BaseException:
            return super(JobSchedule, self).__str__()

    def _get_telemetry_values(self):
        """Return the telemetry values of schedule."""
        return {"trigger_type": type(self.trigger).__name__}
