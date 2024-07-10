# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access
import logging
import typing
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, List, Optional, Tuple, Union

from typing_extensions import Literal

from azure.ai.ml._restclient.v2023_06_01_preview.models import JobBase as RestJobBase
from azure.ai.ml._restclient.v2023_06_01_preview.models import JobScheduleAction
from azure.ai.ml._restclient.v2023_06_01_preview.models import PipelineJob as RestPipelineJob
from azure.ai.ml._restclient.v2023_06_01_preview.models import Schedule as RestSchedule
from azure.ai.ml._restclient.v2023_06_01_preview.models import ScheduleActionType as RestScheduleActionType
from azure.ai.ml._restclient.v2023_06_01_preview.models import ScheduleProperties
from azure.ai.ml._restclient.v2024_01_01_preview.models import TriggerRunSubmissionDto as RestTriggerRunSubmissionDto
from azure.ai.ml._schema.schedule.schedule import JobScheduleSchema
from azure.ai.ml._utils.utils import camel_to_snake, dump_yaml_to_file, is_private_preview_enabled
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import ARM_ID_PREFIX, BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, ScheduleType
from azure.ai.ml.entities._job.command_job import CommandJob
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.pipeline.pipeline_job import PipelineJob
from azure.ai.ml.entities._job.spark_job import SparkJob
from azure.ai.ml.entities._mixins import RestTranslatableMixin, TelemetryMixin, YamlTranslatableMixin
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities._validation import MutableValidationResult, PathAwareSchemaValidatableMixin

from ...exceptions import ErrorCategory, ErrorTarget, ScheduleException, ValidationException
from .._builders import BaseNode
from .trigger import CronTrigger, RecurrenceTrigger, TriggerBase

module_logger = logging.getLogger(__name__)


class Schedule(YamlTranslatableMixin, PathAwareSchemaValidatableMixin, Resource):
    """Schedule object used to create and manage schedules.

    This class should not be instantiated directly. Instead, please use the subclasses.

    :keyword name: The name of the schedule.
    :paramtype name: str
    :keyword trigger: The schedule trigger configuration.
    :paramtype trigger: Union[~azure.ai.ml.entities.CronTrigger, ~azure.ai.ml.entities.RecurrenceTrigger]
    :keyword display_name: The display name of the schedule.
    :paramtype display_name: Optional[str]
    :keyword description: The description of the schedule.
    :paramtype description: Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated.
    :paramtype tags: Optional[dict]]
    :keyword properties: A dictionary of properties to associate with the schedule.
    :paramtype properties: Optional[dict[str, str]]
    :keyword kwargs: Additional keyword arguments passed to the Resource constructor.
    :paramtype kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str,
        trigger: Optional[Union[CronTrigger, RecurrenceTrigger]],
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        is_enabled = kwargs.pop("is_enabled", None)
        provisioning_state = kwargs.pop("provisioning_state", None)
        super().__init__(name=name, description=description, tags=tags, properties=properties, **kwargs)
        self.trigger = trigger
        self.display_name = display_name
        self._is_enabled: bool = is_enabled
        self._provisioning_state: str = provisioning_state
        self._type: Any = None

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
        """Dump the schedule content into a file in YAML format.

        :param dest: The local path or file stream to write the YAML content to.
            If dest is a file path, a new file will be created.
            If dest is an open file, the file will be written to directly.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        :raises FileExistsError: Raised if dest is a file path and the file already exists.
        :raises IOError: Raised if dest is an open file and the file is not writable.
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    @classmethod
    def _create_validation_error(cls, message: str, no_personal_data_message: str) -> ValidationException:
        return ValidationException(
            message=message,
            no_personal_data_message=no_personal_data_message,
            target=ErrorTarget.SCHEDULE,
        )

    @classmethod
    def _resolve_cls_and_type(
        cls, data: Dict, params_override: Optional[List[Dict]] = None
    ) -> Tuple:  # pylint: disable=unused-argument
        from azure.ai.ml.entities._data_import.schedule import ImportDataSchedule
        from azure.ai.ml.entities._monitoring.schedule import MonitorSchedule

        if "create_monitor" in data:
            return MonitorSchedule, None
        if "import_data" in data:
            return ImportDataSchedule, None
        return JobSchedule, None

    @property
    def create_job(self) -> Any:  # pylint: disable=useless-return
        """The create_job entity associated with the schedule if exists."""
        module_logger.warning("create_job is not a valid property of %s", str(type(self)))
        # return None here just to be explicit
        return None

    @create_job.setter
    def create_job(self, value: Any) -> None:  # pylint: disable=unused-argument
        """Set the create_job entity associated with the schedule if exists.

        :param value: The create_job entity associated with the schedule if exists.
        :type value: Any
        """
        module_logger.warning("create_job is not a valid property of %s", str(type(self)))

    @property
    def is_enabled(self) -> bool:
        """Specifies if the schedule is enabled or not.

        :return: True if the schedule is enabled, False otherwise.
        :rtype: bool
        """
        return self._is_enabled

    @property
    def provisioning_state(self) -> str:
        """Returns the schedule's provisioning state. The possible values include
        "Creating", "Updating", "Deleting", "Succeeded", "Failed", "Canceled".

        :return: The schedule's provisioning state.
        :rtype: str
        """
        return self._provisioning_state

    @property
    def type(self) -> Optional[str]:
        """The schedule type. Accepted values are 'job' and 'monitor'.

        :return: The schedule type.
        :rtype: str
        """
        return self._type

    def _to_dict(self) -> Dict:
        res: dict = self._dump_for_validation()
        return res

    @classmethod
    def _from_rest_object(cls, obj: RestSchedule) -> "Schedule":
        from azure.ai.ml.entities._data_import.schedule import ImportDataSchedule
        from azure.ai.ml.entities._monitoring.schedule import MonitorSchedule

        if obj.properties.action.action_type == RestScheduleActionType.CREATE_JOB:
            return JobSchedule._from_rest_object(obj)
        if obj.properties.action.action_type == RestScheduleActionType.CREATE_MONITOR:
            res_monitor_schedule: Schedule = MonitorSchedule._from_rest_object(obj)
            return res_monitor_schedule
        if obj.properties.action.action_type == RestScheduleActionType.IMPORT_DATA:
            res_data_schedule: Schedule = ImportDataSchedule._from_rest_object(obj)
            return res_data_schedule
        msg = f"Unsupported schedule type {obj.properties.action.action_type}"
        raise ScheduleException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.SCHEDULE,
            error_category=ErrorCategory.SYSTEM_ERROR,
        )


class JobSchedule(RestTranslatableMixin, Schedule, TelemetryMixin):
    """Class for managing job schedules.

    :keyword name: The name of the schedule.
    :paramtype name: str
    :keyword trigger: The trigger configuration for the schedule.
    :paramtype trigger: Union[~azure.ai.ml.entities.CronTrigger, ~azure.ai.ml.entities.RecurrenceTrigger]
    :keyword create_job: The job definition or an existing job name.
    :paramtype create_job: Union[~azure.ai.ml.entities.Job, str]
    :keyword display_name: The display name of the schedule.
    :paramtype display_name: Optional[str]
    :keyword description: The description of the schedule.
    :paramtype description: Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated.
    :paramtype tags: Optional[dict[str, str]]
    :keyword properties: A dictionary of properties to associate with the schedule.
    :paramtype properties: Optional[dict[str, str]]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START job_schedule_configuration]
            :end-before: [END job_schedule_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring a JobSchedule.
    """

    def __init__(
        self,
        *,
        name: str,
        trigger: Optional[Union[CronTrigger, RecurrenceTrigger]],
        create_job: Union[Job, str],
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name=name,
            trigger=trigger,
            display_name=display_name,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )
        self._create_job = create_job
        self._type = ScheduleType.JOB

    @property
    def create_job(self) -> Union[Job, str]:
        """Return the job associated with the schedule.

        :return: The job definition or an existing job name.
        :rtype: Union[~azure.ai.ml.entities.Job, str]
        """
        return self._create_job

    @create_job.setter
    def create_job(self, value: Union[Job, str]) -> None:
        """Sets the job that will be run when the schedule is triggered.

        :param value: The job definition or an existing job name.
        :type value: Union[~azure.ai.ml.entities.Job, str]
        """
        self._create_job = value

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "JobSchedule":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return JobSchedule(
            base_path=context[BASE_PATH_CONTEXT_KEY],
            **load_from_dict(JobScheduleSchema, data, context, **kwargs),
        )

    @classmethod
    def _load_from_rest_dict(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "JobSchedule":
        """
        Load job schedule from rest object dict.

        This function is added because the user-faced schema is different from the rest one.

        For example:

        user yaml create_job is a file reference with updates(not a job definition):

        .. code-block:: yaml

            create_job:
                job: ./job.yaml
                inputs:
                    input: 10

        while what we get from rest will be a complete job definition:

        .. code-block:: yaml

            create_job:
                name: xx
                jobs:
                    node1: ...
                inputs:
                    input: ..

        :param data: The REST object to convert
        :type data: Optional[Dict]
        :param yaml_path: The yaml path
        :type yaml_path: Optional[Union[PathLike str]]
        :param params_override: A list of parameter overrides
        :type params_override: Optional[list]
        :return: The job schedule
        :rtype: JobSchedule
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
            **load_from_dict(JobScheduleSchema, data, context, **kwargs),
        )
        schedule.create_job = create_job
        return schedule

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> JobScheduleSchema:
        return JobScheduleSchema(context=context)

    def _customized_validate(self) -> MutableValidationResult:
        """Validate the resource with customized logic.

        :return: The validation result
        :rtype: MutableValidationResult
        """
        if isinstance(self.create_job, PipelineJob):
            return self.create_job._validate()
        return self._create_empty_validation_result()

    @classmethod
    def _get_skip_fields_in_schema_validation(cls) -> typing.List[str]:
        """Get the fields that should be skipped in schema validation.

        Override this method to add customized validation logic.

        :return: The list of fields to skip in schema validation
        :rtype: typing.List[str]
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
        :rtype: RestSchedule
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
            # Rest pipeline job will hold a 'Default' as experiment_name,
            # MFE will add default if None, so pass an empty string here.
            job_definition = RestPipelineJob(source_job_id=self.create_job, experiment_name="")
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
                trigger=self.trigger._to_rest_object() if self.trigger is not None else None,
            )
        )

    def __str__(self) -> str:
        try:
            res_yaml: str = self._to_yaml()
            return res_yaml
        except BaseException:  # pylint: disable=W0718
            res_jobSchedule: str = super(JobSchedule, self).__str__()
            return res_jobSchedule

    # pylint: disable-next=docstring-missing-param
    def _get_telemetry_values(self, *args: Any, **kwargs: Any) -> Dict[Literal["trigger_type"], str]:
        """Return the telemetry values of schedule.

        :return: A dictionary with telemetry values
        :rtype: Dict[Literal["trigger_type"], str]
        """
        return {"trigger_type": type(self.trigger).__name__}


class ScheduleTriggerResult:
    """Schedule trigger result returned by trigger an enabled schedule once.

    This class shouldn't be instantiated directly. Instead, it is used as the return type of schedule trigger.

    :ivar str job_name:
    :ivar str schedule_action_type:
    """

    def __init__(self, **kwargs):  # pylint: disable=unused-argument
        self.job_name = kwargs.get("job_name", None)
        self.schedule_action_type = kwargs.get("schedule_action_type", None)

    @classmethod
    def _from_rest_object(cls, obj: RestTriggerRunSubmissionDto) -> "ScheduleTriggerResult":
        """Construct a ScheduleJob from a rest object.

        :param obj: The rest object to construct from.
        :type obj: ~azure.ai.ml._restclient.v2024_01_01_preview.models.TriggerRunSubmissionDto
        :return: The constructed ScheduleJob.
        :rtype: ScheduleTriggerResult
        """
        return cls(
            schedule_action_type=obj.schedule_action_type,
            job_name=obj.submission_id,
        )

    def _to_dict(self) -> dict:
        """Convert the object to a dictionary.
        :return: The dictionary representation of the object.
        :rtype: dict
        """
        return {
            "job_name": self.job_name,
            "schedule_action_type": self.schedule_action_type,
        }
