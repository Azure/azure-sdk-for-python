# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

# pylint: disable=unused-import
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    NlpLearningRateScheduler,
    TrainingMode,
)
from azure.ai.ml._utils._experimental import experimental


class AutoMLConstants:
    # The following are fields found in the yaml for AutoML Job
    GENERAL_YAML = "general"
    DATA_YAML = "data"
    FEATURIZATION_YAML = "featurization"
    LIMITS_YAML = "limits"
    SWEEP_YAML = "sweep"
    FORECASTING_YAML = "forecasting"
    TRAINING_YAML = "training"
    MAX_TRIALS_YAML = "max_trials"
    VALIDATION_DATASET_SIZE_YAML = "validation_dataset_size"
    TRAINING_DATA_SETTINGS_YAML = "training"
    TEST_DATA_SETTINGS_YAML = "test"
    VALIDATION_DATA_SETTINGS_YAML = "validation"
    COUNTRY_OR_REGION_YAML = "country_or_region_for_holidays"
    TASK_TYPE_YAML = "task"
    TIMEOUT_YAML = "timeout_minutes"
    TRIAL_TIMEOUT_YAML = "trial_timeout_minutes"
    BLOCKED_ALGORITHMS_YAML = "blocked_training_algorithms"
    ALLOWED_ALGORITHMS_YAML = "allowed_training_algorithms"
    ENSEMBLE_MODEL_DOWNLOAD_TIMEOUT_YAML = "ensemble_model_download_timeout_minutes"
    TERMINATION_POLICY_TYPE_YAML = "type"

    # TASK TYPES
    CLASSIFICATION_YAML = "classification"
    REGRESSION_YAML = "regression"
    FORECASTING_YAML = "forecasting"

    # The following are general purpose AutoML fields
    TARGET_LAGS = "target_lags"
    AUTO = "auto"
    OFF = "off"
    CUSTOM = "custom"
    TIME_SERIES_ID_COLUMN_NAMES = "time_series_id_column_names"
    TRANSFORMER_PARAMS = "transformer_params"
    MODE = "mode"


class AutoMLTransformerParameterKeys(Enum):
    IMPUTER = "Imputer"
    TF_IDF = "TfIdf"
    HASH_ONE_HOT_ENCODER = "HashOneHotEncoder"


class ImageClassificationModelNames(Enum):
    """Model names that are supported for Image Classification tasks."""

    MOBILENETV2 = "mobilenetv2"
    RESNET18 = "resnet18"
    RESNET34 = "resnet34"
    RESNET50 = "resnet50"
    RESNET101 = "resnet101"
    RESNET152 = "resnet152"
    RESNEST50 = "resnest50"
    RESNEST101 = "resnest101"
    SERESNEXT = "seresnext"
    VITS16R224 = "vits16r224"
    VITB16R224 = "vitb16r224"
    VITL16R224 = "vitl16r224"


class ImageObjectDetectionModelNames(Enum):
    """Model names that are supported for Image Object Detection tasks."""

    YOLOV5 = "yolov5"
    FASTERRCNN_RESNET18_FPN = "fasterrcnn_resnet18_fpn"
    FASTERRCNN_RESNET34_FPN = "fasterrcnn_resnet34_fpn"
    FASTERRCNN_RESNET50_FPN = "fasterrcnn_resnet50_fpn"
    FASTERRCNN_RESNET101_FPN = "fasterrcnn_resnet101_fpn"
    FASTERRCNN_RESNET152_FPN = "fasterrcnn_resnet152_fpn"
    RETINANET_RESNET50_FPN = "retinanet_resnet50_fpn"


class ImageInstanceSegmentationModelNames(Enum):
    """Model names that are supported for Image Instance Segmentation tasks."""

    MASKRCNN_RESNET18_FPN = "maskrcnn_resnet18_fpn"
    MASKRCNN_RESNET34_FPN = "maskrcnn_resnet34_fpn"
    MASKRCNN_RESNET50_FPN = "maskrcnn_resnet50_fpn"
    MASKRCNN_RESNET101_FPN = "maskrcnn_resnet101_fpn"
    MASKRCNN_RESNET152_FPN = "maskrcnn_resnet152_fpn"


class NlpModels(Enum):
    # Model names for NLP tasks.
    BERT_BASE_CASED = "bert-base-cased"
    BERT_BASE_UNCASED = "bert-base-uncased"
    BERT_BASE_MULTILINGUAL_CASED = "bert-base-multilingual-cased"
    BERT_BASE_GERMAN_CASED = "bert-base-german-cased"
    BERT_LARGE_CASED = "bert-large-cased"
    BERT_LARGE_UNCASED = "bert-large-uncased"
    DISTILBERT_BASE_CASED = "distilbert-base-cased"
    DISTILBERT_BASE_UNCASED = "distilbert-base-uncased"
    ROBERTA_BASE = "roberta-base"
    ROBERTA_LARGE = "roberta-large"
    DISTILROBERTA_BASE = "distilroberta-base"
    XLM_ROBERTA_BASE = "xlm-roberta-base"
    XLM_ROBERTA_LARGE = "xlm-roberta-large"
    XLNET_BASE_CASED = "xlnet-base-cased"
    XLNET_LARGE_CASED = "xlnet-large-cased"


TrainingMode.__doc__ = "Mode to enable/disable distributed training."
TabularTrainingMode = experimental(TrainingMode)
TabularTrainingMode.__name__ = "TabularTrainingMode"
