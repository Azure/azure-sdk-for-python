# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from typing import Any, Dict

from marshmallow import post_load

from azure.ai.ml._restclient.v2022_02_01_preview.models import RegressionPrimaryMetrics, TaskType
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.automl.table_vertical.table_vertical import AutoMLTableVerticalSchema
from azure.ai.ml._schema.automl.training_settings import RegressionTrainingSettingsSchema
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import AutoMLConstants


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
    def make(self, data, **kwargs) -> Dict[str, Any]:

        data.pop("task_type")
        return data
