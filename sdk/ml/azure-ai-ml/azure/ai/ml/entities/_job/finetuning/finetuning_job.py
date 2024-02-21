from .job import Job
from .job_io_mixin import JobIOMixin
from typing import Any, Optional, Dict, cast
from azure.ai.ml import Input
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ModelProvider as RestModelProvider,
)
from azure.ai.ml._utils.utils import camel_to_snake


class FineTuningJob(Job, JobIOMixin):
    def __init__(
        self,
        *,
        task: str,
        model: Input,
        model_provider: str,
        training_data: Input,
        validation_data: Optional[Input] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._task = task
        self._model = model
        self._model_provider = model_provider
        self._training_data = training_data
        self._validation_data = validation_data
        self._hyperparameters = hyperparameters

    @property
    def task(self) -> str:
        """Get finetuning task.

        :return: The type of task to run. Possible values include: "ChatCompletion"
                 "TextCompletion", "TextClassification", "QuestionAnswering","TextSummarization",
                 "TokenClassification", "TextTranslation", "ImageClassification", "ImageInstanceSegmentation",
                 "ImageObjectDetection","VideoMultiObjectTracking".

        :rtype: str
        """
        return self._task

    @task.setter
    def task(self, task: str) -> None:
        """Set finetuning task.

        :param task_type: The type of task to run. Possible values include: "ChatCompletion"
                 "TextCompletion", "TextClassification", "QuestionAnswering","TextSummarization",
                 "TokenClassification", "TextTranslation", "ImageClassification", "ImageInstanceSegmentation",
                 "ImageObjectDetection","VideoMultiObjectTracking",.

        :type task: str
        """
        self._task = task

    @property
    def model(self) -> Optional[Input]:
        """The model to be fine-tuned."""
        return self._model

    @model.setter
    def model(self, value: Input) -> None:
        """Set the model to be fine-tuned.

        :param value: Input object representing the mlflow model to be fine-tuned.
        :type value: typing.Union[typing.Dict, TabularLimitSettings]
        :raises ValidationException: Expected a mlflow model input.
        """
        if isinstance(value, Input) and cast(Input, value).type == "mlflow_model":
            self._model = value
        else:
            if not isinstance(value, dict):
                msg = "Expected a mlflow model input."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.FINETUNING,
                    error_category=ErrorCategory.USER_ERROR,
                )
            self._model = value

    @property
    def model_provider(self) -> str:
        """The model provider."""
        return self._model_provider

    @model_provider.setter
    def model_provider(self, value: str) -> None:
        """Set the model provider.

        :param value: The model provider.
        :type value: str
        """
        self._model_provider = RestModelProvider[camel_to_snake(value).upper()] if value else None

    @property
    def training_data(self) -> Input:
        """Get training data.

        :return: Training data input
        :rtype: Input
        """
        return self._training_data

    @training_data.setter
    def training_data(self, training_data: Input) -> None:
        """Set training data.

        :param training_data: Training data input
        :type training_data: Input
        """
        self._training_data = training_data

    @property
    def validation_data(self) -> Input:
        """Get validation data.

        :return: Validation data input
        :rtype: Input
        """
        return self._validation_data

    @validation_data.setter
    def validation_data(self, validation_data: Input) -> None:
        """Set validation data.

        :param validation_data: Validation data input
        :type validation_data: Input
        """
        self._validation_data = validation_data

    @property
    def hyperparameters(self) -> Input:
        """Get training data.

        :return:
        :rtype: Input
        """
        return self._hyperparameters

    @hyperparameters.setter
    def hyperparameters(self, hyperparameters: Dict[str, str]) -> None:
        """Set hyperparameters.

        :param hyperparameters: Training data input
        :type training_data: Input
        """
        self._hyperparameters = hyperparameters
