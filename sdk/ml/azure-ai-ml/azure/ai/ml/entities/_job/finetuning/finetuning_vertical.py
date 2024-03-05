# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Optional, cast

from azure.ai.ml import Input
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    ModelProvider as RestModelProvider,
    FineTuningVertical as RestFineTuningVertical,
    UriFileJobInput,
    MLFlowModelJobInput,
)
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._job.finetuning.finetuning_job import FineTuningJob
from azure.ai.ml._utils._experimental import experimental


@experimental
class FineTuningVertical(FineTuningJob):
    def __init__(
        self,
        *,
        task: str,
        model: Input,
        model_provider: str,
        training_data: Input,
        validation_data: Optional[Input] = None,
        **kwargs: Any,
    ) -> None:
        self._task = task
        self._model = model
        self._model_provider = model_provider
        self._training_data = training_data
        self._validation_data = validation_data
        super().__init__(**kwargs)

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

        :param task: The type of task to run. Possible values include: "ChatCompletion"
                 "TextCompletion", "TextClassification", "QuestionAnswering","TextSummarization",
                 "TokenClassification", "TextTranslation", "ImageClassification", "ImageInstanceSegmentation",
                 "ImageObjectDetection","VideoMultiObjectTracking",.
        :type task: str

        :return: None
        """
        self._task = task

    @property
    def model(self) -> Optional[Input]:
        """The model to be fine-tuned.
        :return: Input object representing the mlflow model to be fine-tuned.
        :rtype: Input
        """
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
            msg = "Expected a mlflow model input."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.FINETUNING,
                error_category=ErrorCategory.USER_ERROR,
            )

    @property
    def model_provider(self) -> str:
        """The model provider.
        :return: The model provider.
        :rtype: str
        """
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
    def validation_data(self) -> Optional[Input]:
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

    def _resolve_inputs(self, rest_job: RestFineTuningVertical) -> None:
        """Resolve JobInputs to UriFileJobInput within data_settings.

        :param rest_job: The rest job object.
        :type rest_job: RestFineTuningVertical
        """
        if isinstance(rest_job.training_data, Input):
            rest_job.training_data = UriFileJobInput(uri=rest_job.training_data.path)
        if isinstance(rest_job.validation_data, Input):
            rest_job.validation_data = UriFileJobInput(uri=rest_job.validation_data.path)
        if isinstance(rest_job.model, Input):
            rest_job.model = MLFlowModelJobInput(uri=rest_job.model.path)

    def _restore_inputs(self) -> None:
        """Restore UriFileJobInputs to JobInputs within data_settings."""
        if isinstance(self.training_data, UriFileJobInput):
            self.training_data = Input(
                type=AssetTypes.URI_FILE, path=self.training_data.uri  # pylint: disable=no-member
            )
        if isinstance(self.validation_data, UriFileJobInput):
            self.validation_data = Input(
                type=AssetTypes.URI_FILE, path=self.validation_data.uri  # pylint: disable=no-member
            )
        if isinstance(self.model, MLFlowModelJobInput):
            self.model = Input(type=AssetTypes.MLFLOW_MODEL, path=self.model.uri)  # pylint: disable=no-member

    def __eq__(self, other: object) -> bool:
        """Returns True if both instances have the same values.

        This method check instances equality and returns True if both of
            the instances have the same attributes with the same values.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        if not isinstance(other, FineTuningVertical):
            return NotImplemented

        return (
            # TODO: Equality from base class does not work, no current precedence for this
            super().__eq__(other)
            and self.task == other.task
            and self.model == other.model
            and self.model_provider == other.model_provider
            and self.training_data == other.training_data
            and self.validation_data == other.validation_data
        )

    def __ne__(self, other: object) -> bool:
        """Check inequality between two FineTuningJob objects.

        :param other: Any object
        :type other: object
        :return: True or False
        :rtype: bool
        """
        return not self.__eq__(other)
