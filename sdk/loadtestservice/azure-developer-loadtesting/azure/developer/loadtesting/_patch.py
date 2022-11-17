# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from enum import Enum


class TestFileValidationStatus(Enum):
    ValidationInitiated = 10
    ValidationSuccess = 20
    ValidationFailed = 30
    ValidationCheckTimeout = 40


class TestRunStatus(Enum):
    Accepted = 10
    NotStarted = 20
    Provisioning = 30
    Provisioned = 40
    Configuring = 50
    Configured = 60
    Executing = 70
    Executed = 80
    Deprovisioning = 90
    Deprovisioned = 100
    Done = 110
    Cancelling = 120
    Cancelled = 130
    Failed = 140
    ValidationSuccess = 150
    ValidationFailed = 160
    CheckTimeout = 170


__all__: List[str] = [
    "TestFileValidationStatus",
    "TestRunStatus",
]  # Add all objects you want publicly available to users at this
# package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
