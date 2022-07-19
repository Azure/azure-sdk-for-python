# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml.constants import AutoMLConstants
from azure.ai.ml._schema.automl.image_vertical.image_model_distribution_settings import (
    ImageModelDistributionSettingsClassificationSchema,
)
from azure.ai.ml._schema.automl.image_vertical.image_model_settings import ImageModelSettingsClassificationSchema
from azure.ai.ml._schema.automl.image_vertical.image_vertical import ImageVerticalSchema
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from marshmallow import fields, post_load
from azure.ai.ml._schema import NestedField
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ClassificationPrimaryMetrics,
    ClassificationMultilabelPrimaryMetrics,
    TaskType,
)
from azure.ai.ml._utils.utils import camel_to_snake


class ImageClassificationBaseSchema(ImageVerticalSchema):
    image_model = NestedField(ImageModelSettingsClassificationSchema())
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
    def make(self, data, **kwargs) -> "ImageClassificationJob":
        from azure.ai.ml.entities._job.automl.image import ImageClassificationJob

        data.pop("task_type")
        loaded_data = data
        search_space_val = data.pop("search_space", None)
        search_space = ImageClassificationJob._get_search_space_from_str(search_space_val)
        data_settings = {
            "training_data": loaded_data.pop("training_data"),
            "target_column_name": loaded_data.pop("target_column_name"),
            "validation_data": loaded_data.pop("validation_data", None),
            "validation_data_size": loaded_data.pop("validation_data_size", None),
        }
        job = ImageClassificationJob(search_space=search_space, **loaded_data)
        job.set_data(**data_settings)
        return job


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
    def make(self, data, **kwargs) -> "ImageClassificationMultilabelJob":
        from azure.ai.ml.entities._job.automl.image import ImageClassificationMultilabelJob

        data.pop("task_type")
        loaded_data = data
        search_space_val = data.pop("search_space", None)
        search_space = ImageClassificationMultilabelJob._get_search_space_from_str(search_space_val)
        data_settings = {
            "training_data": loaded_data.pop("training_data"),
            "target_column_name": loaded_data.pop("target_column_name"),
            "validation_data": loaded_data.pop("validation_data", None),
            "validation_data_size": loaded_data.pop("validation_data_size", None),
        }
        job = ImageClassificationMultilabelJob(search_space=search_space, **loaded_data)
        job.set_data(**data_settings)
        return job
