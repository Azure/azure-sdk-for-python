# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import post_load
from azure.ai.ml.constants import AutoMLConstants
from azure.ai.ml._schema import StringTransformedEnum
from azure.ai.ml._schema.core.fields import NestedField

from azure.ai.ml._schema.automl.table_vertical.table_vertical import AutoMLTableVerticalSchema
from azure.ai.ml._schema.automl.forecasting_settings import ForecastingSettingsSchema
from azure.ai.ml._schema.automl.training_settings import ForecastingTrainingSettingsSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ForecastingPrimaryMetrics,
    TaskType,
)


@experimental
class AutoMLForecastingSchema(AutoMLTableVerticalSchema):
    task_type = StringTransformedEnum(
        allowed_values=TaskType.FORECASTING,
        casing_transform=camel_to_snake,
        data_key=AutoMLConstants.TASK_TYPE_YAML,
        required=True,
    )
    primary_metric = StringTransformedEnum(
        allowed_values=[o.value for o in ForecastingPrimaryMetrics],
        casing_transform=camel_to_snake,
        load_default=camel_to_snake(ForecastingPrimaryMetrics.NORMALIZED_ROOT_MEAN_SQUARED_ERROR),
    )
    training = NestedField(ForecastingTrainingSettingsSchema(), data_key=AutoMLConstants.TRAINING_YAML)
    forecasting_settings = NestedField(ForecastingSettingsSchema(), data_key=AutoMLConstants.FORECASTING_YAML)

    @post_load
    def make(self, data, **kwargs) -> "ForecastingJob":
        from azure.ai.ml.entities._job.automl.tabular import ForecastingJob

        data.pop("task_type")
        loaded_data = data
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
        job = ForecastingJob(**loaded_data)
        job.set_data(**data_settings)
        return job
