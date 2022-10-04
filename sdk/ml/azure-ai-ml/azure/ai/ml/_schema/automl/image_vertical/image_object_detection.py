# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from typing import Any, Dict

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    InstanceSegmentationPrimaryMetrics,
    ObjectDetectionPrimaryMetrics,
    TaskType,
)
from azure.ai.ml._schema.automl.image_vertical.image_model_distribution_settings import (
    ImageModelDistributionSettingsInstanceSegmentationSchema,
    ImageModelDistributionSettingsObjectDetectionSchema,
)
from azure.ai.ml._schema.automl.image_vertical.image_model_settings import (
    ImageModelSettingsInstanceSegmentationSchema,
    ImageModelSettingsObjectDetectionSchema,
)
from azure.ai.ml._schema.automl.image_vertical.image_vertical import ImageVerticalSchema
from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._job.automl import AutoMLConstants


class ImageObjectDetectionSchema(ImageVerticalSchema):
    task_type = StringTransformedEnum(
        allowed_values=TaskType.IMAGE_OBJECT_DETECTION,
        casing_transform=camel_to_snake,
        data_key=AutoMLConstants.TASK_TYPE_YAML,
        required=True,
    )
    primary_metric = StringTransformedEnum(
        allowed_values=ObjectDetectionPrimaryMetrics.MEAN_AVERAGE_PRECISION,
        casing_transform=camel_to_snake,
        load_default=camel_to_snake(ObjectDetectionPrimaryMetrics.MEAN_AVERAGE_PRECISION),
    )
    training_parameters = NestedField(ImageModelSettingsObjectDetectionSchema())
    search_space = fields.List(NestedField(ImageModelDistributionSettingsObjectDetectionSchema()))

    @post_load
    def make(self, data, **kwargs) -> Dict[str, Any]:
        data.pop("task_type")
        return data


class ImageInstanceSegmentationSchema(ImageVerticalSchema):
    task_type = StringTransformedEnum(
        allowed_values=TaskType.IMAGE_INSTANCE_SEGMENTATION,
        casing_transform=camel_to_snake,
        data_key=AutoMLConstants.TASK_TYPE_YAML,
        required=True,
    )
    primary_metric = StringTransformedEnum(
        allowed_values=[InstanceSegmentationPrimaryMetrics.MEAN_AVERAGE_PRECISION],
        casing_transform=camel_to_snake,
        load_default=camel_to_snake(InstanceSegmentationPrimaryMetrics.MEAN_AVERAGE_PRECISION),
    )
    training_parameters = NestedField(ImageModelSettingsInstanceSegmentationSchema())
    search_space = fields.List(NestedField(ImageModelDistributionSettingsInstanceSegmentationSchema()))

    @post_load
    def make(self, data, **kwargs) -> Dict[str, Any]:
        data.pop("task_type")
        return data
