from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin
from typing import Any, Dict
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ModelProvider as RestModelProvider,
    JobBase as RestJobBase,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class FineTuningJob(Job, JobIOMixin):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        self.outputs = kwargs.pop("outputs", None)
        super().__init__(**kwargs)

    @classmethod
    def _get_model_provider_mapping(cls) -> Dict:
        """Create a mapping of task type to job class.

        :return: An FineTuningVertical object containing the model provider type to job class mapping.
        :rtype: FineTuningJob
        """
        from .custom_model_finetuning_job import CustomModelFineTuningJob
        from .azure_openai_finetuning_job import AzureOpenAIFineTuningJob

        return {
            camel_to_snake(RestModelProvider.CUSTOM): CustomModelFineTuningJob,
            camel_to_snake(RestModelProvider.AZURE_OPEN_AI): AzureOpenAIFineTuningJob,
        }

    @classmethod
    def _load_from_rest(cls, obj: RestJobBase) -> "FineTuningJob":
        """Loads the rest object to a dict containing items to init the AutoMLJob objects.

        :param obj: Azure Resource Manager resource envelope.
        :type obj: JobBase
        :raises ValidationException: task type validation error
        :return: A FineTuningJob
        :rtype: FineTuningJob
        """
        model_provider = (
            camel_to_snake(obj.properties.fine_tuning_details.model_provider)
            if obj.properties.fine_tuning_details.model_provider
            else None
        )
        class_type = cls._get_model_provider_mapping().get(model_provider, None)
        if class_type:
            res: FineTuningJob = class_type._from_rest_object(obj)
            return res
        msg = f"Unsupported model provider type: {obj.properties.task_details.task_type}"
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.FINETUNING,
            error_category=ErrorCategory.SYSTEM_ERROR,
        )
