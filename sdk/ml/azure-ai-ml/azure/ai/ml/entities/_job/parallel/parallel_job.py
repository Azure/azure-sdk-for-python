# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Dict, Union

from azure.ai.ml._schema.job.parallel_job import ParallelJobSchema
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobBaseData
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
    TYPE,
    JobType,
)

from ..job import Job
from azure.ai.ml.entities._util import load_from_dict
from ..job_io_mixin import JobIOMixin
from .parameterized_parallel import ParameterizedParallel
from azure.ai.ml._ml_exceptions import ErrorTarget, ErrorCategory, ValidationException

module_logger = logging.getLogger(__name__)


class ParallelJob(Job, ParameterizedParallel, JobIOMixin):
    """Parallel job

    :param name: Name of the job.
    :type name: str
    :param version: Version of the job.
    :type version: str
    :param id:  Global id of the resource, Azure Resource Manager ID.
    :type id: str
    :param type:  Type of the job, supported is 'parallel'.
    :type type: str
    :param description: Description of the job.
    :type description: str
    :param tags: Internal use only.
    :type tags: dict
    :param properties: Internal use only.
    :type properties: dict
    :param display_name: Display name of the job.
    :type display_name: str
    :param retry_settings: parallel job run failed retry
    :type retry_settings: BatchRetrySettings
    :param logging_level: A string of the logging level name
    :type logging_level: str
    :param max_concurrency_per_instance: The max parallellism that each compute instance has.
    :type max_concurrency_per_instance: int
    :param error_threshold: The number of item processing failures should be ignored.
    :type error_threshold: int
    :param mini_batch_error_threshold: The number of mini batch processing failures should be ignored.
    :type mini_batch_error_threshold: int
    :param task: The parallel task.
    :type task: ParallelTask
    :param mini_batch_size: The mini batch size.
    :type mini_batch_size: str
    :param input_data: The input data.
    :type input_data: str
    :param inputs: Inputs of the job.
    :type inputs: dict
    :param outputs: Outputs of the job.
    :type outputs: dict
    """

    def __init__(
        self,
        *,
        inputs: Dict[str, Union[Input, str, bool, int, float]] = None,
        outputs: Dict[str, Output] = None,
        **kwargs,
    ):
        kwargs[TYPE] = JobType.PARALLEL

        super().__init__(**kwargs)

        self.inputs = inputs
        self.outputs = outputs

    def _to_dict(self):
        return ParallelJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_rest_object(self):
        pass

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "ParallelJob":
        loaded_data = load_from_dict(ParallelJobSchema, data, context, additional_message, **kwargs)
        return ParallelJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

    @classmethod
    def _load_from_rest(cls, obj: JobBaseData):
        pass

    def _to_component(self, context: Dict = None, **kwargs):
        """Translate a parallel job to component job.

        :param context: Context of parallel job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated parallel component.
        """
        from azure.ai.ml.entities import ParallelComponent

        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})

        # Create anonymous parallel component with default version as 1
        return ParallelComponent(
            base_path=context[BASE_PATH_CONTEXT_KEY],
            is_anonymous=True,
            mini_batch_size=self.mini_batch_size,
            input_data=self.input_data,
            task=self.task,
            retry_settings=self.retry_settings,
            logging_level=self.logging_level,
            max_concurrency_per_instance=self.max_concurrency_per_instance,
            error_threshold=self.error_threshold,
            mini_batch_error_threshold=self.mini_batch_error_threshold,
            inputs=self._to_component_inputs(inputs=self.inputs, pipeline_job_dict=pipeline_job_dict),
            outputs=self._to_component_outputs(outputs=self.outputs, pipeline_job_dict=pipeline_job_dict),
            resources=self.resources if self.resources else None,
        )

    def _to_node(self, context: Dict = None, **kwargs):
        """Translate a parallel job to a pipeline node.

        :param context: Context of parallel job YAML file.
        :param kwargs: Extra arguments.
        :return: Translated parallel component.
        """
        from azure.ai.ml.entities._builders import Parallel

        component = self._to_component(context, **kwargs)

        return Parallel(
            component=component,
            compute=self.compute,
            # Need to supply the inputs with double curly.
            inputs=self.inputs,
            outputs=self.outputs,
            mini_batch_size=self.mini_batch_size,
            input_data=self.input_data,
            task=self.task,
            retry_settings=self.retry_settings,
            logging_level=self.logging_level,
            max_concurrency_per_instance=self.max_concurrency_per_instance,
            error_threshold=self.error_threshold,
            mini_batch_error_threshold=self.mini_batch_error_threshold,
            environment_variables=self.environment_variables,
        )

    def _validate(self) -> None:
        if self.name is None:
            msg = "Job name is required"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        if self.compute is None:
            msg = "compute is required"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
        if self.task is None:
            msg = "task is required"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
            )
