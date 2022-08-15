# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from typing import Any, Dict

from marshmallow import post_load

from azure.ai.ml._restclient.v2022_02_01_preview.models import ClassificationPrimaryMetrics, TaskType
from azure.ai.ml._schema.automl.nlp_vertical.nlp_vertical import NlpVerticalSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum, fields
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import AutoMLConstants


class TextNerSchema(NlpVerticalSchema):
    task_type = StringTransformedEnum(
        allowed_values=TaskType.TEXT_NER,
        casing_transform=camel_to_snake,
        data_key=AutoMLConstants.TASK_TYPE_YAML,
        required=True,
    )
    primary_metric = StringTransformedEnum(
        allowed_values=ClassificationPrimaryMetrics.ACCURACY,
        casing_transform=camel_to_snake,
        load_default=camel_to_snake(ClassificationPrimaryMetrics.ACCURACY),
    )
    target_column_name = fields.Str()

    @post_load
    def make(self, data, **kwargs) -> Dict[str, Any]:

        data.pop("task_type")
        return data
