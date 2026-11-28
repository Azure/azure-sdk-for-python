# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from functools import wraps
from typing import Any, IO, Union

from azure.core.polling import AsyncLROPoller

from ... import models, types
from ..._remediation import _normalize_remediation_result
from ._operations import SovereignViewOperationsOperations as _GeneratedOperations

__all__ = ["SovereignViewOperationsOperations"]


class SovereignViewOperationsOperations(_GeneratedOperations):
    @wraps(_GeneratedOperations.begin_remediate)
    async def begin_remediate(
        self,
        resource_group_name: str,
        sovereign_view_name: str,
        body: Union[models.SovereignViewRemediateContent, types.SovereignViewRemediateContent, IO[bytes]],
        **kwargs: Any
    ) -> AsyncLROPoller[models.SovereignViewRemediateResult]:
        cls = kwargs.pop("cls", None)

        def deserialize(response, result, headers):
            result = _normalize_remediation_result(result)
            return cls(response, result, headers) if cls else result

        return await super().begin_remediate(
            resource_group_name, sovereign_view_name, body, cls=deserialize, **kwargs
        )


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
