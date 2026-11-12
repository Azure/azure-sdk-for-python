# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from datetime import datetime
from typing import Optional

from .._utils.model_base import rest_field
from . import _models
from ._snapshot_datetime import _deserialize_snapshot_datetime

__all__ = [
    "SovereignViewComplianceDetail",
    "SovereignViewComplianceResourceDetailsContent",
    "SovereignViewComplianceResourceDetailsResult",
    "SovereignViewDimensionDetail",
]


def _snapshot_field():
    return rest_field(
        name="evaluatedAt", visibility=["read", "create", "update", "delete", "query"],
        format="rfc3339", deserializer=_deserialize_snapshot_datetime,
    )


class SovereignViewComplianceDetail(_models.SovereignViewComplianceDetail):
    """A compliance detail preserving the complete evaluation timestamp."""

    evaluated_at: Optional[datetime] = _snapshot_field()


class SovereignViewComplianceResourceDetailsContent(_models.SovereignViewComplianceResourceDetailsContent):
    """A resource-details request preserving the selected snapshot timestamp."""

    evaluated_at: Optional[datetime] = _snapshot_field()


class SovereignViewComplianceResourceDetailsResult(_models.SovereignViewComplianceResourceDetailsResult):
    """Resource details preserving the complete snapshot timestamp."""

    evaluated_at: datetime = _snapshot_field()


class SovereignViewDimensionDetail(_models.SovereignViewDimensionDetail):
    """A compliance dimension preserving the complete snapshot timestamp."""

    evaluated_at: datetime = _snapshot_field()


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
