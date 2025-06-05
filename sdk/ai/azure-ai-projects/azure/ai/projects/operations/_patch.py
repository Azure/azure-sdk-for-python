# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._patch_datasets import DatasetsOperations
from ._patch_inference import InferenceOperations
from ._patch_telemetry import TelemetryOperations
from ._patch_connections import ConnectionsOperations

__all__: List[str] = [
    "InferenceOperations",
    "TelemetryOperations",
    "DatasetsOperations",
    "ConnectionsOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
