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
    ValidationInitiated = 0
    ValidationSuccess = 1
    ValidationFailed = 2
    ValidationCheckTimeout = 3


class TestRunStatus(Enum):
    Accepted = 0,
    NotStarted = 1,
    Provisioning = 2,
    Provisioned = 3,
    Configuring = 4,
    Configured = 5,
    Executing = 6,
    Executed = 7,
    Deprovisioning = 8,
    Deprovisioned = 9,
    Done = 10,
    Cancelling = 11,
    Cancelled = 12,
    Failed = 13,
    ValidationSuccess = 14,
    ValidationFailed = 15
    CheckTimeout = 16


__all__: List[str] = ["TestFileValidationStatus", "TestRunStatus"]  # Add all objects you want publicly available to users at this
# package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
