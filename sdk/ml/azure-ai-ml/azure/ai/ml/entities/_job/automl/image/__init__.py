# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from .automl_image import AutoMLImage
from .image_classification_job import ImageClassificationJob
from .image_classification_multilabel_job import ImageClassificationMultilabelJob
from .image_classification_search_space import ImageClassificationSearchSpace
from .image_instance_segmentation_job import ImageInstanceSegmentationJob
from .image_limit_settings import ImageLimitSettings
from .image_object_detection_job import ImageObjectDetectionJob
from .image_object_detection_search_space import ImageObjectDetectionSearchSpace
from .image_sweep_settings import ImageSweepSettings
from .image_model_settings import ImageModelSettingsClassification, ImageModelSettingsObjectDetection

__all__ = [
    "AutoMLImage",
    "ImageClassificationJob",
    "ImageClassificationMultilabelJob",
    "ImageClassificationSearchSpace",
    "ImageInstanceSegmentationJob",
    "ImageLimitSettings",
    "ImageObjectDetectionJob",
    "ImageObjectDetectionSearchSpace",
    "ImageSweepSettings",
    "ImageModelSettingsClassification",
    "ImageModelSettingsObjectDetection"
]
