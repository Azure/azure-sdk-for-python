# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from typing import Any, Dict

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    ClassificationMultilabelPrimaryMetrics,
    ClassificationPrimaryMetrics,
    TaskType,
)
from azure.ai.ml._schema.automl.image_vertical.image_model_distribution_settings import (
    ImageModelDistributionSettingsClassificationSchema,
)
from azure.ai.ml._schema.automl.image_vertical.image_model_settings import ImageModelSettingsClassificationSchema
from azure.ai.ml._schema.automl.image_vertical.image_vertical import ImageVerticalSchema
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._job.automl import AutoMLConstants


class ImageClassificationBaseSchema(ImageVerticalSchema):
    training_parameters = NestedField(ImageModelSettingsClassificationSchema())
    search_space = fields.List(NestedField(ImageModelDistributionSettingsClassificationSchema()))


class ImageClassificationSchema(ImageClassificationBaseSchema):
    task_type = StringTransformedEnum(
        allowed_values=TaskType.IMAGE_CLASSIFICATION,
        casing_transform=camel_to_snake,
        data_key=AutoMLConstants.TASK_TYPE_YAML,
        required=True,
    )
    primary_metric = StringTransformedEnum(
        allowed_values=[o.value for o in ClassificationPrimaryMetrics],
        casing_transform=camel_to_snake,
        load_default=camel_to_snake(ClassificationPrimaryMetrics.Accuracy),
    )

    @post_load
    def make(self, data, **kwargs) -> Dict[str, Any]:
        data.pop("task_type")
        return data


class ImageClassificationMultilabelSchema(ImageClassificationBaseSchema):
    task_type = StringTransformedEnum(
        allowed_values=TaskType.IMAGE_CLASSIFICATION_MULTILABEL,
        casing_transform=camel_to_snake,
        data_key=AutoMLConstants.TASK_TYPE_YAML,
        required=True,
    )
    primary_metric = StringTransformedEnum(
        allowed_values=[o.value for o in ClassificationMultilabelPrimaryMetrics],
        casing_transform=camel_to_snake,
        load_default=camel_to_snake(ClassificationMultilabelPrimaryMetrics.IOU),
    )

    @post_load
    def make(self, data, **kwargs) -> Dict[str, Any]:
        data.pop("task_type")
        return data
