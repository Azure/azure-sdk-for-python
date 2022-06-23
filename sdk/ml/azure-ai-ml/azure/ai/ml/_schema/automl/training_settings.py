# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load
from azure.ai.ml.constants import AutoMLConstants
from azure.ai.ml._schema import PatchedSchemaMeta, NestedField, StringTransformedEnum
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._job.automl.training_settings import (
    ClassificationTrainingSettings,
    ForecastingTrainingSettings,
    RegressionTrainingSettings,
)
from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ClassificationModels,
    ForecastingModels,
    RegressionModels,
    StackEnsembleSettings,
    StackMetaLearnerType,
)


class StackEnsembleSettingsSchema(metaclass=PatchedSchemaMeta):
    stack_meta_learner_kwargs = fields.Dict()
    stack_meta_learner_train_percentage = fields.Float()
    stack_meta_learner_type = StringTransformedEnum(
        allowed_values=[o.value for o in StackMetaLearnerType], casing_transform=camel_to_snake
    )

    @post_load
    def make(self, data, **kwargs):
        # Converting it here, as there is no corresponding entity class
        stack_meta_learner_type = data.pop("stack_meta_learner_type")
        stack_meta_learner_type = StackMetaLearnerType[stack_meta_learner_type.upper()]
        return StackEnsembleSettings(stack_meta_learner_type=stack_meta_learner_type, **data)


class TrainingSettingsSchema(metaclass=PatchedSchemaMeta):
    enable_dnn_training = fields.Bool()
    enable_model_explainability = fields.Bool()
    enable_onnx_compatible_models = fields.Bool()
    enable_stack_ensemble = fields.Bool()
    enable_vote_ensemble = fields.Bool()
    ensemble_model_download_timeout = fields.Int(data_key=AutoMLConstants.ENSEMBLE_MODEL_DOWNLOAD_TIMEOUT_YAML)
    stack_ensemble_settings = NestedField(StackEnsembleSettingsSchema())


class ClassificationTrainingSettingsSchema(TrainingSettingsSchema):
    allowed_training_algorithms = fields.List(
        StringTransformedEnum(
            allowed_values=[o.value for o in ClassificationModels],
            casing_transform=camel_to_snake,
        ),
        data_key=AutoMLConstants.ALLOWED_ALGORITHMS_YAML,
    )
    blocked_training_algorithms = fields.List(
        StringTransformedEnum(
            allowed_values=[o.value for o in ClassificationModels],
            casing_transform=camel_to_snake,
        ),
        data_key=AutoMLConstants.BLOCKED_ALGORITHMS_YAML,
    )

    @post_load
    def make(self, data, **kwargs) -> "ClassificationTrainingSettings":
        return ClassificationTrainingSettings(**data)


class ForecastingTrainingSettingsSchema(TrainingSettingsSchema):
    allowed_training_algorithms = fields.List(
        StringTransformedEnum(
            allowed_values=[o.value for o in ForecastingModels],
            casing_transform=camel_to_snake,
        ),
        data_key=AutoMLConstants.ALLOWED_ALGORITHMS_YAML,
    )
    blocked_training_algorithms = fields.List(
        StringTransformedEnum(
            allowed_values=[o.value for o in ForecastingModels],
            casing_transform=camel_to_snake,
        ),
        data_key=AutoMLConstants.BLOCKED_ALGORITHMS_YAML,
    )

    @post_load
    def make(self, data, **kwargs) -> "ForecastingTrainingSettings":
        return ForecastingTrainingSettings(**data)


class RegressionTrainingSettingsSchema(TrainingSettingsSchema):
    allowed_training_algorithms = fields.List(
        StringTransformedEnum(
            allowed_values=[o.value for o in RegressionModels],
            casing_transform=camel_to_snake,
        ),
        data_key=AutoMLConstants.ALLOWED_ALGORITHMS_YAML,
    )
    blocked_training_algorithms = fields.List(
        StringTransformedEnum(
            allowed_values=[o.value for o in RegressionModels],
            casing_transform=camel_to_snake,
        ),
        data_key=AutoMLConstants.BLOCKED_ALGORITHMS_YAML,
    )

    @post_load
    def make(self, data, **kwargs) -> "RegressionTrainingSettings":
        return RegressionTrainingSettings(**data)
