# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_02_01_preview.models import JobBase, MLTableJobInput, ResourceConfiguration, TaskType
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import TYPE, AssetTypes
from azure.ai.ml.constants._job.automl import AutoMLConstants
from azure.ai.ml.entities._credentials import (
    AmlTokenConfiguration,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
)
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin
from azure.ai.ml.entities._job.pipeline._io import AutoMLNodeIOMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

module_logger = logging.getLogger(__name__)


class AutoMLJob(Job, JobIOMixin, AutoMLNodeIOMixin, ABC):
    """AutoML job entity."""

    def __init__(
        self,
        *,
        resources: Optional[ResourceConfiguration] = None,
        identity: Optional[
            Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]
        ] = None,
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

    @property
    @abstractmethod
    def training_data(self) -> Input:
        raise NotImplementedError()

    @property
    @abstractmethod
    def validation_data(self) -> Input:
        raise NotImplementedError()

    @property
    @abstractmethod
    def test_data(self) -> Input:
        raise NotImplementedError()

    @classmethod
    def _load_from_rest(cls, obj: JobBase) -> "AutoMLJob":
        task_type = (
            camel_to_snake(obj.properties.task_details.task_type) if obj.properties.task_details.task_type else None
        )
        class_type = cls._get_task_mapping().get(task_type, None)
        if class_type:
            return class_type._from_rest_object(obj)

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
        **kwargs,
    ) -> "AutoMLJob":
        task_type = data.get(AutoMLConstants.TASK_TYPE_YAML)
        class_type = cls._get_task_mapping().get(task_type, None)
        if class_type:
            return class_type._load_from_dict(
                data,
                context,
                additional_message,
                **kwargs,
            )
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

    def _resolve_data_inputs(self, rest_job):  # pylint: disable=no-self-use
        """Resolve JobInputs to MLTableJobInputs within data_settings."""
        if isinstance(rest_job.training_data, Input):
            rest_job.training_data = MLTableJobInput(uri=rest_job.training_data.path)
        if isinstance(rest_job.validation_data, Input):
            rest_job.validation_data = MLTableJobInput(uri=rest_job.validation_data.path)
        if hasattr(rest_job, "test_data") and isinstance(rest_job.test_data, Input):
            rest_job.test_data = MLTableJobInput(uri=rest_job.test_data.path)

    def _restore_data_inputs(self):
        """Restore MLTableJobInputs to JobInputs within data_settings."""
        if isinstance(self.training_data, MLTableJobInput):
            self.training_data = Input(
                type=AssetTypes.MLTABLE, path=self.training_data.uri  # pylint: disable=no-member
            )
        if isinstance(self.validation_data, MLTableJobInput):
            self.validation_data = Input(
                type=AssetTypes.MLTABLE, path=self.validation_data.uri  # pylint: disable=no-member
            )
        if hasattr(self, "test_data") and isinstance(self.test_data, MLTableJobInput):
            self.test_data = Input(type=AssetTypes.MLTABLE, path=self.test_data.uri)  # pylint: disable=no-member
