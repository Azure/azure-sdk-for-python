# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use,protected-access

from marshmallow import fields, post_dump, post_load, pre_load

from azure.ai.ml._schema._sweep.search_space import (
    ChoiceSchema,
    NormalSchema,
    QNormalSchema,
    QUniformSchema,
    RandintSchema,
    UniformSchema,
)
from azure.ai.ml._schema.core.fields import NestedField, UnionField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta

SEARCH_SPACE_UNION_FIELD = UnionField(
    [
        NestedField(ChoiceSchema()),
        NestedField(UniformSchema()),
        NestedField(QUniformSchema()),
        NestedField(NormalSchema()),
        NestedField(QNormalSchema()),
        NestedField(RandintSchema()),
    ]
)


class ImageModelDistributionSettingsSchema(metaclass=PatchedSchemaMeta):
    ams_gradient = SEARCH_SPACE_UNION_FIELD
    augmentations = SEARCH_SPACE_UNION_FIELD
    beta1 = SEARCH_SPACE_UNION_FIELD
    beta2 = SEARCH_SPACE_UNION_FIELD
    distributed = SEARCH_SPACE_UNION_FIELD
    early_stopping = SEARCH_SPACE_UNION_FIELD
    early_stopping_delay = SEARCH_SPACE_UNION_FIELD
    early_stopping_patience = SEARCH_SPACE_UNION_FIELD
    evaluation_frequency = SEARCH_SPACE_UNION_FIELD
    enable_onnx_normalization = SEARCH_SPACE_UNION_FIELD
    gradient_accumulation_step = SEARCH_SPACE_UNION_FIELD
    layers_to_freeze = SEARCH_SPACE_UNION_FIELD
    learning_rate = SEARCH_SPACE_UNION_FIELD
    learning_rate_scheduler = SEARCH_SPACE_UNION_FIELD
    model_name = SEARCH_SPACE_UNION_FIELD
    momentum = SEARCH_SPACE_UNION_FIELD
    nesterov = SEARCH_SPACE_UNION_FIELD
    number_of_epochs = SEARCH_SPACE_UNION_FIELD
    number_of_workers = SEARCH_SPACE_UNION_FIELD
    optimizer = SEARCH_SPACE_UNION_FIELD
    random_seed = SEARCH_SPACE_UNION_FIELD
    step_lr_gamma = SEARCH_SPACE_UNION_FIELD
    step_lr_step_size = SEARCH_SPACE_UNION_FIELD
    training_batch_size = SEARCH_SPACE_UNION_FIELD
    validation_batch_size = SEARCH_SPACE_UNION_FIELD
    warmup_cosine_lr_cycles = SEARCH_SPACE_UNION_FIELD
    warmup_cosine_lr_warmup_epochs = SEARCH_SPACE_UNION_FIELD
    weight_decay = SEARCH_SPACE_UNION_FIELD


class ImageModelDistributionSettingsClassificationSchema(ImageModelDistributionSettingsSchema):
    training_crop_size = SEARCH_SPACE_UNION_FIELD
    validation_crop_size = SEARCH_SPACE_UNION_FIELD
    validation_resize_size = SEARCH_SPACE_UNION_FIELD
    weighted_loss = SEARCH_SPACE_UNION_FIELD

    @post_dump
    def conversion(self, data, **kwargs):
        if self.context.get("inside_pipeline", False):
            # AutoML job inside pipeline does load(dump) instead of calling to_rest_object explicitly for creating the autoRest Object from sdk job.
            # Hence for pipeline job, we explicitly convert Sweep Distribution dict to str after dump in this method.
            # For standalone automl job, same conversion happens in image_classification_job._to_rest_object()
            from azure.ai.ml.entities._job.automl.image.image_search_space_utils import _convert_sweep_dist_dict_to_str

            for k, sweep_dist_dict in data.items():
                if sweep_dist_dict is not None:
                    data[k] = _convert_sweep_dist_dict_to_str(sweep_dist_dict)
        return data

    @pre_load
    def before_make(self, data, **kwargs):
        if self.context.get("inside_pipeline", False):
            from azure.ai.ml.entities._job.automl.image.image_search_space_utils import _convert_sweep_dist_str_to_dict

            # Converting Sweep Distribution str to Sweep Distribution dict for complying with search_space schema.
            for k, val in data.items():
                if isinstance(val, str):
                    data[k] = _convert_sweep_dist_str_to_dict(val)
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import ImageClassificationSearchSpace

        return ImageClassificationSearchSpace(**data)


class ImageModelDistributionSettingsObjectDetectionSchema(ImageModelDistributionSettingsSchema):
    box_detections_per_image = SEARCH_SPACE_UNION_FIELD
    box_score_threshold = SEARCH_SPACE_UNION_FIELD
    image_size = SEARCH_SPACE_UNION_FIELD
    max_size = SEARCH_SPACE_UNION_FIELD
    min_size = SEARCH_SPACE_UNION_FIELD
    model_size = SEARCH_SPACE_UNION_FIELD
    multi_scale = SEARCH_SPACE_UNION_FIELD
    nms_iou_threshold = SEARCH_SPACE_UNION_FIELD
    tile_grid_size = SEARCH_SPACE_UNION_FIELD
    tile_overlap_ratio = SEARCH_SPACE_UNION_FIELD
    tile_predictions_nms_threshold = SEARCH_SPACE_UNION_FIELD
    validation_iou_threshold = SEARCH_SPACE_UNION_FIELD
    validation_metric_type = SEARCH_SPACE_UNION_FIELD

    @post_dump
    def conversion(self, data, **kwargs):
        if self.context.get("inside_pipeline", False):
            # AutoML job inside pipeline does load(dump) instead of calling to_rest_object explicitly for creating the autoRest Object
            # from sdk job object.
            # Hence for pipeline job, we explicitly convert Sweep Distribution dict to str after dump in this method.
            # For standalone automl job, same conversion happens in image_object_detection_job._to_rest_object()
            from azure.ai.ml.entities._job.automl.image.image_search_space_utils import _convert_sweep_dist_dict_to_str

            for k, sweep_dist_dict in data.items():
                if sweep_dist_dict is not None:
                    data[k] = _convert_sweep_dist_dict_to_str(sweep_dist_dict)
        return data

    @pre_load
    def before_make(self, data, **kwargs):
        if self.context.get("inside_pipeline", False):
            from azure.ai.ml.entities._job.automl.image.image_search_space_utils import _convert_sweep_dist_str_to_dict

            # Converting Sweep Distribution str to Sweep Distribution dict for complying with search_space schema.
            for k, val in data.items():
                if isinstance(val, str):
                    data[k] = _convert_sweep_dist_str_to_dict(val)
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import ImageObjectDetectionSearchSpace

        return ImageObjectDetectionSearchSpace(**data)
