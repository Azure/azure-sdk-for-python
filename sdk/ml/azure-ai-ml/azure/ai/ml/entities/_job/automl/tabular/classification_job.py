# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Union

from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY
from azure.ai.ml._restclient.v2022_02_01_preview.models import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2022_02_01_preview.models import Classification as RestClassification
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ClassificationPrimaryMetrics,
    JobBaseData,
    TaskType,
)
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs
from azure.ai.ml.entities._job.automl.tabular.automl_tabular import AutoMLTabular
from azure.ai.ml.entities._job.automl.tabular.featurization_settings import TabularFeaturizationSettings
from azure.ai.ml.entities._job.automl.tabular.limit_settings import TabularLimitSettings
from azure.ai.ml.entities._job.automl.training_settings import ClassificationTrainingSettings
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._utils.utils import camel_to_snake, is_data_binding_expression
from azure.ai.ml._utils._experimental import experimental


@experimental
class ClassificationJob(AutoMLTabular):
    """
    Configuration for AutoML Classification Job.
    """

    _DEFAULT_PRIMARY_METRIC = ClassificationPrimaryMetrics.ACCURACY

    def __init__(
        self,
        *,
        primary_metric: str = None,
        **kwargs,
    ) -> None:
        """
        Initialize a new AutoML Classification task.

        :param primary_metric: The primary metric to use for optimization
        :param kwargs: Job-specific arguments
        """
        # Extract any task specific settings
        data = kwargs.pop("data", None)
        featurization = kwargs.pop("featurization", None)
        limits = kwargs.pop("limits", None)
        training = kwargs.pop("training", None)

        super().__init__(
            task_type=TaskType.CLASSIFICATION,
            data=data,
            featurization=featurization,
            limits=limits,
            training=training,
            **kwargs,
        )

        self.primary_metric = primary_metric or ClassificationJob._DEFAULT_PRIMARY_METRIC

    @property
    def primary_metric(self):
        return self._primary_metric

    @primary_metric.setter
    def primary_metric(self, value: Union[str, ClassificationPrimaryMetrics]):
        # TODO: better way to do this
        if is_data_binding_expression(str(value), ["parent"]):
            self._primary_metric = value
            return
        self._primary_metric = (
            ClassificationJob._DEFAULT_PRIMARY_METRIC
            if value is None
            else ClassificationPrimaryMetrics[camel_to_snake(value).upper()]
        )

    @AutoMLTabular.training.getter
    def training(self) -> ClassificationTrainingSettings:
        return self._training or ClassificationTrainingSettings()

    def _to_rest_object(self) -> JobBaseData:
        self._resolve_data_inputs()
        self._validation_data_to_rest()

        classification_task = RestClassification(
            data_settings=self._data,
            featurization_settings=self._featurization._to_rest_object() if self._featurization else None,
            limit_settings=self._limits._to_rest_object() if self._limits else None,
            training_settings=self._training._to_rest_object() if self._training else None,
            primary_metric=self.primary_metric,
            allowed_models=self._training.allowed_training_algorithms if self._training else None,
            blocked_models=self._training.blocked_training_algorithms if self._training else None,
            log_verbosity=self.log_verbosity,
        )

        properties = RestAutoMLJob(
            display_name=self.display_name,
            description=self.description,
            experiment_name=self.experiment_name,
            tags=self.tags,
            compute_id=self.compute,
            properties=self.properties,
            environment_id=self.environment_id,
            environment_variables=self.environment_variables,
            services=self.services,
            outputs=to_rest_data_outputs(self.outputs),
            resources=self.resources,
            task_details=classification_task,
            identity=self.identity,
        )

        result = JobBaseData(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _from_rest_object(cls, obj: JobBaseData) -> "ClassificationJob":
        properties: RestAutoMLJob = obj.properties
        task_details: RestClassification = properties.task_details

        job_args_dict = {
            "id": obj.id,
            "name": obj.name,
            "description": properties.description,
            "tags": properties.tags,
            "properties": properties.properties,
            "experiment_name": properties.experiment_name,
            "services": properties.services,
            "status": properties.status,
            "creation_context": obj.system_data,
            "display_name": properties.display_name,
            "compute": properties.compute_id,
            "outputs": from_rest_data_outputs(properties.outputs),
            "resources": properties.resources,
            "identity": properties.identity,
        }

        classification_job = cls(
            data=task_details.data_settings,
            featurization=TabularFeaturizationSettings._from_rest_object(task_details.featurization_settings)
            if task_details.featurization_settings
            else None,
            limits=TabularLimitSettings._from_rest_object(task_details.limit_settings)
            if task_details.limit_settings
            else None,
            training=ClassificationTrainingSettings._from_rest_object(task_details.training_settings)
            if task_details.training_settings
            else None,
            primary_metric=task_details.primary_metric,
            log_verbosity=task_details.log_verbosity,
            **job_args_dict,
        )

        classification_job._restore_data_inputs()
        classification_job._training_settings_from_rest(task_details.allowed_models, task_details.blocked_models)
        classification_job._validation_data_from_rest()

        return classification_job

    @classmethod
    def _load_from_dict(
        cls, data: Dict, context: Dict, additional_message: str, inside_pipeline=False, **kwargs
    ) -> "AutoMLJob":
        from azure.ai.ml._schema.automl.table_vertical.classification import AutoMLClassificationSchema
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLClassificationNodeSchema

        if inside_pipeline:
            return load_from_dict(AutoMLClassificationNodeSchema, data, context, additional_message, **kwargs)
        else:
            return load_from_dict(AutoMLClassificationSchema, data, context, additional_message, **kwargs)

    def _to_dict(self, inside_pipeline=False) -> Dict:
        from azure.ai.ml._schema.automl.table_vertical.classification import AutoMLClassificationSchema
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLClassificationNodeSchema

        if inside_pipeline:
            schema_dict = AutoMLClassificationNodeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        else:
            schema_dict = AutoMLClassificationSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

        return schema_dict

    def __eq__(self, other):
        if not isinstance(other, ClassificationJob):
            return NotImplemented

        if not super(ClassificationJob, self).__eq__(other):
            return False

        return self.primary_metric == other.primary_metric

    def __ne__(self, other):
        return not self.__eq__(other)
