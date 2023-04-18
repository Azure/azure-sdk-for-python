# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from typing import Any, Dict

from marshmallow import post_load

from azure.ai.ml._restclient.v2023_04_01_preview.models import ClassificationMultilabelPrimaryMetrics, TaskType
from azure.ai.ml._schema.automl.nlp_vertical.nlp_vertical import NlpVerticalSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum, fields
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._job.automl import AutoMLConstants


class TextClassificationMultilabelSchema(NlpVerticalSchema):
    task_type = StringTransformedEnum(
        allowed_values=TaskType.TEXT_CLASSIFICATION_MULTILABEL,
        casing_transform=camel_to_snake,
        data_key=AutoMLConstants.TASK_TYPE_YAML,
        required=True,
    )
    primary_metric = StringTransformedEnum(
        allowed_values=ClassificationMultilabelPrimaryMetrics.ACCURACY,
        casing_transform=camel_to_snake,
        load_default=camel_to_snake(ClassificationMultilabelPrimaryMetrics.ACCURACY),
    )
    # added here as for text_ner target_column_name is optional
    target_column_name = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs) -> Dict[str, Any]:
        data.pop("task_type")
        return data
