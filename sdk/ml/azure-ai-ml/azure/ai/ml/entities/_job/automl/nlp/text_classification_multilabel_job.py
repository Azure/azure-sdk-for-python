# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-member

from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2023_04_01_preview.models import ClassificationMultilabelPrimaryMetrics, JobBase, TaskType
from azure.ai.ml._restclient.v2024_01_01_preview.models import (
    TextClassificationMultilabel as RestTextClassificationMultilabel,
)
from azure.ai.ml._utils.utils import camel_to_snake, is_data_binding_expression
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._job.automl import AutoMLConstants
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

# avoid circular import error
if TYPE_CHECKING:
    from azure.ai.ml.entities._component.component import Component


class TextClassificationMultilabelJob(AutoMLNLPJob):
    """Configuration for AutoML Text Classification Multilabel Job.

    :param target_column_name: The name of the target column, defaults to None
    :type target_column_name: Optional[str]
    :param training_data: Training data to be used for training, defaults to None
    :type training_data: Optional[~azure.ai.ml.Input]
    :param validation_data: Validation data to be used for evaluating the trained model, defaults to None
    :type validation_data: Optional[~azure.ai.ml.Input]
    :param primary_metric: The primary metric to be displayed., defaults to None
    :type primary_metric: Optional[str]
    :param log_verbosity: Log verbosity level, defaults to None
    :type log_verbosity: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_automl_nlp.py
                :start-after: [START automl.text_classification_multilabel_job]
                :end-before: [END automl.text_classification_multilabel_job]
                :language: python
                :dedent: 8
                :caption: creating an automl text classification multilabel job
    """

    _DEFAULT_PRIMARY_METRIC = ClassificationMultilabelPrimaryMetrics.ACCURACY

    def __init__(
        self,
        *,
        target_column_name: Optional[str] = None,
        training_data: Optional[Input] = None,
        validation_data: Optional[Input] = None,
        primary_metric: Optional[str] = None,
        log_verbosity: Optional[str] = None,
        **kwargs: Any
    ):
        super().__init__(
            task_type=TaskType.TEXT_CLASSIFICATION_MULTILABEL,
            primary_metric=primary_metric or TextClassificationMultilabelJob._DEFAULT_PRIMARY_METRIC,
            target_column_name=target_column_name,
            training_data=training_data,
            validation_data=validation_data,
            log_verbosity=log_verbosity,
            **kwargs,
        )

    @property
    def primary_metric(self) -> Union[str, ClassificationMultilabelPrimaryMetrics]:
        return self._primary_metric

    @primary_metric.setter
    def primary_metric(self, value: Union[str, ClassificationMultilabelPrimaryMetrics]) -> None:
        if is_data_binding_expression(str(value), ["parent"]):
            self._primary_metric = value
            return

        self._primary_metric = (
            TextClassificationMultilabelJob._DEFAULT_PRIMARY_METRIC
            if value is None
            else ClassificationMultilabelPrimaryMetrics[camel_to_snake(value).upper()]
        )

    def _to_rest_object(self) -> JobBase:
        text_classification_multilabel = RestTextClassificationMultilabel(
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
        self._resolve_data_inputs(text_classification_multilabel)

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
            task_details=text_classification_multilabel,
            identity=self.identity._to_job_rest_object() if self.identity else None,
            queue_settings=self.queue_settings,
        )

        result = JobBase(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _from_rest_object(cls, obj: JobBase) -> "TextClassificationMultilabelJob":
        properties: RestAutoMLJob = obj.properties
        task_details: RestTextClassificationMultilabel = properties.task_details
        assert isinstance(task_details, RestTextClassificationMultilabel)
        limits = (
            NlpLimitSettings._from_rest_object(task_details.limit_settings) if task_details.limit_settings else None
        )
        featurization = (
            NlpFeaturizationSettings._from_rest_object(task_details.featurization_settings)
            if task_details.featurization_settings
            else None
        )
        sweep = NlpSweepSettings._from_rest_object(task_details.sweep_settings) if task_details.sweep_settings else None
        training_parameters = (
            NlpFixedParameters._from_rest_object(task_details.fixed_parameters)
            if task_details.fixed_parameters
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
            identity=(
                _BaseJobIdentityConfiguration._from_rest_object(properties.identity) if properties.identity else None
            ),
            queue_settings=properties.queue_settings,
        )

        text_classification_multilabel_job._restore_data_inputs()

        return text_classification_multilabel_job

    def _to_component(self, context: Optional[Dict] = None, **kwargs: Any) -> "Component":
        raise NotImplementedError()

    @classmethod
    def _load_from_dict(
        cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any
    ) -> "TextClassificationMultilabelJob":
        from azure.ai.ml._schema.automl.nlp_vertical.text_classification_multilabel import (
            TextClassificationMultilabelSchema,
        )

        if kwargs.pop("inside_pipeline", False):
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

    def _to_dict(self, inside_pipeline: bool = False) -> Dict:  # pylint: disable=arguments-differ
        from azure.ai.ml._schema.automl.nlp_vertical.text_classification_multilabel import (
            TextClassificationMultilabelSchema,
        )
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLTextClassificationMultilabelNode

        if inside_pipeline:
            res_autoML: dict = AutoMLTextClassificationMultilabelNode(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
            return res_autoML

        res: dict = TextClassificationMultilabelSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TextClassificationMultilabelJob):
            return NotImplemented

        if not super(TextClassificationMultilabelJob, self).__eq__(other):
            return False

        return self.primary_metric == other.primary_metric

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
