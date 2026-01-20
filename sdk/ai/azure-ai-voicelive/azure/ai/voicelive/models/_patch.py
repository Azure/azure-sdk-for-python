# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any
from ._models import RequestSession as GeneratedRequestSession


class RequestSession(GeneratedRequestSession):
    """Extended RequestSession that tracks explicitly set None values."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Track which kwargs were explicitly passed as None
        self._explicit_none_fields = {k for k, v in kwargs.items() if v is None}
        super().__init__(*args, **kwargs)

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Convert to dict, including explicitly set None values.

        :return: A dictionary representation of the RequestSession, including fields that were
            explicitly set to None.
        :rtype: dict[str, Any]
        """
        result = super().as_dict(**kwargs)
        # Add back any fields that were explicitly set to None
        for field in self._explicit_none_fields:
            # Convert attribute name to rest field name if needed
            rest_name = self._attr_to_rest_field.get(field)
            if rest_name:
                result[rest_name._rest_name] = None  # pylint: disable=protected-access
            else:
                result[field] = None
        return result


__all__: list[str] = ["RequestSession"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
