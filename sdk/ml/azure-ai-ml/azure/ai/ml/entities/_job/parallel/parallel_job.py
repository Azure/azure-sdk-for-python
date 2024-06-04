# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import JobBaseData
from azure.ai.ml._schema.job.parallel_job import ParallelJobSchema
from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.entities._credentials import (
    AmlTokenConfiguration,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from ..job import Job
from ..job_io_mixin import JobIOMixin
from .parameterized_parallel import ParameterizedParallel

# avoid circular import error
if TYPE_CHECKING:
    from azure.ai.ml.entities._builders import Parallel
    from azure.ai.ml.entities._component.parallel_component import ParallelComponent

module_logger = logging.getLogger(__name__)


class ParallelJob(Job, ParameterizedParallel, JobIOMixin):
    """Parallel job.

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
    :keyword identity: The identity that the job will use while running on compute.
    :paramtype identity: Optional[Union[~azure.ai.ml.ManagedIdentityConfiguration, ~azure.ai.ml.AmlTokenConfiguration,
        ~azure.ai.ml.UserIdentityConfiguration]]
    :param task: The parallel task.
    :type task: ParallelTask
    :param mini_batch_size: The mini batch size.
    :type mini_batch_size: str
    :param partition_keys: The partition keys.
    :type partition_keys: list
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
        inputs: Optional[Dict[str, Union[Input, str, bool, int, float]]] = None,
        outputs: Optional[Dict[str, Output]] = None,
        identity: Optional[
            Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration, Dict]
        ] = None,
        **kwargs: Any,
    ):
        kwargs[TYPE] = JobType.PARALLEL

        super().__init__(**kwargs)

        self.inputs = inputs  # type: ignore[assignment]
        self.outputs = outputs  # type: ignore[assignment]
        self.identity = identity

    def _to_dict(self) -> Dict:
        res: dict = ParallelJobSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)  # pylint: disable=no-member
        return res

    def _to_rest_object(self) -> None:
        pass

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "ParallelJob":
        loaded_data = load_from_dict(ParallelJobSchema, data, context, additional_message, **kwargs)
        return ParallelJob(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

    @classmethod
    def _load_from_rest(cls, obj: JobBaseData) -> None:
        pass

    def _to_component(self, context: Optional[Dict] = None, **kwargs: Any) -> "ParallelComponent":
        """Translate a parallel job to component job.

        :param context: Context of parallel job YAML file.
        :type context: dict
        :return: Translated parallel component.
        :rtype: ParallelComponent
        """
        from azure.ai.ml.entities._component.parallel_component import ParallelComponent

        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        context = context or {BASE_PATH_CONTEXT_KEY: Path("./")}

        # Create anonymous parallel component with default version as 1
        init_kwargs = {}
        for key in [
            "mini_batch_size",
            "partition_keys",
            "logging_level",
            "max_concurrency_per_instance",
            "error_threshold",
            "mini_batch_error_threshold",
            "retry_settings",
            "resources",
        ]:
            value = getattr(self, key)
            from azure.ai.ml.entities import BatchRetrySettings, JobResourceConfiguration

            values_to_check: List = []
            if key == "retry_settings" and isinstance(value, BatchRetrySettings):
                values_to_check = [value.max_retries, value.timeout]
            elif key == "resources" and isinstance(value, JobResourceConfiguration):
                values_to_check = [
                    value.locations,
                    value.instance_count,
                    value.instance_type,
                    value.shm_size,
                    value.max_instance_count,
                    value.docker_args,
                ]
            else:
                values_to_check = [value]

            # note that component level attributes can not be data binding expressions
            # so filter out data binding expression properties here;
            # they will still take effect at node level according to _to_node
            if any(
                map(
                    lambda x: is_data_binding_expression(x, binding_prefix=["parent", "inputs"], is_singular=False)
                    or is_data_binding_expression(x, binding_prefix=["inputs"], is_singular=False),
                    values_to_check,
                )
            ):
                continue

            init_kwargs[key] = getattr(self, key)

        return ParallelComponent(
            base_path=context[BASE_PATH_CONTEXT_KEY],
            # for parallel_job.task, all attributes for this are string for now so data binding expression is allowed
            # in SDK level naturally, but not sure if such component is valid. leave the validation to service side.
            task=self.task,
            inputs=self._to_inputs(inputs=self.inputs, pipeline_job_dict=pipeline_job_dict),
            outputs=self._to_outputs(outputs=self.outputs, pipeline_job_dict=pipeline_job_dict),
            input_data=self.input_data,
            # keep them if no data binding expression detected to keep the behavior of to_component
            **init_kwargs,
        )

    def _to_node(self, context: Optional[Dict] = None, **kwargs: Any) -> "Parallel":
        """Translate a parallel job to a pipeline node.

        :param context: Context of parallel job YAML file.
        :type context: dict
        :return: Translated parallel component.
        :rtype: Parallel
        """
        from azure.ai.ml.entities._builders import Parallel

        component = self._to_component(context, **kwargs)

        # pylint: disable=abstract-class-instantiated
        return Parallel(
            component=component,
            compute=self.compute,
            # Need to supply the inputs with double curly.
            inputs=self.inputs,  # type: ignore[arg-type]
            outputs=self.outputs,  # type: ignore[arg-type]
            mini_batch_size=self.mini_batch_size,
            partition_keys=self.partition_keys,
            input_data=self.input_data,
            # task will be inherited from component & base_path will be set correctly.
            retry_settings=self.retry_settings,
            logging_level=self.logging_level,
            max_concurrency_per_instance=self.max_concurrency_per_instance,
            error_threshold=self.error_threshold,
            mini_batch_error_threshold=self.mini_batch_error_threshold,
            environment_variables=self.environment_variables,
            properties=self.properties,
            identity=self.identity,
            resources=self.resources if self.resources and not isinstance(self.resources, dict) else None,
        )

    def _validate(self) -> None:
        if self.name is None:
            msg = "Job name is required"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )
        if self.compute is None:
            msg = "compute is required"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )
        if self.task is None:
            msg = "task is required"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )
