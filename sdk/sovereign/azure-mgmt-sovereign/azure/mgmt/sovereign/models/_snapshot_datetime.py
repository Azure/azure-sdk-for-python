# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Preserve snapshot identifiers with greater than microsecond precision."""

from datetime import datetime, tzinfo
import re
from typing import Any, Optional, Union

from .._utils.model_base import _deserialize_datetime


class _SnapshotDatetime(datetime):
    _extra_fraction: str

    @classmethod
    def _from_datetime(cls, value: datetime, extra_fraction: str) -> "_SnapshotDatetime":
        result = cls(
            value.year, value.month, value.day, value.hour, value.minute,
            value.second, value.microsecond, value.tzinfo, fold=value.fold,
        )
        result._extra_fraction = extra_fraction
        return result

    def isoformat(self, sep: str = "T", timespec: str = "auto") -> str:
        result = super().isoformat(sep, timespec)
        fraction = getattr(self, "_extra_fraction", "")
        if fraction and timespec == "auto":
            result = super().isoformat(sep, "microseconds")
            return result[:26] + fraction + result[26:]
        return result

    def astimezone(self, tz: Optional[tzinfo] = None) -> "_SnapshotDatetime":
        return self._from_datetime(super().astimezone(tz), getattr(self, "_extra_fraction", ""))

    def replace(self, *args: Any, **kwargs: Any) -> "_SnapshotDatetime":
        fraction = "" if len(args) > 6 or "microsecond" in kwargs else getattr(self, "_extra_fraction", "")
        return self._from_datetime(super().replace(*args, **kwargs), fraction)

    def __reduce_ex__(self, protocol: int):
        constructor, args = super().__reduce_ex__(protocol)
        return constructor, args, self.__dict__


def _deserialize_snapshot_datetime(value: Union[str, datetime]) -> datetime:
    parsed = _deserialize_datetime(value)
    if isinstance(value, str):
        fraction = re.search(r"\.(\d{7,})(?:Z|[+-]\d{2}:?\d{2})?$", value, re.IGNORECASE)
        if fraction:
            return _SnapshotDatetime._from_datetime(parsed, fraction.group(1)[6:])
    return parsed
