# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import traceback
from abc import abstractclassmethod, abstractmethod
import logging
from os import PathLike
from pathlib import Path
from typing import Dict, Optional, Type, Union
from azure.ai.ml._utils.utils import load_yaml, dump_yaml_to_file
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
    CommonYamlFields,
    JobType,
    PARAMS_OVERRIDE_KEY,
    JobServices,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin, TelemetryMixin
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    JobService,
    JobBaseData,
    JobType as RestJobType,
)
from azure.ai.ml._restclient.runhistory.models import Run
from azure.ai.ml.entities._util import find_type_in_override
from azure.ai.ml.entities._job.job_errors import JobParsingError, PipelineChildJobError
from .pipeline._component_translatable import ComponentTranslatableMixin

from azure.ai.ml._ml_exceptions import ErrorTarget, ErrorCategory, ValidationException, JobException
from collections import OrderedDict

from azure.ai.ml._utils._html_utils import to_html, make_link

module_logger = logging.getLogger(__name__)


def _is_pipeline_child_job(job: JobBaseData) -> bool:
    # pipeline child job has no properties, so we can check through testing job.properties
    # if backend has spec changes, this method need to be updated
    return job.properties is None


class Job(Resource, RestTranslatableMixin, ComponentTranslatableMixin, TelemetryMixin):
    """Base class for job, can't be instantiated directly.

    :param name: Name of the resource.
    :type name: str
    :param display_name: Display name of the resource.
    :type display_name: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The job property dictionary.
    :type properties: dict[str, str]
    :param experiment_name:  Name of the experiment the job will be created under, if None is provided, experiment will be set to current directory.
    :type experiment_name: str
    :param services: Information on services associated with the job.
    :type services: dict[str, JobService]
    :param compute: Information on compute resources associated with the job.
    :type compute: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        name: str = None,
        display_name: str = None,
        description: str = None,
        tags: Dict = None,
        properties: Dict = None,
        experiment_name: str = None,
        compute: str = None,
        services: Dict[str, JobService] = None,
        **kwargs,
    ):
        self._type = kwargs.pop("type", JobType.COMMAND)
        self._status = kwargs.pop("status", None)
        self._log_files = kwargs.pop("log_files", None)

        super().__init__(name=name, description=description, tags=tags, properties=properties, **kwargs)

        self.display_name = display_name
        self.experiment_name = experiment_name
        self.compute = compute
        self.services = services

    @property
    def type(self) -> Optional[str]:
        """Type of the job, supported are 'command' and 'sweep'.

        :return: Type of the job.
        :rtype: str
        """
        return self._type

    @property
    def status(self) -> Optional[str]:
        """Status of the job.

        Common values returned include "Running", "Completed", and "Failed".

        .. note::

            * NotStarted - This is a temporary state client-side Run objects are in before cloud submission.
            * Starting - The Run has started being processed in the cloud. The caller has a run ID at this point.
            * Provisioning - Returned when on-demand compute is being created for a given job submission.
            * Preparing - The run environment is being prepared:
                * docker image build
                * conda environment setup
            * Queued - The job is queued in the compute target. For example, in BatchAI the job is in queued state
                 while waiting for all the requested nodes to be ready.
            * Running - The job started to run in the compute target.
            * Finalizing - User code has completed and the run is in post-processing stages.
            * CancelRequested - Cancellation has been requested for the job.
            * Completed - The run completed successfully. This includes both the user code and run
                post-processing stages.
            * Failed - The run failed. Usually the Error property on a run will provide details as to why.
            * Canceled - Follows a cancellation request and indicates that the run is now successfully cancelled.
            * NotResponding - For runs that have Heartbeats enabled, no heartbeat has been recently sent.

        :return: Status of the job.
        :rtype: str
        """
        return self._status

    @property
    def log_files(self) -> Optional[Dict[str, str]]:
        """Job output files.

        :return: Dictionary of log names to url.
        :rtype: Optional[Dict[str, str]]
        """
        return self._log_files

    @property
    def studio_url(self) -> Optional[str]:
        """Azure ML studio endpoint

        :return: URL to the job detail page.
        :rtype: Optional[str]
        """

        if self.services and self.services[JobServices.STUDIO]:
            return self.services[JobServices.STUDIO].endpoint

    def dump(self, path: Union[PathLike, str]) -> None:
        """Dump the job content into a file in yaml format.

        :param path: Path to a local file as the target, new file will be created, raises exception if the file exists.
        :type path: str
        """

        yaml_serialized = self._to_dict()
        dump_yaml_to_file(path, yaml_serialized, default_flow_style=False)

    def _get_base_info_dict(self):
        return OrderedDict(
            [("Experiment", self.experiment_name), ("Name", self.name), ("Type", self._type), ("Status", self._status)]
        )

    def _repr_html_(self):
        info = self._get_base_info_dict()
        info.update(
            [
                ("Details Page", make_link(self.studio_url, "Link to Azure Machine Learning studio")),
            ]
        )
        return to_html(info)

    @abstractmethod
    def _to_dict(self) -> Dict:
        pass

    @classmethod
    def load(
        cls,
        path: Union[PathLike, str],
        params_override: list = None,
        **kwargs,
    ) -> "Job":
        """Construct a job object from a yaml file.

        :param cls: Indicates that this is a class method.
        :type cls: class
        :param path: Path to a local file as the source.
        :type path: Union[PathLike, str]
        :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}], defaults to None
        :type params_override: list, optional
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        :return: Loaded job object.
        :rtype: Job
        """
        params_override = params_override or []
        yaml_dict = load_yaml(path)
        return cls._load(data=yaml_dict, yaml_path=path, params_override=params_override, **kwargs)

    @classmethod
    def _load(
        cls,
        data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "Job":
        """Load a job object from a yaml file.

        :param cls: Indicates that this is a class method.
        :type cls: class
        :param data: Data Dictionary, defaults to None
        :type data: Dict, optional
        :param yaml_path: YAML Path, defaults to None
        :type yaml_path: Union[PathLike, str], optional
        :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}], defaults to None
        :type params_override: list, optional
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        :raises Exception: An exception
        :return: Loaded job object.
        :rtype: Job
        """
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }

        from azure.ai.ml.entities import (
            CommandJob,
            PipelineJob,
        )
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
        from azure.ai.ml.entities._job.sweep.sweep_job import SweepJob

        job_type: Optional[Type["Job"]] = None
        type_in_override = find_type_in_override(params_override)
        type = type_in_override or data.get(CommonYamlFields.TYPE, JobType.COMMAND)  # override takes the priority
        if type == JobType.COMMAND:
            job_type = CommandJob
        elif type == JobType.SWEEP:
            job_type = SweepJob
        elif type == JobType.AUTOML:
            job_type = AutoMLJob
        elif type == JobType.PIPELINE:
            job_type = PipelineJob
        else:
            msg = f"Unsupported job type: {type}."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        return job_type._load_from_dict(
            data=data,
            context=context,
            additional_message=f"If you are trying to configure a job that is not of type {type}, please specify the correct job type in the 'type' property.",
            **kwargs,
        )

    @classmethod
    def _from_rest_object(cls, job_rest_object: Union[JobBaseData, Run]) -> "Job":
        from azure.ai.ml.entities import CommandJob, PipelineJob
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
        from azure.ai.ml.entities._job.sweep.sweep_job import SweepJob
        from azure.ai.ml.entities._job.base_job import _BaseJob

        try:
            if isinstance(job_rest_object, Run):
                # special handling for child jobs
                return _BaseJob._load_from_rest(job_rest_object)
            elif _is_pipeline_child_job(job_rest_object):
                raise PipelineChildJobError(job_id=job_rest_object.id)
            elif job_rest_object.properties.job_type == RestJobType.COMMAND:
                return CommandJob._load_from_rest(job_rest_object)
            elif job_rest_object.properties.job_type == RestJobType.SWEEP:
                return SweepJob._load_from_rest(job_rest_object)
            elif job_rest_object.properties.job_type == RestJobType.AUTO_ML:
                return AutoMLJob._load_from_rest(job_rest_object)
            elif job_rest_object.properties.job_type == RestJobType.PIPELINE:
                return PipelineJob._load_from_rest(job_rest_object)
        except PipelineChildJobError as ex:
            raise ex
        except Exception as ex:
            error_message = json.dumps(job_rest_object.as_dict(), indent=2) if job_rest_object else None
            module_logger.info(
                f"Exception: {ex}.\n{traceback.format_exc()}\n" f"Unable to parse the job resource: {error_message}.\n"
            )
            raise JobParsingError(
                message=str(ex),
                no_personal_data_message=f"Unable to parse a job resourse of type:{type(job_rest_object).__name__}",
                error_category=ErrorCategory.SYSTEM_ERROR,
            )
        else:
            msg = f"Unsupported job type {job_rest_object.properties.job_type}"
            raise JobException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.SYSTEM_ERROR,
            )

    def _get_telemetry_values(self):
        telemetry_values = {"type": self.type}
        return telemetry_values

    @abstractclassmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "Job":
        pass
