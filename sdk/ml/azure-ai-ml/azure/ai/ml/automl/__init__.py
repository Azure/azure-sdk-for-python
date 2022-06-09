# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._automl_image import (
    image_classification,
    image_classification_multilabel,
    image_object_detection,
    image_instance_segmentation,
)
from ._automl_nlp import text_classification, text_classification_multilabel, text_ner
from ._automl_tabular import classification, regression, forecasting

from .._restclient.v2022_02_01_preview.models import (
    ClassificationModels,
    RegressionModels,
    ForecastingModels,
    FeaturizationMode,
    NCrossValidationsMode,
    ForecastHorizonMode,
    ShortSeriesHandlingConfiguration,
    TargetLagsMode,
    TargetRollingWindowSizeMode,
    TargetAggregationFunction,
    UseStl,
    ClassificationPrimaryMetrics,
    RegressionPrimaryMetrics,
    ForecastingPrimaryMetrics,
    ClassificationMultilabelPrimaryMetrics,
    ObjectDetectionPrimaryMetrics,
    InstanceSegmentationPrimaryMetrics,
)

from azure.ai.ml.entities._job.automl.tabular.featurization_settings import (
    ColumnTransformer,
    TabularFeaturizationSettings,
)
from azure.ai.ml.entities._job.automl.tabular.forecasting_settings import ForecastingSettings
from azure.ai.ml.entities._job.automl.tabular.limit_settings import TabularLimitSettings
from azure.ai.ml.entities._job.automl.nlp import NlpFeaturizationSettings, NlpLimitSettings
from azure.ai.ml.entities._job.automl.image import (
    ImageLimitSettings,
    ImageSweepSettings,
    ImageObjectDetectionSearchSpace,
    ImageClassificationSearchSpace,
)

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
