# mypy: disable_error_code=misc
# pyright: reportGeneralTypeIssues=false
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from enum import Enum
from typing import List

from azure.core import CaseInsensitiveEnumMeta

from ._enums import FaceAttributeType


class FaceAttributeTypeDetection01(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Available attribute options for detection_01 model."""

    ACCESSORIES = FaceAttributeType.ACCESSORIES.value
    BLUR = FaceAttributeType.BLUR.value
    EXPOSURE = FaceAttributeType.EXPOSURE.value
    GLASSES = FaceAttributeType.GLASSES.value
    HEAD_POSE = FaceAttributeType.HEAD_POSE.value
    NOISE = FaceAttributeType.NOISE.value
    OCCLUSION = FaceAttributeType.OCCLUSION.value


class FaceAttributeTypeDetection03(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Available attribute options for detection_03 model."""

    BLUR = FaceAttributeType.BLUR.value
    HEAD_POSE = FaceAttributeType.HEAD_POSE.value
    MASK = FaceAttributeType.MASK.value


class FaceAttributeTypeRecognition03(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Available attribute options for recognition_03 model."""

    QUALITY_FOR_RECOGNITION = FaceAttributeType.QUALITY_FOR_RECOGNITION.value


class FaceAttributeTypeRecognition04(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Available attribute options for recognition_04 model."""

    QUALITY_FOR_RECOGNITION = FaceAttributeType.QUALITY_FOR_RECOGNITION.value


__all__: List[str] = [
    "FaceAttributeTypeDetection01",
    "FaceAttributeTypeDetection03",
    "FaceAttributeTypeRecognition03",
    "FaceAttributeTypeRecognition04",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
