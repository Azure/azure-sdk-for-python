# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, Optional, Union

from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    AutoMLJob as RestAutoMLJob,
    JobBaseData,
    TaskType,
    TextNer as RestTextNER,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models._azure_machine_learning_workspaces_enums import (
    ClassificationPrimaryMetrics,
)
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs
from azure.ai.ml.entities._job.automl.nlp.automl_nlp_job import AutoMLNLPJob
from azure.ai.ml.entities._job.automl.nlp.nlp_featurization_settings import NlpFeaturizationSettings
from azure.ai.ml.entities._job.automl.nlp.nlp_limit_settings import NlpLimitSettings
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._utils.utils import camel_to_snake, is_data_binding_expression
from azure.ai.ml._utils._experimental import experimental


@experimental
class TextNerJob(AutoMLNLPJob):
    """
    Configuration for AutoML Text NER Job.
    """

    _DEFAULT_PRIMARY_METRIC = ClassificationPrimaryMetrics.ACCURACY

    def __init__(
        self,
        *,
        training_data: Input = None,
        validation_data: Input = None,
        target_column_name: Optional[str] = None,
        primary_metric: Optional[str] = None,
        log_verbosity: Optional[str] = None,
        **kwargs
    ):
        """
        Initializes a new AutoML Text NER task.

        :param training_data: Training data to be used for training
        :param validation_data: Validation data to be used for evaluating the trained model
        :param target_column_name: The name of the target column  # 1779366 remove when model gets updated
        :param primary_metric: The primary metric to be displayed.
        :param log_verbosity: Log verbosity level
        :param kwargs: Job-specific arguments
        """
        if target_column_name is None:
            target_column_name = "label"  # 1779366 remove when model gets updated
        data = kwargs.pop("data", None)
        if data is not None:
            target_column_name = data.target_column_name
            training_data = data.training_data.data  # type: Input
            validation_data = data.validation_data.data  # type: Input
        super(TextNerJob, self).__init__(
            task_type=TaskType.TEXT_NER,
            primary_metric=primary_metric or TextNerJob._DEFAULT_PRIMARY_METRIC,
            target_column_name=target_column_name,
            training_data=training_data,
            validation_data=validation_data,
            log_verbosity=log_verbosity,
            **kwargs,
        )

    @AutoMLNLPJob.primary_metric.setter
    def primary_metric(self, value: Union[str, ClassificationPrimaryMetrics]):
        if is_data_binding_expression(str(value), ["parent"]):
            self._primary_metric = value
            return

        self._primary_metric = (
            TextNerJob._DEFAULT_PRIMARY_METRIC
            if value is None
            else ClassificationPrimaryMetrics[camel_to_snake(value).upper()]
        )

    def _to_rest_object(self) -> JobBaseData:
        self._resolve_data_inputs()

        text_classification = RestTextNER(
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
    def _from_rest_object(cls, obj: JobBaseData) -> "TextNerJob":
        properties: RestAutoMLJob = obj.properties
        task_details: RestTextNER = properties.task_details
        assert isinstance(task_details, RestTextNER)
        data_settings = task_details.data_settings
        limits = (
            NlpLimitSettings._from_rest_object(task_details.limit_settings) if task_details.limit_settings else None
        )
        featurization = (
            NlpFeaturizationSettings._from_rest_object(task_details.featurization_settings)
            if task_details.featurization_settings
            else None
        )

        text_ner_job = cls(
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

        text_ner_job._restore_data_inputs()

        return text_ner_job

    def _to_component(self, **kwargs):
        raise NotImplementedError()

    @classmethod
    def _load_from_dict(
        cls, data: Dict, context: Dict, additional_message: str, inside_pipeline=False, **kwargs
    ) -> "AutoMLJob":
        from azure.ai.ml._schema.automl.nlp_vertical.text_ner import TextNerSchema

        if inside_pipeline:
            from azure.ai.ml._schema.pipeline.automl_node import AutoMLTextNerNode

            return load_from_dict(AutoMLTextNerNode, data, context, additional_message, **kwargs)

        return load_from_dict(TextNerSchema, data, context, additional_message, **kwargs)

    def _to_dict(self, inside_pipeline=False) -> Dict:
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLTextNerNode
        from azure.ai.ml._schema.automl.nlp_vertical.text_ner import TextNerSchema

        if inside_pipeline:
            return AutoMLTextNerNode(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        else:
            return TextNerSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def __eq__(self, other):
        if not isinstance(other, TextNerJob):
            return NotImplemented

        if not super(TextNerJob, self).__eq__(other):
            return False

        return self.primary_metric == other.primary_metric

    def __ne__(self, other):
        return not self.__eq__(other)
