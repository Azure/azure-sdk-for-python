# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._schema.core.fields import NestedField
from marshmallow import post_load
from azure.ai.ml.constants import AutoMLConstants
from azure.ai.ml._schema import StringTransformedEnum
from azure.ai.ml._schema.automl.table_vertical.table_vertical import AutoMLTableVerticalSchema
from azure.ai.ml._schema.automl.training_settings import RegressionTrainingSettingsSchema
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    RegressionPrimaryMetrics,
    TaskType,
)


class AutoMLRegressionSchema(AutoMLTableVerticalSchema):
    task_type = StringTransformedEnum(
        allowed_values=TaskType.REGRESSION,
        casing_transform=camel_to_snake,
        data_key=AutoMLConstants.TASK_TYPE_YAML,
        required=True,
    )
    primary_metric = StringTransformedEnum(
        allowed_values=[o.value for o in RegressionPrimaryMetrics],
        casing_transform=camel_to_snake,
        load_default=camel_to_snake(RegressionPrimaryMetrics.NORMALIZED_ROOT_MEAN_SQUARED_ERROR),
    )
    training = NestedField(RegressionTrainingSettingsSchema(), data_key=AutoMLConstants.TRAINING_YAML)

    @post_load
    def make(self, data, **kwargs) -> "RegressionJob":
        from azure.ai.ml.entities._job.automl.tabular import RegressionJob

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
        job = RegressionJob(**loaded_data)
        job.set_data(**data_settings)
        return job
