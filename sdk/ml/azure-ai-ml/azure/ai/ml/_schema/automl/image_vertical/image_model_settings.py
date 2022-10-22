# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    LearningRateScheduler,
    ModelSize,
    StochasticOptimizer,
    ValidationMetricType,
)
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._job.automl import (
    ImageClassificationModelNames,
    ImageInstanceSegmentationModelNames,
    ImageObjectDetectionModelNames,
)


class ImageModelSettingsSchema(metaclass=PatchedSchemaMeta):
    ams_gradient = fields.Bool()
    advanced_settings = fields.Str()
    beta1 = fields.Float()
    beta2 = fields.Float()
    checkpoint_frequency = fields.Int()
    checkpoint_run_id = fields.Str()
    distributed = fields.Bool()
    early_stopping = fields.Bool()
    early_stopping_delay = fields.Int()
    early_stopping_patience = fields.Int()
    evaluation_frequency = fields.Int()
    enable_onnx_normalization = fields.Bool()
    gradient_accumulation_step = fields.Int()
    layers_to_freeze = fields.Int()
    learning_rate = fields.Float()
    learning_rate_scheduler = StringTransformedEnum(
        allowed_values=[o.value for o in LearningRateScheduler],
        casing_transform=camel_to_snake,
    )
    momentum = fields.Float()
    nesterov = fields.Bool()
    number_of_epochs = fields.Int()
    number_of_workers = fields.Int()
    optimizer = StringTransformedEnum(
        allowed_values=[o.value for o in StochasticOptimizer],
        casing_transform=camel_to_snake,
    )
    random_seed = fields.Int()
    step_lr_gamma = fields.Float()
    step_lr_step_size = fields.Int()
    training_batch_size = fields.Int()
    validation_batch_size = fields.Int()
    warmup_cosine_lr_cycles = fields.Float()
    warmup_cosine_lr_warmup_epochs = fields.Int()
    weight_decay = fields.Float()


class ImageModelSettingsClassificationSchema(ImageModelSettingsSchema):
    model_name = StringTransformedEnum(
        allowed_values=[o.value for o in ImageClassificationModelNames],
    )
    training_crop_size = fields.Int()
    validation_crop_size = fields.Int()
    validation_resize_size = fields.Int()
    weighted_loss = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._job.automl.image.image_model_settings import ImageModelSettingsClassification
        return ImageModelSettingsClassification(**data)


class ImageDetectionSegmentationCommonSchema(ImageModelSettingsSchema):
    box_detections_per_image = fields.Int()
    box_score_threshold = fields.Float()
    image_size = fields.Int()
    max_size = fields.Int()
    min_size = fields.Int()
    model_size = StringTransformedEnum(allowed_values=[o.value for o in ModelSize], casing_transform=camel_to_snake)
    multi_scale = fields.Bool()
    nms_iou_threshold = fields.Float()
    tile_grid_size = fields.Str()
    tile_overlap_ratio = fields.Float()
    tile_predictions_nms_threshold = fields.Float()
    validation_iou_threshold = fields.Float()
    validation_metric_type = StringTransformedEnum(
        allowed_values=[o.value for o in ValidationMetricType],
        casing_transform=camel_to_snake,
    )


class ImageModelSettingsObjectDetectionSchema(ImageDetectionSegmentationCommonSchema):
    model_name = StringTransformedEnum(
        allowed_values=[o.value for o in ImageObjectDetectionModelNames],
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._job.automl.image.image_model_settings import ImageModelSettingsObjectDetection
        return ImageModelSettingsObjectDetection(**data)


class ImageModelSettingsInstanceSegmentationSchema(ImageDetectionSegmentationCommonSchema):
    model_name = StringTransformedEnum(
        allowed_values=[o.value for o in ImageInstanceSegmentationModelNames],
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._job.automl.image.image_model_settings import ImageModelSettingsObjectDetection
        return ImageModelSettingsObjectDetection(**data)
