# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from abc import ABC
from typing import Any, Dict, Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    AmlToken,
    JobBaseData,
    ManagedIdentity,
    MLTableJobInput,
    ResourceConfiguration,
    TaskType,
    UserIdentity,
)
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import TYPE, AssetTypes, AutoMLConstants, JobType
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin
from azure.ai.ml.entities._job.pipeline._io import AutoMLNodeIOMixin

module_logger = logging.getLogger(__name__)


class AutoMLJob(Job, JobIOMixin, AutoMLNodeIOMixin, ABC):
    """AutoML job entity."""

    def __init__(
        self,
        *,
        resources: ResourceConfiguration = None,
        identity: Union[ManagedIdentity, AmlToken, UserIdentity] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize an AutoML job entity.

        :param task_details: The task configuration of the job. This can be Classification, Regression, etc.
        :param resources: Resource configuration for the job.
        :param identity: Identity that training job will use while running on compute.
        :type identity: Union[ManagedIdentity, AmlToken, UserIdentity]
        :param kwargs:
        """
        kwargs[TYPE] = JobType.AUTOML
        self.environment_id = kwargs.pop("environment_id", None)
        self.environment_variables = kwargs.pop("environment_variables", None)
        self.outputs = kwargs.pop("outputs", None)

        super().__init__(**kwargs)

        self.resources = resources
        self.identity = identity

    @classmethod
    def _load_from_rest(cls, obj: JobBaseData) -> "AutoMLJob":
        task_type = (
            camel_to_snake(obj.properties.task_details.task_type) if obj.properties.task_details.task_type else None
        )
        class_type = cls._get_task_mapping().get(task_type, None)
        if class_type:
            return class_type._from_rest_object(obj)
        else:
            msg = f"Unsupported task type: {obj.properties.task_details.task_type}"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.SYSTEM_ERROR,
            )

    @classmethod
    def _load_from_dict(
        cls,
        data: Dict,
        context: Dict,
        additional_message: str,
        inside_pipeline=False,
        **kwargs,
    ) -> "AutoMLJob":
        task_type = data.get(AutoMLConstants.TASK_TYPE_YAML)
        class_type = cls._get_task_mapping().get(task_type, None)
        if class_type:
            return class_type._load_from_dict(
                data,
                context,
                additional_message,
                inside_pipeline=inside_pipeline,
                **kwargs,
            )
        else:
            msg = f"Unsupported task type: {task_type}"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.USER_ERROR,
            )

    @classmethod
    def _create_instance_from_schema_dict(cls, loaded_data: Dict) -> "AutoMLJob":
        """Create an automl job instance from schema parsed dict."""
        task_type = loaded_data.pop(AutoMLConstants.TASK_TYPE_YAML)
        class_type = cls._get_task_mapping().get(task_type, None)
        if class_type:
            return class_type._create_instance_from_schema_dict(loaded_data=loaded_data)
        else:
            msg = f"Unsupported task type: {task_type}"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.AUTOML,
                error_category=ErrorCategory.USER_ERROR,
            )

    @classmethod
    def _get_task_mapping(cls):
        from .image import (
            ImageClassificationJob,
            ImageClassificationMultilabelJob,
            ImageInstanceSegmentationJob,
            ImageObjectDetectionJob,
        )
        from .nlp import TextClassificationJob, TextClassificationMultilabelJob, TextNerJob
        from .tabular import ClassificationJob, ForecastingJob, RegressionJob

        # create a mapping of task type to job class
        return {
            camel_to_snake(TaskType.CLASSIFICATION): ClassificationJob,
            camel_to_snake(TaskType.REGRESSION): RegressionJob,
            camel_to_snake(TaskType.FORECASTING): ForecastingJob,
            camel_to_snake(TaskType.IMAGE_CLASSIFICATION): ImageClassificationJob,
            camel_to_snake(TaskType.IMAGE_CLASSIFICATION_MULTILABEL): ImageClassificationMultilabelJob,
            camel_to_snake(TaskType.IMAGE_OBJECT_DETECTION): ImageObjectDetectionJob,
            camel_to_snake(TaskType.IMAGE_INSTANCE_SEGMENTATION): ImageInstanceSegmentationJob,
            camel_to_snake(TaskType.TEXT_NER): TextNerJob,
            camel_to_snake(TaskType.TEXT_CLASSIFICATION): TextClassificationJob,
            camel_to_snake(TaskType.TEXT_CLASSIFICATION_MULTILABEL): TextClassificationMultilabelJob,
        }

    def _resolve_data_inputs(self):
        """Resolve JobInputs to MLTableJobInputs within data_settings."""
        training_data = self._data.training_data
        if isinstance(training_data.data, Input):
            self._data.training_data.data = MLTableJobInput(uri=training_data.data.path)
        validation_data = self._data.validation_data
        if validation_data and isinstance(validation_data.data, Input):
            self._data.validation_data.data = MLTableJobInput(uri=validation_data.data.path)
        test_data = self._data.test_data
        if test_data and isinstance(test_data.data, Input):
            self._data.test_data.data = MLTableJobInput(uri=test_data.data.path)

    def _restore_data_inputs(self):
        """Restore MLTableJobInputs to JobInputs within data_settings."""
        training_data = self._data.training_data
        if isinstance(training_data.data, MLTableJobInput):
            self._data.training_data.data = Input(type=AssetTypes.MLTABLE, path=training_data.data.uri)
        validation_data = self._data.validation_data
        if validation_data and isinstance(validation_data.data, MLTableJobInput):
            self._data.validation_data.data = Input(type=AssetTypes.MLTABLE, path=validation_data.data.uri)
        test_data = self._data.test_data
        if test_data and isinstance(test_data.data, MLTableJobInput):
            self._data.test_data.data = Input(type=AssetTypes.MLTABLE, path=test_data.data.uri)
