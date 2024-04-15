# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from enum import Enum
from typing import List

from ._enums import FaceAttributeType

FaceAttributeTypeDetection01 = Enum("FaceAttributeTypeDetection01", [
    (a.name, a.value) for a in FaceAttributeType if a in [
        FaceAttributeType.ACCESSORIES,
        FaceAttributeType.BLUR,
        FaceAttributeType.EXPOSURE,
        FaceAttributeType.GLASSES,
        FaceAttributeType.HEAD_POSE,
        FaceAttributeType.NOISE,
        FaceAttributeType.OCCLUSION]])
"""Available attribute options for detection_01 model."""

FaceAttributeTypeDetection03 = Enum("FaceAttributeTypeDetection03", [
    (a.name, a.value) for a in FaceAttributeType if a in [
        FaceAttributeType.HEAD_POSE,
        FaceAttributeType.MASK]])
"""Available attribute options for detection_03 model."""

FaceAttributeTypeRecognition03 = Enum("FaceAttributeTypeRecognition03", [
    (a.name, a.value) for a in FaceAttributeType if a in [
        FaceAttributeType.QUALITY_FOR_RECOGNITION]])
"""Available attribute options for recognition_03 model."""

FaceAttributeTypeRecognition04 = Enum("FaceAttributeTypeRecognition04", [
    (a.name, a.value) for a in FaceAttributeType if a in [
        FaceAttributeType.QUALITY_FOR_RECOGNITION]])
"""Available attribute options for recognition_04 model."""


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
