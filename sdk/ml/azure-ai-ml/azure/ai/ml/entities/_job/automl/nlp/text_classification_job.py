# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-member

from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2022_10_01_preview.models import JobBase, TaskType
from azure.ai.ml._restclient.v2022_10_01_preview.models import TextClassification as RestTextClassification
from azure.ai.ml._restclient.v2022_10_01_preview.models._azure_machine_learning_workspaces_enums import (
    ClassificationPrimaryMetrics,
)
from azure.ai.ml._utils.utils import camel_to_snake, is_data_binding_expression
from azure.ai.ml.constants._job.automl import AutoMLConstants
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._credentials import _BaseJobIdentityConfiguration
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs
from azure.ai.ml.entities._job.automl.nlp.automl_nlp_job import AutoMLNLPJob
from azure.ai.ml.entities._job.automl.nlp.nlp_featurization_settings import NlpFeaturizationSettings
from azure.ai.ml.entities._job.automl.nlp.nlp_fixed_parameters import NlpFixedParameters
from azure.ai.ml.entities._job.automl.nlp.nlp_limit_settings import NlpLimitSettings
from azure.ai.ml.entities._job.automl.nlp.nlp_sweep_settings import NlpSweepSettings
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict


class TextClassificationJob(AutoMLNLPJob):
    """Configuration for AutoML Text Classification Job."""

    _DEFAULT_PRIMARY_METRIC = ClassificationPrimaryMetrics.ACCURACY

    def __init__(
        self,
        *,
        target_column_name: str = None,
        training_data: Input = None,
        validation_data: Input = None,
        primary_metric: Optional[ClassificationPrimaryMetrics] = None,
        log_verbosity: Optional[str] = None,
        **kwargs
    ):
        """Initializes a new AutoML Text Classification task.

        :param target_column_name: The name of the target column
        :param training_data: Training data to be used for training
        :param validation_data: Validation data to be used for evaluating the trained model
        :param primary_metric: The primary metric to be displayed
        :param log_verbosity: Log verbosity level
        :param kwargs: Job-specific arguments
        """
        super().__init__(
            task_type=TaskType.TEXT_CLASSIFICATION,
            primary_metric=primary_metric or TextClassificationJob._DEFAULT_PRIMARY_METRIC,
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
            TextClassificationJob._DEFAULT_PRIMARY_METRIC
            if value is None
            else ClassificationPrimaryMetrics[camel_to_snake(value).upper()]
        )

    def _to_rest_object(self) -> JobBase:
        text_classification = RestTextClassification(
            target_column_name=self.target_column_name,
            training_data=self.training_data,
            validation_data=self.validation_data,
            limit_settings=self._limits._to_rest_object() if self._limits else None,
            sweep_settings=self._sweep._to_rest_object() if self._sweep else None,
            fixed_parameters=self._training_parameters._to_rest_object() if self._training_parameters else None,
            search_space=(
                [entry._to_rest_object() for entry in self._search_space if entry is not None]
                if self._search_space is not None
                else None
            ),
            featurization_settings=self._featurization._to_rest_object() if self._featurization else None,
            primary_metric=self.primary_metric,
            log_verbosity=self.log_verbosity,
        )
        # resolve data inputs in rest object
        self._resolve_data_inputs(text_classification)

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
            identity=self.identity._to_ob_rest_object() if self.identity else None,
        )

        result = JobBase(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _from_rest_object(cls, obj: JobBase) -> "TextClassificationJob":
        properties: RestAutoMLJob = obj.properties
        task_details: RestTextClassification = properties.task_details
        assert isinstance(task_details, RestTextClassification)
        limits = (
            NlpLimitSettings._from_rest_object(task_details.limit_settings) if task_details.limit_settings else None
        )
        featurization = (
            NlpFeaturizationSettings._from_rest_object(task_details.featurization_settings)
            if task_details.featurization_settings
            else None
        )
        sweep = (
            NlpSweepSettings._from_rest_object(task_details.sweep_settings)
            if task_details.sweep_settings
            else None
        )
        training_parameters = (
            NlpFixedParameters._from_rest_object(task_details.fixed_parameters)
            if task_details.fixed_parameters
            else None
        )

        text_classification_job = cls(
            # ----- job specific params
            id=obj.id,
            name=obj.name,
            description=properties.description,
            tags=properties.tags,
            properties=properties.properties,
            experiment_name=properties.experiment_name,
            services=properties.services,
            status=properties.status,
            creation_context=SystemData._from_rest_object(obj.system_data) if obj.system_data else None,
            display_name=properties.display_name,
            compute=properties.compute_id,
            outputs=from_rest_data_outputs(properties.outputs),
            resources=properties.resources,
            # ----- task specific params
            primary_metric=task_details.primary_metric,
            log_verbosity=task_details.log_verbosity,
            target_column_name=task_details.target_column_name,
            training_data=task_details.training_data,
            validation_data=task_details.validation_data,
            limits=limits,
            sweep=sweep,
            training_parameters=training_parameters,
            search_space=cls._get_search_space_from_str(task_details.search_space),
            featurization=featurization,
            identity=_BaseJobIdentityConfiguration._from_rest_object(
                properties.identity) if properties.identity else None,
        )

        text_classification_job._restore_data_inputs()

        return text_classification_job

    def _to_component(self, context: Dict = None, **kwargs) -> "Component":
        raise NotImplementedError()

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "TextClassificationJob":
        from azure.ai.ml._schema.automl.nlp_vertical.text_classification import TextClassificationSchema

        if kwargs.pop("inside_pipeline", False):
            from azure.ai.ml._schema.pipeline.automl_node import AutoMLTextClassificationNode

            loaded_data = load_from_dict(
                AutoMLTextClassificationNode,
                data,
                context,
                additional_message,
                **kwargs,
            )
        else:
            loaded_data = load_from_dict(TextClassificationSchema, data, context, additional_message, **kwargs)
        job_instance = cls._create_instance_from_schema_dict(loaded_data)
        return job_instance

    @classmethod
    def _create_instance_from_schema_dict(cls, loaded_data: Dict) -> "TextClassificationJob":
        loaded_data.pop(AutoMLConstants.TASK_TYPE_YAML, None)
        return TextClassificationJob(**loaded_data)

    def _to_dict(self, inside_pipeline=False) -> Dict:  # pylint: disable=arguments-differ
        from azure.ai.ml._schema.automl.nlp_vertical.text_classification import TextClassificationSchema
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLTextClassificationNode

        if inside_pipeline:
            return AutoMLTextClassificationNode(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

        return TextClassificationSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def __eq__(self, other):
        if not isinstance(other, TextClassificationJob):
            return NotImplemented

        if not super(TextClassificationJob, self).__eq__(other):
            return False

        return self.primary_metric == other.primary_metric

    def __ne__(self, other):
        return not self.__eq__(other)
