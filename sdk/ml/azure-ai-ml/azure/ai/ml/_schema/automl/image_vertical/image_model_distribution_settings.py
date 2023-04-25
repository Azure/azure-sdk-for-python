# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use,protected-access

from marshmallow import fields, post_dump, post_load, pre_load

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    LearningRateScheduler,
    ModelSize,
    StochasticOptimizer,
    ValidationMetricType,
)
from azure.ai.ml._schema._sweep.search_space import (
    ChoiceSchema,
    IntegerQNormalSchema,
    IntegerQUniformSchema,
    NormalSchema,
    QNormalSchema,
    QUniformSchema,
    RandintSchema,
    UniformSchema,
)
from azure.ai.ml._schema.core.fields import (
    DumpableIntegerField,
    DumpableStringField,
    NestedField,
    StringTransformedEnum,
    UnionField,
)
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._job.automl import (
    ImageClassificationModelNames,
    ImageInstanceSegmentationModelNames,
    ImageObjectDetectionModelNames,
)


def get_choice_schema_of_type(cls, **kwargs):
    class CustomChoiceSchema(ChoiceSchema):
        values = fields.List(cls(**kwargs))

    return CustomChoiceSchema()


def get_choice_and_single_value_schema_of_type(cls, **kwargs):
    # Reshuffling the order of fields for allowing choice of booleans.
    # The reason is, while dumping [Bool, Choice[Bool]] is parsing even dict as True.
    # Since all unionFields are parsed sequentially, to avoid this, we are giving the "type" field at the end.
    return UnionField([NestedField(get_choice_schema_of_type(cls, **kwargs)), cls(**kwargs)])


FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD = UnionField(
    [
        fields.Float(),
        DumpableIntegerField(strict=True),
        NestedField(get_choice_schema_of_type(DumpableIntegerField, strict=True)),
        NestedField(get_choice_schema_of_type(fields.Float)),
        NestedField(UniformSchema()),
        NestedField(QUniformSchema()),
        NestedField(NormalSchema()),
        NestedField(QNormalSchema()),
        NestedField(RandintSchema()),
    ]
)

INT_SEARCH_SPACE_DISTRIBUTION_FIELD = UnionField(
    [
        DumpableIntegerField(strict=True),
        NestedField(get_choice_schema_of_type(DumpableIntegerField, strict=True)),
        NestedField(RandintSchema()),
        NestedField(IntegerQUniformSchema()),
        NestedField(IntegerQNormalSchema()),
    ]
)

STRING_SEARCH_SPACE_DISTRIBUTION_FIELD = get_choice_and_single_value_schema_of_type(DumpableStringField)
BOOL_SEARCH_SPACE_DISTRIBUTION_FIELD = get_choice_and_single_value_schema_of_type(fields.Bool)

classification_model_name_args = {"allowed_values": [o.value for o in ImageClassificationModelNames]}
detection_model_name_args = {"allowed_values": [o.value for o in ImageObjectDetectionModelNames]}
segmentation_model_name_args = {"allowed_values": [o.value for o in ImageInstanceSegmentationModelNames]}
model_size_enum_args = {"allowed_values": [o.value for o in ModelSize], "casing_transform": camel_to_snake}
learning_rate_scheduler_enum_args = {
    "allowed_values": [o.value for o in LearningRateScheduler],
    "casing_transform": camel_to_snake,
}
optimizer_enum_args = {"allowed_values": [o.value for o in StochasticOptimizer], "casing_transform": camel_to_snake}
validation_metric_enum_args = {
    "allowed_values": [o.value for o in ValidationMetricType],
    "casing_transform": camel_to_snake,
}

CLASSIFICATION_MODEL_NAME_DISTRIBUTION_FIELD = get_choice_and_single_value_schema_of_type(
    StringTransformedEnum, **classification_model_name_args
)
DETECTION_MODEL_NAME_DISTRIBUTION_FIELD = get_choice_and_single_value_schema_of_type(
    StringTransformedEnum, **detection_model_name_args
)
SEGMENTATION_MODEL_NAME_DISTRIBUTION_FIELD = get_choice_and_single_value_schema_of_type(
    StringTransformedEnum, **segmentation_model_name_args
)
MODEL_SIZE_DISTRIBUTION_FIELD = get_choice_and_single_value_schema_of_type(
    StringTransformedEnum, **model_size_enum_args
)
LEARNING_RATE_SCHEDULER_DISTRIBUTION_FIELD = get_choice_and_single_value_schema_of_type(
    StringTransformedEnum, **learning_rate_scheduler_enum_args
)
OPTIMIZER_DISTRIBUTION_FIELD = get_choice_and_single_value_schema_of_type(StringTransformedEnum, **optimizer_enum_args)
VALIDATION_METRIC_DISTRIBUTION_FIELD = get_choice_and_single_value_schema_of_type(
    StringTransformedEnum, **validation_metric_enum_args
)


class ImageModelDistributionSettingsSchema(metaclass=PatchedSchemaMeta):
    ams_gradient = BOOL_SEARCH_SPACE_DISTRIBUTION_FIELD
    augmentations = STRING_SEARCH_SPACE_DISTRIBUTION_FIELD
    beta1 = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    beta2 = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    distributed = BOOL_SEARCH_SPACE_DISTRIBUTION_FIELD
    early_stopping = BOOL_SEARCH_SPACE_DISTRIBUTION_FIELD
    early_stopping_delay = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    early_stopping_patience = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    evaluation_frequency = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    enable_onnx_normalization = BOOL_SEARCH_SPACE_DISTRIBUTION_FIELD
    gradient_accumulation_step = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    layers_to_freeze = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    learning_rate = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    learning_rate_scheduler = LEARNING_RATE_SCHEDULER_DISTRIBUTION_FIELD
    momentum = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    nesterov = BOOL_SEARCH_SPACE_DISTRIBUTION_FIELD
    number_of_epochs = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    number_of_workers = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    optimizer = OPTIMIZER_DISTRIBUTION_FIELD
    random_seed = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    step_lr_gamma = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    step_lr_step_size = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    training_batch_size = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    validation_batch_size = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    warmup_cosine_lr_cycles = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    warmup_cosine_lr_warmup_epochs = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    weight_decay = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD


class ImageModelDistributionSettingsClassificationSchema(ImageModelDistributionSettingsSchema):
    model_name = CLASSIFICATION_MODEL_NAME_DISTRIBUTION_FIELD
    training_crop_size = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    validation_crop_size = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    validation_resize_size = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    weighted_loss = INT_SEARCH_SPACE_DISTRIBUTION_FIELD

    @post_dump
    def conversion(self, data, **kwargs):
        if self.context.get("inside_pipeline", False):  # pylint: disable=no-member
            # AutoML job inside pipeline does load(dump) instead of calling to_rest_object
            # explicitly for creating the autoRest Object from sdk job.
            # Hence for pipeline job, we explicitly convert Sweep Distribution dict to str after dump in this method.
            # For standalone automl job, same conversion happens in image_classification_job._to_rest_object()
            from azure.ai.ml.entities._job.automl.search_space_utils import _convert_sweep_dist_dict_to_str_dict

            data = _convert_sweep_dist_dict_to_str_dict(data)
        return data

    @pre_load
    def before_make(self, data, **kwargs):
        if self.context.get("inside_pipeline", False):  # pylint: disable=no-member
            from azure.ai.ml.entities._job.automl.search_space_utils import _convert_sweep_dist_str_to_dict

            # Converting Sweep Distribution str to Sweep Distribution dict for complying with search_space schema.
            data = _convert_sweep_dist_str_to_dict(data)
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import ImageClassificationSearchSpace

        return ImageClassificationSearchSpace(**data)


class ImageModelDistributionSettingsDetectionCommonSchema(ImageModelDistributionSettingsSchema):
    box_detections_per_image = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    box_score_threshold = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    image_size = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    max_size = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    min_size = INT_SEARCH_SPACE_DISTRIBUTION_FIELD
    model_size = MODEL_SIZE_DISTRIBUTION_FIELD
    multi_scale = BOOL_SEARCH_SPACE_DISTRIBUTION_FIELD
    nms_iou_threshold = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    tile_grid_size = STRING_SEARCH_SPACE_DISTRIBUTION_FIELD
    tile_overlap_ratio = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    tile_predictions_nms_threshold = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    validation_iou_threshold = FLOAT_SEARCH_SPACE_DISTRIBUTION_FIELD
    validation_metric_type = VALIDATION_METRIC_DISTRIBUTION_FIELD

    @post_dump
    def conversion(self, data, **kwargs):
        if self.context.get("inside_pipeline", False):  # pylint: disable=no-member
            # AutoML job inside pipeline does load(dump) instead of calling to_rest_object
            # explicitly for creating the autoRest Object from sdk job object.
            # Hence for pipeline job, we explicitly convert Sweep Distribution dict to str after dump in this method.
            # For standalone automl job, same conversion happens in image_object_detection_job._to_rest_object()
            from azure.ai.ml.entities._job.automl.search_space_utils import _convert_sweep_dist_dict_to_str_dict

            data = _convert_sweep_dist_dict_to_str_dict(data)
        return data

    @pre_load
    def before_make(self, data, **kwargs):
        if self.context.get("inside_pipeline", False):  # pylint: disable=no-member
            from azure.ai.ml.entities._job.automl.search_space_utils import _convert_sweep_dist_str_to_dict

            # Converting Sweep Distribution str to Sweep Distribution dict for complying with search_space schema.
            data = _convert_sweep_dist_str_to_dict(data)
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.automl import ImageObjectDetectionSearchSpace

        return ImageObjectDetectionSearchSpace(**data)


class ImageModelDistributionSettingsObjectDetectionSchema(ImageModelDistributionSettingsDetectionCommonSchema):
    model_name = DETECTION_MODEL_NAME_DISTRIBUTION_FIELD


class ImageModelDistributionSettingsInstanceSegmentationSchema(ImageModelDistributionSettingsObjectDetectionSchema):
    model_name = SEGMENTATION_MODEL_NAME_DISTRIBUTION_FIELD
