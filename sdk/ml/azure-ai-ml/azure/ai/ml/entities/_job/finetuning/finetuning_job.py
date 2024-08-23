# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Dict

from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ModelProvider as RestModelProvider,
    JobBase as RestJobBase,
)
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import TYPE
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml.constants._job.finetuning import FineTuningConstants
from azure.ai.ml._utils._experimental import experimental


@experimental
class FineTuningJob(Job, JobIOMixin):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        kwargs[TYPE] = JobType.FINE_TUNING
        self.outputs = kwargs.pop("outputs", None)
        super().__init__(**kwargs)

    def __eq__(self, other: object) -> bool:
        """Returns True if both instances have the same values.

        This method check instances equality and returns True if both of
            the instances have the same attributes with the same values.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        if not isinstance(other, FineTuningJob):
            return NotImplemented

        return self.outputs == other.outputs

    def __ne__(self, other: object) -> bool:
        """Check inequality between two FineTuningJob objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)

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
        msg = f"Unsupported model provider type: {obj.properties.fine_tuning_details.model_provider}"
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.FINETUNING,
            error_category=ErrorCategory.SYSTEM_ERROR,
        )

    @classmethod
    def _load_from_dict(
        cls,
        data: Dict,
        context: Dict,
        additional_message: str,
        **kwargs: Any,
    ) -> "FineTuningJob":
        """Loads the dictionary objects to an FineTuningJob object.

        :param data: A data dictionary.
        :type data: typing.Dict
        :param context: A context dictionary.
        :type context: typing.Dict
        :param additional_message: An additional message to be logged in the ValidationException.
        :type additional_message: str

        :raises ValidationException: task type validation error
        :return: An FineTuningJob
        :rtype: FineTuningJob
        """
        model_provider = data.get(FineTuningConstants.ModelProvider)
        class_type = cls._get_model_provider_mapping().get(model_provider, None)
        if class_type:
            res: FineTuningJob = class_type._load_from_dict(
                data,
                context,
                additional_message,
                **kwargs,
            )
            return res
        msg = f"Unsupported model provider type: {model_provider}"
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.AUTOML,
            error_category=ErrorCategory.USER_ERROR,
        )
