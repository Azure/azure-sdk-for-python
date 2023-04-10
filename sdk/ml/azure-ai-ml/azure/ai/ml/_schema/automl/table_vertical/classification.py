# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from typing import Any, Dict

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2023_04_01_preview.models import ClassificationPrimaryMetrics, TaskType
from azure.ai.ml._schema.automl.table_vertical.table_vertical import AutoMLTableVerticalSchema
from azure.ai.ml._schema.automl.training_settings import ClassificationTrainingSettingsSchema
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._job.automl import AutoMLConstants


class AutoMLClassificationSchema(AutoMLTableVerticalSchema):
    task_type = StringTransformedEnum(
        allowed_values=TaskType.CLASSIFICATION,
        casing_transform=camel_to_snake,
        data_key=AutoMLConstants.TASK_TYPE_YAML,
        required=True,
    )
    primary_metric = StringTransformedEnum(
        allowed_values=[o.value for o in ClassificationPrimaryMetrics],
        casing_transform=camel_to_snake,
        load_default=camel_to_snake(ClassificationPrimaryMetrics.AUC_WEIGHTED),
    )
    positive_label = fields.Str()
    training = NestedField(ClassificationTrainingSettingsSchema(), data_key=AutoMLConstants.TRAINING_YAML)

    @post_load
    def make(self, data, **kwargs) -> Dict[str, Any]:
        data.pop("task_type")
        return data
