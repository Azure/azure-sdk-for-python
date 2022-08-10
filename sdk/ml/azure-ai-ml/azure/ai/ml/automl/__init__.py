# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml.entities._job.automl.image import (
    ImageClassificationSearchSpace,
    ImageLimitSettings,
    ImageObjectDetectionSearchSpace,
    ImageSweepSettings,
)
from azure.ai.ml.entities._job.automl.nlp import NlpFeaturizationSettings, NlpLimitSettings
from azure.ai.ml.entities._job.automl.tabular.featurization_settings import (
    ColumnTransformer,
    TabularFeaturizationSettings,
)
from azure.ai.ml.entities._job.automl.tabular.forecasting_settings import ForecastingSettings
from azure.ai.ml.entities._job.automl.tabular.limit_settings import TabularLimitSettings

from .._restclient.v2022_02_01_preview.models import (
    ClassificationModels,
    ClassificationMultilabelPrimaryMetrics,
    ClassificationPrimaryMetrics,
    FeaturizationMode,
    ForecastHorizonMode,
    ForecastingModels,
    ForecastingPrimaryMetrics,
    InstanceSegmentationPrimaryMetrics,
    NCrossValidationsMode,
    ObjectDetectionPrimaryMetrics,
    RegressionModels,
    RegressionPrimaryMetrics,
    ShortSeriesHandlingConfiguration,
    TargetAggregationFunction,
    TargetLagsMode,
    TargetRollingWindowSizeMode,
    UseStl,
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
    "NlpLimitSettings",
    "ImageLimitSettings",
    "ImageSweepSettings",
    "ImageObjectDetectionSearchSpace",
    "ImageClassificationSearchSpace",
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
]
