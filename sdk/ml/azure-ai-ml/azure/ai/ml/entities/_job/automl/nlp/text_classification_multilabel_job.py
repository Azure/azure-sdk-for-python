# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ClassificationMultilabelPrimaryMetrics,
    JobBaseData,
    TaskType,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    TextClassificationMultilabel as RestTextClassificationMultilabel,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake, is_data_binding_expression
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, AutoMLConstants
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.automl.nlp.automl_nlp_job import AutoMLNLPJob
from azure.ai.ml.entities._job.automl.nlp.nlp_featurization_settings import NlpFeaturizationSettings
from azure.ai.ml.entities._job.automl.nlp.nlp_limit_settings import NlpLimitSettings
from azure.ai.ml.entities._util import load_from_dict


@experimental
class TextClassificationMultilabelJob(AutoMLNLPJob):
    """Configuration for AutoML Text Classification Multilabel Job."""

    _DEFAULT_PRIMARY_METRIC = ClassificationMultilabelPrimaryMetrics.ACCURACY

    def __init__(
        self,
        *,
        target_column_name: str = None,
        training_data: Input = None,
        validation_data: Input = None,
        primary_metric: Optional[str] = None,
        log_verbosity: Optional[str] = None,
        **kwargs
    ):
        """Initializes a new AutoML Text Classification Multilabel task.

        :param target_column_name: The name of the target column
        :param training_data: Training data to be used for training
        :param validation_data: Validation data to be used for evaluating the trained model
        :param primary_metric: The primary metric to be displayed.
        :param log_verbosity: Log verbosity level
        :param kwargs: Job-specific arguments
        """
        data = kwargs.pop("data", None)
        if data is not None:
            target_column_name = data.target_column_name
            training_data = data.training_data.data  # type: Input
            validation_data = data.validation_data.data  # type: Input
        super().__init__(
            task_type=TaskType.TEXT_CLASSIFICATION_MULTILABEL,
            primary_metric=primary_metric or TextClassificationMultilabelJob._DEFAULT_PRIMARY_METRIC,
            target_column_name=target_column_name,
            training_data=training_data,
            validation_data=validation_data,
            log_verbosity=log_verbosity,
            **kwargs,
        )

    @AutoMLNLPJob.primary_metric.setter
    def primary_metric(self, value: Union[str, ClassificationMultilabelPrimaryMetrics]):
        if is_data_binding_expression(str(value), ["parent"]):
            self._primary_metric = value
            return

        self._primary_metric = (
            TextClassificationMultilabelJob._DEFAULT_PRIMARY_METRIC
            if value is None
            else ClassificationMultilabelPrimaryMetrics[camel_to_snake(value).upper()]
        )

    def _to_rest_object(self) -> JobBaseData:
        self._resolve_data_inputs()

        text_classification = RestTextClassificationMultilabel(
            data_settings=self._data,
            limit_settings=self._limits._to_rest_object() if self._limits else None,
            featurization_settings=self._featurization._to_rest_object() if self._featurization else None,
            primary_metric=self.primary_metric,
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
            task_details=text_classification,
            identity=self.identity,
        )

        result = JobBaseData(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _from_rest_object(cls, obj: JobBaseData) -> "TextClassificationMultilabelJob":
        properties: RestAutoMLJob = obj.properties
        task_details: RestTextClassificationMultilabel = properties.task_details
        assert isinstance(task_details, RestTextClassificationMultilabel)
        data_settings = task_details.data_settings
        limits = (
            NlpLimitSettings._from_rest_object(task_details.limit_settings) if task_details.limit_settings else None
        )
        featurization = (
            NlpFeaturizationSettings._from_rest_object(task_details.featurization_settings)
            if task_details.featurization_settings
            else None
        )

        text_classification_multilabel_job = cls(
            # ----- job specific params
            id=obj.id,
            name=obj.name,
            description=properties.description,
            tags=properties.tags,
            properties=properties.properties,
            experiment_name=properties.experiment_name,
            services=properties.services,
            status=properties.status,
            creation_context=obj.system_data,
            display_name=properties.display_name,
            compute=properties.compute_id,
            outputs=from_rest_data_outputs(properties.outputs),
            resources=properties.resources,
            # ----- task specific params
            primary_metric=task_details.primary_metric,
            log_verbosity=task_details.log_verbosity,
            data=data_settings,
            limits=limits,
            featurization=featurization,
            identity=properties.identity,
        )

        text_classification_multilabel_job._restore_data_inputs()

        return text_classification_multilabel_job

    def _to_component(self, **kwargs):
        raise NotImplementedError()

    @classmethod
    def _load_from_dict(
        cls, data: Dict, context: Dict, additional_message: str, inside_pipeline=False, **kwargs
    ) -> "AutoMLJob":
        from azure.ai.ml._schema.automl.nlp_vertical.text_classification_multilabel import (
            TextClassificationMultilabelSchema,
        )

        if inside_pipeline:
            from azure.ai.ml._schema.pipeline.automl_node import AutoMLTextClassificationMultilabelNode

            loaded_data = load_from_dict(
                AutoMLTextClassificationMultilabelNode,
                data,
                context,
                additional_message,
                **kwargs,
            )
        else:
            loaded_data = load_from_dict(
                TextClassificationMultilabelSchema,
                data,
                context,
                additional_message,
                **kwargs,
            )
        job_instance = cls._create_instance_from_schema_dict(loaded_data)
        return job_instance

    @classmethod
    def _create_instance_from_schema_dict(cls, loaded_data: Dict) -> "TextClassificationMultilabelJob":
        loaded_data.pop(AutoMLConstants.TASK_TYPE_YAML, None)
        return TextClassificationMultilabelJob(**loaded_data)

    def _to_dict(self, inside_pipeline=False) -> Dict:
        from azure.ai.ml._schema.automl.nlp_vertical.text_classification_multilabel import (
            TextClassificationMultilabelSchema,
        )
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLTextClassificationMultilabelNode

        if inside_pipeline:
            return AutoMLTextClassificationMultilabelNode(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        else:
            return TextClassificationMultilabelSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def __eq__(self, other):
        if not isinstance(other, TextClassificationMultilabelJob):
            return NotImplemented

        if not super(TextClassificationMultilabelJob, self).__eq__(other):
            return False

        return self.primary_metric == other.primary_metric

    def __ne__(self, other):
        return not self.__eq__(other)
