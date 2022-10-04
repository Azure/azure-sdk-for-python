# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import json
import logging
import traceback
from abc import abstractclassmethod, abstractmethod
from collections import OrderedDict
from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, Optional, Type, Union

from azure.ai.ml._restclient.runhistory.models import Run
from azure.ai.ml._restclient.v2022_10_01_preview.models import JobBase
from azure.ai.ml._restclient.v2022_10_01_preview.models import JobType as RestJobType
from azure.ai.ml._restclient.v2022_10_01_preview.models import JobService
from azure.ai.ml._utils._html_utils import make_link, to_html
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, CommonYamlFields
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.constants._job.job import JobServices, JobType
from azure.ai.ml.entities._mixins import TelemetryMixin
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import find_type_in_override
from azure.ai.ml.exceptions import(
    ErrorCategory,
    ErrorTarget,
    JobException,
    ValidationErrorType,
    ValidationException,
    JobParsingError,
    PipelineChildJobError,
)

from ._studio_url_from_job_id import studio_url_from_job_id
from .pipeline._component_translatable import ComponentTranslatableMixin

module_logger = logging.getLogger(__name__)


def _is_pipeline_child_job(job: JobBase) -> bool:
    # pipeline child job has no properties, so we can check through testing job.properties
    # if backend has spec changes, this method need to be updated
    return job.properties is None


class Job(Resource, ComponentTranslatableMixin, TelemetryMixin):
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
    :param experiment_name:  Name of the experiment the job will be created under,
        if None is provided, experiment will be set to current directory.
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

        super().__init__(
            name=name,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )

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
        """Azure ML studio endpoint.

        :return: URL to the job detail page.
        :rtype: Optional[str]
        """
        if self.services and (JobServices.STUDIO in self.services.keys()):
            return self.services[JobServices.STUDIO].endpoint

        return studio_url_from_job_id(self.id)

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the job content into a file in yaml format.

        :param dest: The destination to receive this job's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _get_base_info_dict(self):
        return OrderedDict(
            [
                ("Experiment", self.experiment_name),
                ("Name", self.name),
                ("Type", self._type),
                ("Status", self._status),
            ]
        )

    def _repr_html_(self):
        info = self._get_base_info_dict()
        if self.studio_url:
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
    def _resolve_cls_and_type(cls, data, params_override):
        from azure.ai.ml.entities._builders.command import Command
        from azure.ai.ml.entities._builders.spark import Spark
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
        from azure.ai.ml.entities._job.import_job import ImportJob
        from azure.ai.ml.entities._job.pipeline.pipeline_job import PipelineJob
        from azure.ai.ml.entities._job.sweep.sweep_job import SweepJob

        job_type: Optional[Type["Job"]] = None
        type_in_override = find_type_in_override(params_override)
        type_str = type_in_override or data.get(CommonYamlFields.TYPE, JobType.COMMAND)  # override takes the priority
        if type_str == JobType.COMMAND:
            job_type = Command
        elif type_str == JobType.SPARK:
            job_type = Spark
        elif type_str == JobType.IMPORT:
            job_type = ImportJob
        elif type_str == JobType.SWEEP:
            job_type = SweepJob
        elif type_str == JobType.AUTOML:
            job_type = AutoMLJob
        elif type_str == JobType.PIPELINE:
            job_type = PipelineJob
        else:
            msg = f"Unsupported job type: {type_str}."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        return job_type, type_str

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
        :param params_override: Fields to overwrite on top of the yaml file.
            Format is [{"field1": "value1"}, {"field2": "value2"}], defaults to None
        :type params_override: List[Dict], optional
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
        job_type, type_str = cls._resolve_cls_and_type(data, params_override)
        job = job_type._load_from_dict(
            data=data,
            context=context,
            additional_message=f"If you are trying to configure a job that is not of type {type_str}, please specify "
            f"the correct job type in the 'type' property.",
            **kwargs,
        )
        if yaml_path:
            job._source_path = yaml_path
        return job

    @classmethod
    def _from_rest_object(cls, obj: Union[JobBase, Run]) -> "Job":  # pylint: disable=too-many-return-statements
        from azure.ai.ml.entities import PipelineJob
        from azure.ai.ml.entities._builders.command import Command
        from azure.ai.ml.entities._builders.spark import Spark
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
        from azure.ai.ml.entities._job.base_job import _BaseJob
        from azure.ai.ml.entities._job.import_job import ImportJob
        from azure.ai.ml.entities._job.sweep.sweep_job import SweepJob

        try:
            if isinstance(obj, Run):
                # special handling for child jobs
                return _BaseJob._load_from_rest(obj)
            if _is_pipeline_child_job(obj):
                raise PipelineChildJobError(job_id=obj.id)
            if obj.properties.job_type == RestJobType.COMMAND:
                # PrP only until new import job type is ready on MFE in PuP
                # compute type 'DataFactory' is reserved compute name for 'clusterless' ADF jobs
                if obj.properties.compute_id.endswith("/" + ComputeType.ADF):
                    return ImportJob._load_from_rest(obj)

                return Command._load_from_rest_job(obj)
            if obj.properties.job_type == RestJobType.SPARK:
                return Spark._load_from_rest_job(obj)
            if obj.properties.job_type == RestJobType.SWEEP:
                return SweepJob._load_from_rest(obj)
            if obj.properties.job_type == RestJobType.AUTO_ML:
                return AutoMLJob._load_from_rest(obj)
            if obj.properties.job_type == RestJobType.PIPELINE:
                return PipelineJob._load_from_rest(obj)
        except PipelineChildJobError as ex:
            raise ex
        except Exception as ex:
            error_message = json.dumps(obj.as_dict(), indent=2) if obj else None
            module_logger.info(
                "Exception: %s.\n%s\nUnable to parse the job resource: %s.\n", ex, traceback.format_exc(), error_message
            )
            raise JobParsingError(
                message=str(ex),
                no_personal_data_message=f"Unable to parse a job resource of type:{type(obj).__name__}",
                error_category=ErrorCategory.SYSTEM_ERROR,
            )
        else:
            msg = f"Unsupported job type {obj.properties.job_type}"
            raise JobException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.SYSTEM_ERROR,
            )

    def _get_telemetry_values(self):  # pylint: disable=arguments-differ
        telemetry_values = {"type": self.type}
        return telemetry_values

    @abstractclassmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "Job":
        pass
