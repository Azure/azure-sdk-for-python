# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml.constants import AutoMLConstants
from azure.ai.ml._schema.automl.image_vertical.image_vertical import ImageVerticalSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from marshmallow import fields, post_load
from azure.ai.ml._schema import NestedField
from azure.ai.ml._schema.automl.image_vertical.image_model_distribution_settings import (
    ImageModelDistributionSettingsObjectDetectionSchema,
)
from azure.ai.ml._schema.automl.image_vertical.image_model_settings import ImageModelSettingsObjectDetectionSchema
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    InstanceSegmentationPrimaryMetrics,
    ObjectDetectionPrimaryMetrics,
    TaskType,
)
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils.utils import camel_to_snake


class ImageObjectDetectionBaseSchema(ImageVerticalSchema):
    image_model = NestedField(ImageModelSettingsObjectDetectionSchema())
    search_space = fields.List(NestedField(ImageModelDistributionSettingsObjectDetectionSchema()))


@experimental
class ImageObjectDetectionSchema(ImageObjectDetectionBaseSchema):
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

    @post_load
    def make(self, data, **kwargs) -> "ImageObjectDetectionJob":
        from azure.ai.ml.entities._job.automl.image import ImageObjectDetectionJob

        data.pop("task_type")
        loaded_data = data
        search_space_val = data.pop("search_space")
        search_space = ImageObjectDetectionJob._get_search_space_from_str(search_space_val)
        data_settings = {
            "training_data": loaded_data.pop("training_data"),
            "target_column_name": loaded_data.pop("target_column_name"),
            "validation_data": loaded_data.pop("validation_data", None),
            "validation_data_size": loaded_data.pop("validation_data_size", None),
        }
        job = ImageObjectDetectionJob(search_space=search_space, **loaded_data)
        job.set_data(**data_settings)
        return job


@experimental
class ImageInstanceSegmentationSchema(ImageObjectDetectionBaseSchema):
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

    @post_load
    def make(self, data, **kwargs) -> "ImageInstanceSegmentationJob":
        from azure.ai.ml.entities._job.automl.image import ImageInstanceSegmentationJob

        data.pop("task_type")
        loaded_data = data
        search_space_val = data.pop("search_space")
        search_space = ImageInstanceSegmentationJob._get_search_space_from_str(search_space_val)
        data_settings = {
            "training_data": loaded_data.pop("training_data"),
            "target_column_name": loaded_data.pop("target_column_name"),
            "validation_data": loaded_data.pop("validation_data", None),
            "validation_data_size": loaded_data.pop("validation_data_size", None),
        }
        job = ImageInstanceSegmentationJob(search_space=search_space, **loaded_data)
        job.set_data(**data_settings)
        return job
