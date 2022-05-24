# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load, pre_dump
from azure.ai.ml._schema import PatchedSchemaMeta


class ImageModelDistributionSettingsSchema(metaclass=PatchedSchemaMeta):
    ams_gradient = fields.Str()
    augmentations = fields.Str()
    beta1 = fields.Str()
    beta2 = fields.Str()
    distributed = fields.Str()
    early_stopping = fields.Str()
    early_stopping_delay = fields.Str()
    early_stopping_patience = fields.Str()
    evaluation_frequency = fields.Str()
    enable_onnx_normalization = fields.Str()
    gradient_accumulation_step = fields.Str(data_key="grad_accumulation_step")
    layers_to_freeze = fields.Str()
    learning_rate = fields.Str()
    learning_rate_scheduler = fields.Str()
    model_name = fields.Str()
    momentum = fields.Str()
    nesterov = fields.Str()
    number_of_epochs = fields.Str()
    number_of_workers = fields.Str()
    optimizer = fields.Str()
    random_seed = fields.Str()
    split_ratio = fields.Str()
    step_lr_gamma = fields.Str()
    step_lr_step_size = fields.Str()
    training_batch_size = fields.Str()
    validation_batch_size = fields.Str()
    warmup_cosine_lr_cycles = fields.Str()
    warmup_cosine_lr_warmup_epochs = fields.Str()
    weight_decay = fields.Str()


class ImageModelDistributionSettingsClassificationSchema(ImageModelDistributionSettingsSchema):
    training_crop_size = fields.Str()
    validation_crop_size = fields.Str()
    validation_resize_size = fields.Str()
    weighted_loss = fields.Str()

    @pre_dump
    def conversion(self, data, **kwargs):
        return data._to_rest_object()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import ImageClassificationSearchSpace

        return ImageClassificationSearchSpace(**data)


class ImageModelDistributionSettingsObjectDetectionSchema(ImageModelDistributionSettingsSchema):
    box_detections_per_image = fields.Str()
    box_score_threshold = fields.Str()
    image_size = fields.Str()
    max_size = fields.Str()
    min_size = fields.Str()
    model_size = fields.Str()
    multi_scale = fields.Str()
    nms_iou_threshold = fields.Str()
    tile_grid_size = fields.Str()
    tile_overlap_ratio = fields.Str()
    tile_predictions_nms_threshold = fields.Str()
    validation_iou_threshold = fields.Str()
    validation_metric_type = fields.Str()

    @pre_dump
    def conversion(self, data, **kwargs):
        return data._to_rest_object()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import ImageObjectDetectionSearchSpace

        return ImageObjectDetectionSearchSpace(**data)
