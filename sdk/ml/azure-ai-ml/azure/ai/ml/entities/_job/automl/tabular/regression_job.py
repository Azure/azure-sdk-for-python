# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-member

from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import AutoMLJob as RestAutoMLJob
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobBase
from azure.ai.ml._restclient.v2023_04_01_preview.models import Regression as RestRegression
from azure.ai.ml._restclient.v2023_04_01_preview.models import RegressionPrimaryMetrics, TaskType
from azure.ai.ml._utils.utils import camel_to_snake, is_data_binding_expression
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._job.automl import AutoMLConstants
from azure.ai.ml.entities._credentials import _BaseJobIdentityConfiguration
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, to_rest_data_outputs
from azure.ai.ml.entities._job.automl.tabular import AutoMLTabular, TabularFeaturizationSettings, TabularLimitSettings
from azure.ai.ml.entities._job.automl.training_settings import RegressionTrainingSettings
from azure.ai.ml.entities._util import load_from_dict


class RegressionJob(AutoMLTabular):
    """Configuration for AutoML Regression Job."""

    _DEFAULT_PRIMARY_METRIC = RegressionPrimaryMetrics.NORMALIZED_ROOT_MEAN_SQUARED_ERROR

    def __init__(
        self,
        *,
        primary_metric: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a new AutoML Regression task.

        :param primary_metric: The primary metric to use for optimization
        :type primary_metric: str
        :param kwargs: Job-specific arguments
        :type kwargs: dict
        """
        # Extract any task specific settings
        featurization = kwargs.pop("featurization", None)
        limits = kwargs.pop("limits", None)
        training = kwargs.pop("training", None)

        super().__init__(
            task_type=TaskType.REGRESSION,
            featurization=featurization,
            limits=limits,
            training=training,
            **kwargs,
        )

        self.primary_metric = primary_metric or RegressionJob._DEFAULT_PRIMARY_METRIC

    @property
    def primary_metric(self) -> Union[str, RegressionPrimaryMetrics]:
        return self._primary_metric

    @primary_metric.setter
    def primary_metric(self, value: Union[str, RegressionPrimaryMetrics]) -> None:
        # TODO: better way to do this
        if is_data_binding_expression(str(value), ["parent"]):
            self._primary_metric = value
            return
        self._primary_metric = (
            RegressionJob._DEFAULT_PRIMARY_METRIC
            if value is None
            else RegressionPrimaryMetrics[camel_to_snake(value).upper()]
        )

    @property
    def training(self) -> RegressionTrainingSettings:
        return self._training or RegressionTrainingSettings()

    @training.setter
    def training(self, value: Union[Dict, RegressionTrainingSettings]) -> None:  # pylint: disable=unused-argument
        ...

    def _to_rest_object(self) -> JobBase:
        regression_task = RestRegression(
            target_column_name=self.target_column_name,
            training_data=self.training_data,
            validation_data=self.validation_data,
            validation_data_size=self.validation_data_size,
            weight_column_name=self.weight_column_name,
            cv_split_column_names=self.cv_split_column_names,
            n_cross_validations=self.n_cross_validations,
            test_data=self.test_data,
            test_data_size=self.test_data_size,
            featurization_settings=self._featurization._to_rest_object() if self._featurization else None,
            limit_settings=self._limits._to_rest_object() if self._limits else None,
            training_settings=self._training._to_rest_object() if self._training else None,
            primary_metric=self.primary_metric,
            log_verbosity=self.log_verbosity,
        )
        self._resolve_data_inputs(regression_task)
        self._validation_data_to_rest(regression_task)

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
            task_details=regression_task,
            identity=self.identity._to_job_rest_object() if self.identity else None,
            queue_settings=self.queue_settings,
        )

        result = JobBase(properties=properties)
        result.name = self.name
        return result

    @classmethod
    def _from_rest_object(cls, obj: JobBase) -> "RegressionJob":
        properties: RestAutoMLJob = obj.properties
        task_details: RestRegression = properties.task_details

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
            "identity": (
                _BaseJobIdentityConfiguration._from_rest_object(properties.identity) if properties.identity else None
            ),
            "queue_settings": properties.queue_settings,
        }

        regression_job = cls(
            target_column_name=task_details.target_column_name,
            training_data=task_details.training_data,
            validation_data=task_details.validation_data,
            validation_data_size=task_details.validation_data_size,
            weight_column_name=task_details.weight_column_name,
            cv_split_column_names=task_details.cv_split_column_names,
            n_cross_validations=task_details.n_cross_validations,
            test_data=task_details.test_data,
            test_data_size=task_details.test_data_size,
            featurization=(
                TabularFeaturizationSettings._from_rest_object(task_details.featurization_settings)
                if task_details.featurization_settings
                else None
            ),
            limits=(
                TabularLimitSettings._from_rest_object(task_details.limit_settings)
                if task_details.limit_settings
                else None
            ),
            training=(
                RegressionTrainingSettings._from_rest_object(task_details.training_settings)
                if task_details.training_settings
                else None
            ),
            primary_metric=task_details.primary_metric,
            log_verbosity=task_details.log_verbosity,
            **job_args_dict,
        )

        regression_job._restore_data_inputs()
        regression_job._validation_data_from_rest()

        return regression_job

    @classmethod
    def _load_from_dict(
        cls,
        data: Dict,
        context: Dict,
        additional_message: str,
        **kwargs: Any,
    ) -> "RegressionJob":
        from azure.ai.ml._schema.automl.table_vertical.regression import AutoMLRegressionSchema
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLRegressionNodeSchema

        if kwargs.pop("inside_pipeline", False):
            loaded_data = load_from_dict(AutoMLRegressionNodeSchema, data, context, additional_message, **kwargs)
        else:
            loaded_data = load_from_dict(AutoMLRegressionSchema, data, context, additional_message, **kwargs)
        job_instance = cls._create_instance_from_schema_dict(loaded_data)
        return job_instance

    @classmethod
    def _create_instance_from_schema_dict(cls, loaded_data: Dict) -> "RegressionJob":
        loaded_data.pop(AutoMLConstants.TASK_TYPE_YAML, None)
        data_settings = {
            "training_data": loaded_data.pop("training_data"),
            "target_column_name": loaded_data.pop("target_column_name"),
            "weight_column_name": loaded_data.pop("weight_column_name", None),
            "validation_data": loaded_data.pop("validation_data", None),
            "validation_data_size": loaded_data.pop("validation_data_size", None),
            "cv_split_column_names": loaded_data.pop("cv_split_column_names", None),
            "n_cross_validations": loaded_data.pop("n_cross_validations", None),
            "test_data": loaded_data.pop("test_data", None),
            "test_data_size": loaded_data.pop("test_data_size", None),
        }
        job = RegressionJob(**loaded_data)
        job.set_data(**data_settings)
        return job

    def _to_dict(self, inside_pipeline: bool = False) -> Dict:  # pylint: disable=arguments-differ
        from azure.ai.ml._schema.automl.table_vertical.regression import AutoMLRegressionSchema
        from azure.ai.ml._schema.pipeline.automl_node import AutoMLRegressionNodeSchema

        schema_dict: dict = {}
        if inside_pipeline:
            schema_dict = AutoMLRegressionNodeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        else:
            schema_dict = AutoMLRegressionSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

        return schema_dict

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RegressionJob):
            return NotImplemented

        if not super(RegressionJob, self).__eq__(other):
            return False

        return self.primary_metric == other.primary_metric

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
