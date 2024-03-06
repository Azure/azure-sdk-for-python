# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains automated machine learning classes for Azure Machine Learning SDKv2.

Main areas include managing AutoML tasks.
"""
from azure.ai.ml.entities._job.automl import TrainingSettings
from azure.ai.ml.entities._job.automl.image import (
    LogTrainingMetrics,
    LogValidationLoss,
    ImageClassificationJob,
    ImageClassificationMultilabelJob,
    ImageClassificationSearchSpace,
    ImageInstanceSegmentationJob,
    ImageLimitSettings,
    ImageModelSettingsClassification,
    ImageModelSettingsObjectDetection,
    ImageObjectDetectionJob,
    ImageObjectDetectionSearchSpace,
    ImageSweepSettings,
)
from azure.ai.ml.entities._job.automl.nlp import (
    NlpFeaturizationSettings,
    NlpFixedParameters,
    NlpLimitSettings,
    NlpSearchSpace,
    NlpSweepSettings,
    TextClassificationJob,
    TextClassificationMultilabelJob,
    TextNerJob,
)
from azure.ai.ml.entities._job.automl.search_space import SearchSpace
from azure.ai.ml.entities._job.automl.stack_ensemble_settings import (
    StackEnsembleSettings,
)
from azure.ai.ml.entities._job.automl.tabular import (
    ClassificationJob,
    ColumnTransformer,
    ForecastingJob,
    ForecastingSettings,
    RegressionJob,
    TabularFeaturizationSettings,
    TabularLimitSettings,
)

from .._restclient.v2023_04_01_preview.models import (
    BlockedTransformers,
    ClassificationModels,
    ClassificationMultilabelPrimaryMetrics,
    ClassificationPrimaryMetrics,
    FeaturizationMode,
    ForecastHorizonMode,
    ForecastingModels,
    ForecastingPrimaryMetrics,
    InstanceSegmentationPrimaryMetrics,
    LearningRateScheduler,
    NCrossValidationsMode,
    ObjectDetectionPrimaryMetrics,
    RegressionModels,
    RegressionPrimaryMetrics,
    SamplingAlgorithmType,
    ShortSeriesHandlingConfiguration,
    StochasticOptimizer,
    TargetAggregationFunction,
    TargetLagsMode,
    TargetRollingWindowSizeMode,
    UseStl,
    ValidationMetricType,
)
from ._automl_image import (
    image_classification,
    image_classification_multilabel,
    image_instance_segmentation,
    image_object_detection,
)
from ._automl_nlp import text_classification, text_classification_multilabel, text_ner
from ._automl_tabular import classification, forecasting, regression

__all__ = [
    "ClassificationModels",
    "RegressionModels",
    "ForecastingModels",
    "FeaturizationMode",
    "NCrossValidationsMode",
    "ForecastHorizonMode",
    "ShortSeriesHandlingConfiguration",
    "TargetLagsMode",
    "TargetRollingWindowSizeMode",
    "TargetAggregationFunction",
    "UseStl",
    "ClassificationPrimaryMetrics",
    "RegressionPrimaryMetrics",
    "ForecastingPrimaryMetrics",
    "ClassificationMultilabelPrimaryMetrics",
    "ObjectDetectionPrimaryMetrics",
    "InstanceSegmentationPrimaryMetrics",
    "ColumnTransformer",
    "TabularFeaturizationSettings",
    "ForecastingSettings",
    "TabularLimitSettings",
    "NlpFeaturizationSettings",
    "NlpFixedParameters",
    "NlpLimitSettings",
    "NlpSweepSettings",
    "NlpSearchSpace",
    "LogTrainingMetrics",
    "LogValidationLoss",
    "ImageLimitSettings",
    "ImageModelSettingsClassification",
    "ImageModelSettingsObjectDetection",
    "ImageSweepSettings",
    "ImageObjectDetectionSearchSpace",
    "ImageClassificationSearchSpace",
    "TrainingSettings",
    "image_classification",
    "image_classification_multilabel",
    "image_object_detection",
    "image_instance_segmentation",
    "text_classification",
    "text_classification_multilabel",
    "text_ner",
    "classification",
    "regression",
    "forecasting",
    "SearchSpace",
    "StackEnsembleSettings",
    "BlockedTransformers",
    "ClassificationJob",
    "ForecastingJob",
    "RegressionJob",
    "ImageClassificationJob",
    "ImageClassificationMultilabelJob",
    "ImageObjectDetectionJob",
    "ImageInstanceSegmentationJob",
    "LearningRateScheduler",
    "SamplingAlgorithmType",
    "StochasticOptimizer",
    "TextClassificationJob",
    "TextClassificationMultilabelJob",
    "TextNerJob",
    "ValidationMetricType",
]
